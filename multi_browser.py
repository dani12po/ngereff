import asyncio
from agent import AutomationAgent
from logger import logger
import config
import psutil
import os
import glob
import time

# Track stuck browsers
stuck_browser_count = {}

# Track active browser processes launched by bot
bot_browser_pids = set()

# Track proxy usage index for round-robin
proxy_index = 0

def cleanup_old_logs(max_age_hours: int = 24):
    """Clean up old log files older than max_age_hours."""
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for log_file in glob.glob(f"{log_dir}/*.log"):
            try:
                file_age = current_time - os.path.getmtime(log_file)
                if file_age > max_age_seconds:
                    os.remove(log_file)
                    deleted_count += 1
            except Exception as e:
                logger.debug(f"Error deleting log {log_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old log files")
    except Exception as e:
        logger.debug(f"Error cleaning up logs: {e}")

def kill_bot_chrome_processes():
    """Force kill only Chrome/Chromium processes launched by this bot."""
    killed_count = 0
    try:
        for pid in list(bot_browser_pids):
            try:
                proc = psutil.Process(pid)
                proc.kill()
                killed_count += 1
                logger.debug(f"Killed bot Chrome process: {pid}")
                bot_browser_pids.remove(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                bot_browser_pids.discard(pid)
    except Exception as e:
        logger.error(f"Error killing bot Chrome processes: {e}")
    
    # Clear all tracked PIDs after killing
    bot_browser_pids.clear()
    
    if killed_count > 0:
        logger.warning(f"Force killed {killed_count} bot Chrome processes")
    return killed_count

def count_bot_chrome_processes():
    """Count active Chrome/Chromium processes launched by bot."""
    count = 0
    for pid in list(bot_browser_pids):
        try:
            proc = psutil.Process(pid)
            if proc.is_running():
                count += 1
            else:
                bot_browser_pids.discard(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            bot_browser_pids.discard(pid)
    return count

def register_browser_process(browser_obj):
    """Register browser process PID to track bot-launched browsers."""
    try:
        # Get browser process and all child processes
        current_pid = os.getpid()
        current_process = psutil.Process(current_pid)
        
        # Find all Chrome child processes
        for child in current_process.children(recursive=True):
            if 'chrome' in child.name().lower() or 'chromium' in child.name().lower():
                bot_browser_pids.add(child.pid)
                logger.debug(f"Registered bot browser PID: {child.pid}")
    except Exception as e:
        logger.debug(f"Error registering browser process: {e}")

async def ensure_max_browsers(max_browsers: int = 5):
    """Ensure no more than max_browsers bot Chrome processes are running."""
    bot_chrome_count = count_bot_chrome_processes()
    
    # Each browser spawns ~6-8 processes, so max_browsers * 10 is safe threshold
    max_processes = max_browsers * 10
    
    if bot_chrome_count > max_processes:
        logger.warning(f"⚠️ Too many bot Chrome processes ({bot_chrome_count}/{max_processes}), cleaning up...")
        kill_bot_chrome_processes()
        await asyncio.sleep(2)
        logger.info("✓ Bot Chrome processes cleaned up")

async def run_browser_instance(browser_id: int, proxy_config: dict) -> bool:
    """Run single browser instance with specific proxy and conditional timeout."""
    global stuck_browser_count
    
    try:
        # Ensure we don't exceed max browsers before starting
        await ensure_max_browsers(config.MAX_CONCURRENT_BROWSERS)
        
        logger.info(f"[Browser {browser_id}] Starting with proxy: {proxy_config.get('server', 'N/A')}")
        
        # Check if this browser has been stuck before
        if browser_id in stuck_browser_count:
            if stuck_browser_count[browser_id] >= 2:
                logger.warning(f"[Browser {browser_id}] ⚠️ Stuck 2x before, skipping this round...")
                # Reset counter and skip
                stuck_browser_count[browser_id] = 0
                return False
        
        # Create agent instance
        agent = AutomationAgent()
        
        # Override proxy for this specific browser BEFORE launching
        original_proxy_list = config.PROXY_LIST
        config.PROXY_LIST = [proxy_config]  # Set only this proxy
        
        # Reinitialize browser controller with new proxy
        from browser_controller import BrowserController
        agent.browser_controller = BrowserController()
        
        # Run the agent WITHOUT timeout (will stop when no more green notifications)
        try:
            # Start the agent run
            agent_task = asyncio.create_task(agent.run())
            
            # Register browser processes after launch
            if agent.browser_controller.browser:
                register_browser_process(agent.browser_controller.browser)
            
            # Wait for agent to complete (no timeout)
            # Agent will stop automatically when:
            # 1. No more green notifications (success case)
            # 2. Rate limited without success (needs referral - will close immediately)
            success = await agent_task
            
            # Reset stuck counter on success
            if browser_id in stuck_browser_count:
                stuck_browser_count[browser_id] = 0
                
        except Exception as e:
            logger.error(f"[Browser {browser_id}] Error during execution: {e}")
            success = False
        
        # Cleanup
        try:
            await asyncio.wait_for(agent.cleanup(), timeout=5)
        except asyncio.TimeoutError:
            logger.error(f"[Browser {browser_id}] Cleanup timeout, force killing bot browsers...")
            kill_bot_chrome_processes()
        
        # Restore original proxy list
        config.PROXY_LIST = original_proxy_list
        
        if success:
            logger.info(f"[Browser {browser_id}] ✓ Completed successfully")
        else:
            logger.warning(f"[Browser {browser_id}] ✗ Failed (needs referral or error)")
            # Increment stuck counter on failure
            if browser_id not in stuck_browser_count:
                stuck_browser_count[browser_id] = 0
            stuck_browser_count[browser_id] += 1
        
        return success
        
    except Exception as e:
        logger.error(f"[Browser {browser_id}] Error: {e}")
        # Increment stuck counter on error
        if browser_id not in stuck_browser_count:
            stuck_browser_count[browser_id] = 0
        stuck_browser_count[browser_id] += 1
        
        return False

async def run_multi_browser(num_browsers: int = None) -> None:
    """Run multiple browser instances one by one, maintaining max 5 successful browsers."""
    global proxy_index
    
    if num_browsers is None:
        num_browsers = config.MAX_CONCURRENT_BROWSERS
    
    # Ensure we have proxies
    if len(config.PROXY_LIST) == 0:
        logger.error("No proxies configured! Please add proxies to config.PROXY_LIST")
        return
    
    # Clean up any leftover bot Chrome processes before starting
    bot_chrome_count = count_bot_chrome_processes()
    if bot_chrome_count > 0:
        logger.warning(f"Found {bot_chrome_count} leftover bot Chrome processes, cleaning up...")
        kill_bot_chrome_processes()
        logger.info("Waiting for cleanup to complete...")
        await asyncio.sleep(3)
    
    logger.info("=" * 60)
    logger.info(f"MULTI-BROWSER MODE: Sequential launch with max {num_browsers} successful browsers")
    logger.info(f"Available proxies: {len(config.PROXY_LIST)}")
    logger.info(f"Strategy:")
    logger.info(f"  - Launch browsers one by one")
    logger.info(f"  - Failed browsers close immediately, launch new one")
    logger.info(f"  - Successful browsers (green) stay open until notifications stop")
    logger.info(f"  - Max {num_browsers} successful browsers running simultaneously")
    logger.info("=" * 60)
    
    # Track active successful browser tasks
    active_browsers = {}  # {browser_id: task}
    browser_counter = 0
    successful_count = 0
    failed_count = 0
    
    while True:
        # Check how many successful browsers are currently running
        # Remove completed tasks
        completed_ids = []
        for browser_id, task in active_browsers.items():
            if task.done():
                completed_ids.append(browser_id)
                try:
                    result = task.result()
                    if result:
                        logger.info(f"[Browser {browser_id}] ✓ Completed successfully")
                        successful_count += 1
                    else:
                        logger.info(f"[Browser {browser_id}] ✗ Failed")
                        failed_count += 1
                except Exception as e:
                    logger.error(f"[Browser {browser_id}] Error: {e}")
                    failed_count += 1
        
        # Remove completed browsers from active list
        for browser_id in completed_ids:
            del active_browsers[browser_id]
        
        # Check if we can launch a new browser
        active_count = len(active_browsers)
        
        if active_count < num_browsers:
            # Launch a new browser
            browser_counter += 1
            
            # Get next proxy using round-robin
            proxy = config.PROXY_LIST[proxy_index % len(config.PROXY_LIST)]
            proxy_index += 1
            
            logger.info("=" * 60)
            logger.info(f"Launching Browser {browser_counter}")
            logger.info(f"Active successful browsers: {active_count}/{num_browsers}")
            logger.info(f"Using proxy: {proxy['username']} ({proxy['server']})")
            logger.info("=" * 60)
            
            # Create task for this browser
            task = asyncio.create_task(run_browser_instance(browser_counter, proxy))
            active_browsers[browser_counter] = task
            
            # Wait a bit before checking again (to see if browser fails quickly)
            await asyncio.sleep(10)
        else:
            # Max browsers reached, wait for one to complete
            logger.info(f"Max {num_browsers} successful browsers running, waiting for one to complete...")
            
            # Wait for any browser to complete
            if active_browsers:
                done, pending = await asyncio.wait(
                    active_browsers.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
            else:
                # No active browsers, continue to launch new one
                await asyncio.sleep(1)
    
    # This loop runs forever, but can be interrupted with Ctrl+C

async def run_multi_browser_loop() -> None:
    """Run multi-browser in continuous loop."""
    iteration = 0
    
    try:
        iteration += 1
        logger.info("=" * 60)
        logger.info(f"MULTI-BROWSER SESSION STARTED")
        logger.info("=" * 60)
        
        # Run multi-browser (infinite loop)
        await run_multi_browser()
        
    except KeyboardInterrupt:
        logger.info("Multi-browser loop interrupted by user")
        # Clean up only bot Chrome processes
        logger.info("Cleaning up all bot browsers...")
        kill_bot_chrome_processes()
    except Exception as e:
        logger.error(f"Multi-browser error: {e}")
        # Clean up only bot processes on error
        logger.info("Cleaning up bot browsers after error...")
        kill_bot_chrome_processes()
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(run_multi_browser_loop())
