import asyncio
from agent import AutomationAgent
from logger import logger
import config
import psutil

# Track stuck browsers
stuck_browser_count = {}

# Track active browser processes
active_browsers = {}

def kill_all_chrome_processes():
    """Force kill all Chrome/Chromium processes."""
    killed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if 'chrome' in proc_name or 'chromium' in proc_name:
                    proc.kill()
                    killed_count += 1
                    logger.debug(f"Killed Chrome process: {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        logger.error(f"Error killing Chrome processes: {e}")
    
    if killed_count > 0:
        logger.warning(f"Force killed {killed_count} Chrome processes")
    return killed_count

def count_chrome_processes():
    """Count active Chrome/Chromium processes."""
    count = 0
    try:
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if 'chrome' in proc_name or 'chromium' in proc_name:
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        logger.error(f"Error counting Chrome processes: {e}")
    return count

async def ensure_max_browsers(max_browsers: int = 5):
    """Ensure no more than max_browsers Chrome processes are running."""
    chrome_count = count_chrome_processes()
    
    # Each browser spawns ~6-8 processes, so max_browsers * 10 is safe threshold
    max_processes = max_browsers * 10
    
    if chrome_count > max_processes:
        logger.warning(f"⚠️ Too many Chrome processes ({chrome_count}/{max_processes}), cleaning up...")
        kill_all_chrome_processes()
        await asyncio.sleep(2)  # Wait for processes to die
        logger.info("✓ Chrome processes cleaned up")

async def run_browser_instance(browser_id: int, proxy_config: dict) -> bool:
    """Run single browser instance with specific proxy and timeout."""
    global stuck_browser_count, active_browsers
    
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
        active_browsers[browser_id] = agent
        
        # Override proxy for this specific browser BEFORE launching
        original_proxy_list = config.PROXY_LIST
        config.PROXY_LIST = [proxy_config]  # Set only this proxy
        
        # Reinitialize browser controller with new proxy
        from browser_controller import BrowserController
        agent.browser_controller = BrowserController()
        
        # Run the agent with timeout
        try:
            success = await asyncio.wait_for(
                agent.run(), 
                timeout=config.BROWSER_TIMEOUT
            )
            # Reset stuck counter on success
            if browser_id in stuck_browser_count:
                stuck_browser_count[browser_id] = 0
        except asyncio.TimeoutError:
            logger.warning(f"[Browser {browser_id}] ⏱️ Timeout after {config.BROWSER_TIMEOUT}s, forcing close...")
            
            # Increment stuck counter
            if browser_id not in stuck_browser_count:
                stuck_browser_count[browser_id] = 0
            stuck_browser_count[browser_id] += 1
            logger.warning(f"[Browser {browser_id}] Stuck count: {stuck_browser_count[browser_id]}/2")
            
            # Force cleanup with aggressive timeout
            try:
                await asyncio.wait_for(agent.cleanup(), timeout=5)
            except asyncio.TimeoutError:
                logger.error(f"[Browser {browser_id}] Cleanup timeout, force killing...")
                kill_all_chrome_processes()
            
            success = False
        finally:
            # Remove from active browsers
            if browser_id in active_browsers:
                del active_browsers[browser_id]
        
        # Restore original proxy list
        config.PROXY_LIST = original_proxy_list
        
        if success:
            logger.info(f"[Browser {browser_id}] ✓ Completed successfully")
        else:
            logger.warning(f"[Browser {browser_id}] ✗ Failed or timeout")
        
        return success
        
    except Exception as e:
        logger.error(f"[Browser {browser_id}] Error: {e}")
        # Increment stuck counter on error
        if browser_id not in stuck_browser_count:
            stuck_browser_count[browser_id] = 0
        stuck_browser_count[browser_id] += 1
        
        # Remove from active browsers
        if browser_id in active_browsers:
            del active_browsers[browser_id]
        
        return False

async def run_multi_browser(num_browsers: int = None) -> None:
    """Run multiple browser instances concurrently."""
    if num_browsers is None:
        num_browsers = min(config.MAX_CONCURRENT_BROWSERS, len(config.PROXY_LIST))
    
    # Limit to max configured browsers
    num_browsers = min(num_browsers, config.MAX_CONCURRENT_BROWSERS, len(config.PROXY_LIST))
    
    # Clean up any leftover Chrome processes before starting
    chrome_count = count_chrome_processes()
    if chrome_count > 0:
        logger.warning(f"Found {chrome_count} leftover Chrome processes, cleaning up...")
        kill_all_chrome_processes()
        await asyncio.sleep(2)
    
    logger.info("=" * 60)
    logger.info(f"MULTI-BROWSER MODE: Running {num_browsers} browsers")
    logger.info(f"Timeout per browser: {config.BROWSER_TIMEOUT}s ({config.BROWSER_TIMEOUT//60} minutes)")
    logger.info("=" * 60)
    
    # Ensure we have enough proxies
    if len(config.PROXY_LIST) < num_browsers:
        logger.warning(f"Not enough proxies! Have {len(config.PROXY_LIST)}, need {num_browsers}")
        num_browsers = len(config.PROXY_LIST)
    
    # Create tasks for each browser
    tasks = []
    for i in range(num_browsers):
        proxy = config.PROXY_LIST[i]
        task = run_browser_instance(i + 1, proxy)
        tasks.append(task)
    
    # Run all browsers concurrently
    logger.info(f"Launching {num_browsers} browsers concurrently...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Force cleanup after all browsers finish
    logger.info("All browsers finished, cleaning up remaining processes...")
    kill_all_chrome_processes()
    await asyncio.sleep(1)
    
    # Summary
    logger.info("=" * 60)
    logger.info("MULTI-BROWSER SUMMARY")
    logger.info("=" * 60)
    
    success_count = sum(1 for r in results if r is True)
    failed_count = len(results) - success_count
    
    logger.info(f"Total browsers: {len(results)}")
    logger.info(f"✓ Successful: {success_count}")
    logger.info(f"✗ Failed/Timeout: {failed_count}")
    logger.info("=" * 60)

async def run_multi_browser_loop() -> None:
    """Run multi-browser in loop with auto-restart."""
    iteration = 0
    
    while True:
        iteration += 1
        logger.info("=" * 60)
        logger.info(f"MULTI-BROWSER ITERATION {iteration}")
        logger.info("=" * 60)
        
        try:
            await run_multi_browser()
            
            if not config.AUTO_RESTART:
                logger.info("Auto-restart disabled. Stopping.")
                break
            
            logger.info(f"Waiting {config.RESTART_DELAY}s before next iteration...")
            await asyncio.sleep(config.RESTART_DELAY)
            
        except KeyboardInterrupt:
            logger.info("Multi-browser loop interrupted by user")
            # Clean up all Chrome processes
            kill_all_chrome_processes()
            break
        except Exception as e:
            logger.error(f"Multi-browser iteration {iteration} error: {e}")
            # Clean up on error
            kill_all_chrome_processes()
            logger.info(f"Waiting {config.RESTART_DELAY}s before retry...")
            await asyncio.sleep(config.RESTART_DELAY)

if __name__ == "__main__":
    asyncio.run(run_multi_browser_loop())
