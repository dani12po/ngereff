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
        self.click_success = False  # Track if clicks were successful
    
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
            
            # Auto-click Nano button with human-like timing and batch rest
            logger.info(f"Starting auto-click Nano button: {config.CLICK_COUNT} times (or until no more green notifications)")
            logger.info(f"Initial delays: {config.CLICK_DELAY_MIN}s - {config.CLICK_DELAY_MAX}s")
            logger.info(f"Fast delays (after success): {config.CLICK_DELAY_FAST_MIN}s - {config.CLICK_DELAY_FAST_MAX}s")
            logger.info(f"Batch clicking: {config.CLICK_BATCH_SIZE} clicks → {config.CLICK_BATCH_REST}s rest")
            logger.info("Waiting for Nano button to be ready...")
            await asyncio.sleep(1)
            
            import random
            rate_limit_pause = 0
            success_detected = False
            fast_mode = False
            consecutive_no_success = 0  # Track consecutive clicks without success notification
            captcha_retry_count = 0  # Track CAPTCHA retries
            
            for i in range(config.CLICK_COUNT):
                # PRIORITY 1: Check if browser should be closed (rate limited without success)
                # Check EVERY click for faster detection
                if i > 0:
                    should_close = await self.actions.should_close_browser()
                    if should_close:
                        logger.error("⚠️⚠️⚠️ BROWSER NEEDS REFERRAL - CLOSING IMMEDIATELY ⚠️⚠️⚠️")
                        logger.error("Message: 'Please wait a moment before clicking again. Invite friends to earn more'")
                        await self._take_screenshot("needs_referral")
                        return False  # Return False to indicate failure - browser will close
                
                # PRIORITY 2: Check if CAPTCHA is required
                if i > 0 and i % config.CLICK_CHECK_INTERVAL == 0:
                    needs_captcha = await self.actions.check_captcha_required()
                    if needs_captcha:
                        logger.warning("⚠️ CAPTCHA required during clicking, attempting to solve...")
                        captcha_retry_count += 1
                        
                        # Click CAPTCHA checkbox
                        await self.actions.click_captcha_checkbox(
                            config.CAPTCHA_CHECKBOX_POSITION[0],
                            config.CAPTCHA_CHECKBOX_POSITION[1]
                        )
                        await asyncio.sleep(2)
                        
                        # Check if still successful after CAPTCHA
                        has_success_after_captcha = await self.actions.check_click_success()
                        if not has_success_after_captcha:
                            logger.error("⚠️ No green notification after CAPTCHA, browser will close")
                            await self._take_screenshot("captcha_no_success")
                            return False
                        else:
                            logger.info("✓ CAPTCHA solved, green notifications still appearing")
                            captcha_retry_count = 0  # Reset counter
                        
                        # If CAPTCHA appears too many times, close browser
                        if captcha_retry_count > 3:
                            logger.error("⚠️ CAPTCHA appeared too many times (>3), closing browser")
                            await self._take_screenshot("captcha_too_many")
                            return False
                
                # PRIORITY 3: Check for rate limit message (only if not in fast mode)
                # This is redundant with should_close_browser but kept for logging
                if not fast_mode and i > 0 and i % config.CLICK_CHECK_INTERVAL == 0:
                    is_rate_limited = await self.actions.check_rate_limit_message()
                    if is_rate_limited:
                        logger.warning(f"⚠️ Rate limit detected at click {i+1}, pausing for 5 seconds...")
                        await asyncio.sleep(5)
                        rate_limit_pause += 1
                        
                        # If rate limited multiple times, increase pause
                        if rate_limit_pause > 2:
                            logger.warning(f"⚠️ Rate limited {rate_limit_pause} times, pausing for 10 seconds...")
                            await asyncio.sleep(10)
                
                # Try to click using selector (SVG element)
                clicked = await self.actions.click_nano_button_by_selector()
                
                # If selector method fails, use coordinates as fallback
                if not clicked:
                    logger.warning(f"Selector failed on click {i+1}, using coordinates")
                    await self.actions.click_coordinates(
                        config.NANO_BUTTON_POSITION[0], 
                        config.NANO_BUTTON_POSITION[1]
                    )
                
                # Check if click was successful (green checkmark + dollar)
                if i == 0 or (i + 1) % config.CLICK_CHECK_INTERVAL == 0:  # Check every X clicks
                    has_success = await self.actions.check_click_success()
                    
                    if has_success:
                        consecutive_no_success = 0  # Reset counter
                        if not success_detected:
                            success_detected = True
                            fast_mode = True
                            logger.info("✓✓✓ Click success confirmed! Switching to FAST MODE (100ms clicks)")
                            logger.info("Browser will continue until green notifications stop appearing")
                        else:
                            logger.debug(f"Still getting green notifications at click {i+1}")
                    else:
                        if success_detected:
                            # Was successful before, but now no notification
                            consecutive_no_success += 1
                            logger.info(f"No green notification detected ({consecutive_no_success}x)")
                            
                            # If no success for 3 consecutive checks (15 clicks), stop
                            if consecutive_no_success >= 3:
                                logger.info("✓ No more green notifications detected for 3 checks, stopping clicks")
                                logger.info(f"Total clicks completed: {i+1}")
                                break
                
                if (i + 1) % 10 == 0:  # Log every 10 clicks
                    mode_text = "FAST MODE" if fast_mode else "NORMAL MODE"
                    logger.info(f"Progress: {i+1}/{config.CLICK_COUNT} clicks [{mode_text}]")
                
                # Use random delay - FAST if success detected, SLOW if not
                if config.CLICK_DELAY_RANDOM:
                    if fast_mode:
                        # Fast mode: 80-120ms
                        delay = random.uniform(config.CLICK_DELAY_FAST_MIN, config.CLICK_DELAY_FAST_MAX)
                    else:
                        # Normal mode: 250-500ms
                        delay = random.uniform(config.CLICK_DELAY_MIN, config.CLICK_DELAY_MAX)
                else:
                    delay = config.CLICK_DELAY
                
                await asyncio.sleep(delay)
                
                # Batch rest: After every CLICK_BATCH_SIZE clicks, rest for CLICK_BATCH_REST seconds
                # Skip batch rest in fast mode
                if not fast_mode and (i + 1) % config.CLICK_BATCH_SIZE == 0 and (i + 1) < config.CLICK_COUNT:
                    logger.info(f"Batch rest after {i+1} clicks, pausing for {config.CLICK_BATCH_REST}s...")
                    await asyncio.sleep(config.CLICK_BATCH_REST)
            
            logger.info("Auto-click Nano button completed")
            
            # Store success status for timeout handling
            self.click_success = success_detected
            
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
