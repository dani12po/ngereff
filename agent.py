import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
import config
from browser_controller import BrowserController
from actions import Actions
from logger import logger

class AutomationAgent:
    """Main automation agent orchestrating browser actions."""
    
    def __init__(self):
        self.browser_controller = BrowserController()
        self.actions: Optional[Actions] = None
        self.url = self._build_url()
    
    def _build_url(self) -> str:
        """Build URL with optional referral parameters."""
        if config.USE_REFERRAL and config.REFERRAL_USERNAME:
            url = f"{config.BASE_URL}{config.REFERRAL_USERNAME}?unit={config.UNIT}"
            logger.info(f"Using referral URL: {url}")
        else:
            url = config.BASE_URL
            logger.info(f"Using base URL: {url}")
        return url
    
    async def _take_screenshot(self, name: str = "error") -> None:
        """Take screenshot for debugging."""
        if config.SCREENSHOT_ON_ERROR and self.browser_controller.page:
            try:
                Path(config.SCREENSHOT_DIR).mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"{config.SCREENSHOT_DIR}/{name}_{timestamp}.png"
                await self.browser_controller.page.screenshot(path=filepath, full_page=True)
                logger.info(f"Screenshot saved: {filepath}")
            except Exception as e:
                logger.error(f"Failed to take screenshot: {e}")
    
    async def initialize(self) -> bool:
        """Initialize browser and navigate to target URL."""
        try:
            page = await self.browser_controller.launch()
            self.actions = Actions(page)
            
            await self.browser_controller.navigate(self.url)
            await self.browser_controller.wait_for_stability()
            
            logger.info("Agent initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            await self._take_screenshot("init_error")
            return False
    
    async def execute_workflow(self) -> bool:
        """Execute the main automation workflow."""
        try:
            logger.info("Starting workflow execution...")
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Check and click CAPTCHA once
            logger.info("Checking for CAPTCHA...")
            logger.info("CAPTCHA attempt 1/1 (single click)")
            
            # Click CAPTCHA checkbox once
            await self.actions.click_captcha_checkbox(
                config.CAPTCHA_CHECKBOX_POSITION[0],
                config.CAPTCHA_CHECKBOX_POSITION[1]
            )
            
            # Wait for CAPTCHA processing
            await asyncio.sleep(config.CAPTCHA_CLICK_DELAY)
            logger.info("CAPTCHA clicked, continuing to Nano button...")
            
            # Skip success message check if configured
            if not config.SKIP_SUCCESS_CHECK:
                logger.info("Waiting for Success message...")
                success_found = False
                for attempt in range(config.SUCCESS_WAIT_TIMEOUT):
                    if await self.actions.check_success_message():
                        success_found = True
                        logger.info("Success message found!")
                        break
                    await asyncio.sleep(1)
                
                if not success_found:
                    logger.warning("Success message not found after timeout, continuing anyway...")
            else:
                logger.info("Skipping success message check (faster mode)")
            
            # Additional wait for page stability
            await asyncio.sleep(1)
            
            # Auto-click Nano button 100x using selector
            logger.info(f"Starting auto-click Nano button: {config.CLICK_COUNT} times")
            logger.info("Waiting for Nano button to be ready...")
            await asyncio.sleep(1)
            
            for i in range(config.CLICK_COUNT):
                # Try to click using selector (SVG element)
                clicked = await self.actions.click_nano_button_by_selector()
                
                # If selector method fails, use coordinates as fallback
                if not clicked:
                    logger.warning(f"Selector failed on click {i+1}, using coordinates")
                    await self.actions.click_coordinates(
                        config.NANO_BUTTON_POSITION[0], 
                        config.NANO_BUTTON_POSITION[1]
                    )
                
                if (i + 1) % 10 == 0:  # Log every 10 clicks
                    logger.info(f"Progress: {i+1}/{config.CLICK_COUNT} clicks on Nano button")
                
                await asyncio.sleep(config.CLICK_DELAY)
            
            logger.info("Auto-click Nano button completed")
            
            # Wait to see the dollar amount
            logger.info(f"Waiting {config.WAIT_FOR_DOLLAR}s to see dollar amount...")
            await asyncio.sleep(config.WAIT_FOR_DOLLAR)
            
            await self._take_screenshot("dollar_earned")
            
            logger.info("Workflow completed successfully")
            await self._take_screenshot("success")
            return True
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            await self._take_screenshot("workflow_error")
            return False
    
    async def run(self) -> bool:
        """Run the complete automation agent."""
        try:
            logger.info("=" * 60)
            logger.info("Starting Automation Agent")
            logger.info("=" * 60)
            
            if not await self.initialize():
                return False
            
            success = await self.execute_workflow()
            
            return success
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            await self._take_screenshot("fatal_error")
            return False
        finally:
            await self.cleanup()
    
    async def run_loop(self, iterations: int = None) -> None:
        """Run agent in loop with auto-restart and DNS rotation."""
        iteration = 0
        
        while True:
            iteration += 1
            logger.info("=" * 60)
            logger.info(f"ITERATION {iteration}")
            logger.info("=" * 60)
            
            try:
                # Ensure clean state
                if iteration > 1:
                    logger.info("Waiting before next iteration...")
                    await asyncio.sleep(config.RESTART_DELAY)
                
                success = await self.run()
                
                if success:
                    logger.info(f"✓ Iteration {iteration} completed successfully")
                else:
                    logger.warning(f"✗ Iteration {iteration} failed")
                
                # Check if we should stop
                if iterations and iteration >= iterations:
                    logger.info(f"Completed {iterations} iterations. Stopping.")
                    break
                
                # Reinitialize for next iteration
                if config.AUTO_RESTART:
                    logger.info("Preparing for next iteration...")
                    # Create new browser controller with new proxy/DNS
                    self.browser_controller = BrowserController()
                    self.actions = None
                    self.url = self._build_url()
                else:
                    break
                    
            except KeyboardInterrupt:
                logger.info("Loop interrupted by user")
                break
            except Exception as e:
                logger.error(f"Loop iteration {iteration} error: {e}")
                logger.info("Attempting to recover...")
                
                # Cleanup and reinitialize
                try:
                    await self.cleanup()
                except Exception:
                    pass
                
                self.browser_controller = BrowserController()
                self.actions = None
                self.url = self._build_url()
                
                await asyncio.sleep(config.RESTART_DELAY)
    
    async def cleanup(self) -> None:
        """Cleanup resources and clear all browser data."""
        try:
            logger.info("Cleaning up...")
            
            # Clear browser data before closing
            if self.actions:
                try:
                    await self.actions.clear_browser_data()
                except Exception as e:
                    logger.debug(f"Clear data error: {e}")
            
            # Close browser
            await self.browser_controller.close()
            
            # Add small delay to ensure cleanup completes
            await asyncio.sleep(0.5)
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
