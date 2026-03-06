import asyncio
from agent import AutomationAgent
from logger import logger
import config

async def run_browser_instance(browser_id: int, proxy_config: dict) -> bool:
    """Run single browser instance with specific proxy."""
    try:
        logger.info(f"[Browser {browser_id}] Starting with proxy: {proxy_config.get('server', 'N/A')}")
        
        # Create agent instance
        agent = AutomationAgent()
        
        # Override proxy for this specific browser BEFORE launching
        # We need to set it before browser_controller is used
        original_proxy_list = config.PROXY_LIST
        config.PROXY_LIST = [proxy_config]  # Set only this proxy
        
        # Reinitialize browser controller with new proxy
        from browser_controller import BrowserController
        agent.browser_controller = BrowserController()
        
        # Run the agent
        success = await agent.run()
        
        # Restore original proxy list
        config.PROXY_LIST = original_proxy_list
        
        if success:
            logger.info(f"[Browser {browser_id}] ✓ Completed successfully")
        else:
            logger.warning(f"[Browser {browser_id}] ✗ Failed")
        
        return success
        
    except Exception as e:
        logger.error(f"[Browser {browser_id}] Error: {e}")
        return False

async def run_multi_browser(num_browsers: int = None) -> None:
    """Run multiple browser instances concurrently."""
    if num_browsers is None:
        num_browsers = min(config.MAX_CONCURRENT_BROWSERS, len(config.PROXY_LIST))
    
    logger.info("=" * 60)
    logger.info(f"MULTI-BROWSER MODE: Running {num_browsers} browsers")
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
    logger.info(f"✗ Failed: {failed_count}")
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
