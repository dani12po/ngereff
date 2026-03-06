import asyncio
import sys
import argparse
from agent import AutomationAgent
from logger import logger
import config

async def main():
    """Entry point for the automation agent."""
    parser = argparse.ArgumentParser(description='Browser Automation Agent')
    parser.add_argument('--loop', action='store_true', help='Run in loop mode with auto-restart')
    parser.add_argument('--iterations', type=int, default=None, help='Number of iterations (default: infinite)')
    parser.add_argument('--multi', action='store_true', help='Run multiple browsers concurrently')
    parser.add_argument('--browsers', type=int, default=None, help='Number of concurrent browsers (max 5)')
    args = parser.parse_args()
    
    try:
        # Multi-browser mode
        if args.multi or config.USE_MULTI_BROWSER:
            from multi_browser import run_multi_browser_loop, run_multi_browser
            
            num_browsers = args.browsers or config.MAX_CONCURRENT_BROWSERS
            num_browsers = min(num_browsers, 5)  # Max 5 browsers
            
            logger.info(f"Running in MULTI-BROWSER mode ({num_browsers} browsers)")
            
            if args.loop or config.AUTO_RESTART:
                await run_multi_browser_loop()
            else:
                await run_multi_browser(num_browsers)
        
        # Single browser mode
        else:
            agent = AutomationAgent()
            
            if args.loop or config.AUTO_RESTART:
                logger.info("Running in LOOP mode with auto-restart")
                await agent.run_loop(iterations=args.iterations)
            else:
                logger.info("Running in SINGLE mode")
                success = await agent.run()
                
                if success:
                    logger.info("Automation completed successfully")
                    sys.exit(0)
                else:
                    logger.error("Automation failed")
                    sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
