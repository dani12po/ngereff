import asyncio
from agent import AutomationAgent
from logger import logger
import config

# Track stuck browsers
stuck_browser_count = {}

async def run_browser_instance(browser_id: int, proxy_config: dict) -> bool:
    """Run single browser instance with specific proxy and timeout."""
    global stuck_browser_count
    
    try:
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
            
            # Force cleanup
            try:
                await asyncio.wait_for(agent.cleanup(), timeout=10)
            except asyncio.TimeoutError:
                logger.error(f"[Browser {browser_id}] Cleanup timeout, force killing...")
                # Force kill all chrome processes
                try:
                    import psutil
                    for proc in psutil.process_iter(['pid', 'name']):
                        if 'chrome' in proc.info['name'].lower() or 'chromium' in proc.info['name'].lower():
                            try:
                                proc.kill()
                                logger.warning(f"Force killed process: {proc.info['pid']}")
                            except:
                                pass
                except Exception as e:
                    logger.error(f"Force kill error: {e}")
            
            success = False
        
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
        return False

async def run_multi_browser(num_browsers: int = None) -> None:
    """Run multiple browser instances concurrently."""
    if num_browsers is None:
        num_browsers = min(config.MAX_CONCURRENT_BROWSERS, len(config.PROXY_LIST))
    
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
            break
        except Exception as e:
            logger.error(f"Multi-browser iteration {iteration} error: {e}")
            logger.info(f"Waiting {config.RESTART_DELAY}s before retry...")
            await asyncio.sleep(config.RESTART_DELAY)

if __name__ == "__main__":
    asyncio.run(run_multi_browser_loop())
