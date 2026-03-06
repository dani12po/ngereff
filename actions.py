from playwright.async_api import Page, TimeoutError as PlaywrightTimeout
from typing import Optional
import asyncio
import config
from logger import logger

class Actions:
    """Reusable browser actions."""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Wait for element to be visible."""
        timeout = timeout or config.TIMEOUT
        try:
            logger.info(f"Waiting for element: {selector}")
            await self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            logger.info(f"Element found: {selector}")
            return True
        except PlaywrightTimeout:
            logger.error(f"Element not found: {selector}")
            return False
    
    async def click_element(self, selector: str, retry: int = 3) -> bool:
        """Click element with retry logic."""
        for attempt in range(retry):
            try:
                logger.info(f"Clicking element: {selector} (attempt {attempt + 1}/{retry})")
                await self.page.click(selector, timeout=config.TIMEOUT)
                logger.info(f"Clicked: {selector}")
                return True
            except Exception as e:
                logger.warning(f"Click failed on attempt {attempt + 1}: {e}")
                if attempt < retry - 1:
                    await asyncio.sleep(config.RETRY_DELAY)
                else:
                    logger.error(f"Failed to click after {retry} attempts: {selector}")
                    return False
    
    async def fill_input(self, selector: str, value: str, clear: bool = True) -> bool:
        """Fill input field with value."""
        try:
            logger.info(f"Filling input: {selector} with value: {value}")
            if clear:
                await self.page.fill(selector, "")
            await self.page.fill(selector, value)
            logger.info(f"Input filled: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to fill input {selector}: {e}")
            return False
    
    async def type_input(self, selector: str, value: str, delay: int = 50) -> bool:
        """Type into input field with delay (human-like)."""
        try:
            logger.info(f"Typing into: {selector}")
            await self.page.type(selector, value, delay=delay)
            logger.info(f"Typed into: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to type into {selector}: {e}")
            return False
    
    async def wait_for_network_idle(self, timeout: int = 5000) -> None:
        """Wait for network to be idle."""
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.info("Network idle")
        except Exception as e:
            logger.warning(f"Network idle timeout: {e}")
    
    async def get_text(self, selector: str) -> Optional[str]:
        """Get text content of element."""
        try:
            text = await self.page.text_content(selector)
            logger.info(f"Got text from {selector}: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to get text from {selector}: {e}")
            return None
    
    async def is_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        try:
            return await self.page.is_visible(selector)
        except Exception:
            return False
    
    async def click_coordinates(self, x: int, y: int) -> bool:
        """Click at specific coordinates."""
        try:
            logger.info(f"Clicking at coordinates: ({x}, {y})")
            await self.page.mouse.click(x, y)
            return True
        except Exception as e:
            logger.error(f"Failed to click at ({x}, {y}): {e}")
            return False
    
    async def wait_for_captcha_complete(self, max_attempts: int = 10) -> bool:
        """Wait and click CAPTCHA checkbox until it completely disappears."""
        try:
            logger.info("Checking for CAPTCHA and clicking until it disappears...")
            
            captcha_selectors = [
                'iframe[src*="challenges.cloudflare.com"]',
                'iframe[src*="turnstile"]',
                'iframe[id*="cf-chl-widget"]',
                'iframe[title*="Cloudflare"]',
                'iframe[title*="tantangan"]',
                'div.cf-browser-verification',
                '#challenge-form',
                'div[class*="captcha"]',
                'input[type="checkbox"]',
                '[id*="captcha"]',
                '[class*="challenge"]'
            ]
            
            attempts = 0
            while attempts < max_attempts:
                captcha_found = False
                
                # Check if any CAPTCHA element is visible
                for selector in captcha_selectors:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            is_visible = await element.is_visible()
                            if is_visible:
                                captcha_found = True
                                logger.info(f"CAPTCHA still visible: {selector} (attempt {attempts + 1}/{max_attempts})")
                                break
                    except Exception:
                        continue
                
                if not captcha_found:
                    logger.info("CAPTCHA completely disappeared!")
                    return True
                
                # CAPTCHA still visible, wait a bit
                await asyncio.sleep(1)  # Dipercepat dari 2 ke 1 detik
                attempts += 1
            
            logger.warning(f"CAPTCHA still visible after {max_attempts} attempts, continuing anyway...")
            return True
            
        except Exception as e:
            logger.warning(f"CAPTCHA check error: {e}")
            return True
    
    async def check_success_message(self) -> bool:
        """Check if 'Success!' message is visible."""
        try:
            # Check for success text
            success_selectors = [
                'text=Success!',
                'text=success',
                '//*[contains(text(), "Success")]'
            ]
            
            for selector in success_selectors:
                try:
                    element = await self.page.wait_for_selector(
                        selector, 
                        timeout=2000, 
                        state="visible"
                    )
                    if element:
                        logger.info("Success message detected!")
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"Success check error: {e}")
            return False
    
    async def click_nano_button_by_selector(self) -> bool:
        """Click Nano button using element selector."""
        try:
            # Try multiple selectors for the Nano button (SVG element)
            selectors = [
                'svg.button.noselect[alt="Nano"]',
                'svg.button[alt="Nano"]',
                'svg.button.noselect',
                'svg.button',
                '#root > div > div > div > div:nth-child(1) > div > div > div > svg',
                'svg[width="128"][height="128"]',
                'div > svg.button',
            ]
            
            for selector in selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000, state="visible")
                    if element:
                        await element.click()
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to click Nano button: {e}")
            return False
    
    async def click_captcha_checkbox(self, x: int, y: int) -> bool:
        """Click CAPTCHA checkbox at specific coordinates."""
        try:
            logger.info(f"Attempting to click CAPTCHA checkbox...")
            
            # Method 1: Try to find and click inside Cloudflare Turnstile iframe
            logger.info("Looking for Cloudflare Turnstile iframe...")
            
            # Wait for iframe to load
            await asyncio.sleep(0.5)
            
            # Get all frames
            frames = self.page.frames
            logger.info(f"Found {len(frames)} frames")
            
            for frame in frames:
                frame_url = frame.url
                logger.info(f"Checking frame: {frame_url[:100]}...")
                
                # Check if this is Cloudflare Turnstile iframe
                if 'challenges.cloudflare.com' in frame_url or 'turnstile' in frame_url:
                    logger.info(f"Found Cloudflare Turnstile iframe!")
                    
                    try:
                        # Try multiple selectors for checkbox inside iframe
                        checkbox_selectors = [
                            'input[type="checkbox"]',
                            'input[id*="challenge"]',
                            'input[id*="cf"]',
                            'span[role="checkbox"]',
                            'div[role="checkbox"]',
                            'label',
                            'input',
                            'span'
                        ]
                        
                        for selector in checkbox_selectors:
                            try:
                                element = await frame.wait_for_selector(selector, timeout=2000, state="visible")
                                if element:
                                    logger.info(f"Found checkbox with selector: {selector}")
                                    await element.click()
                                    logger.info("✓ Clicked checkbox inside Turnstile iframe")
                                    return True
                            except Exception as e:
                                logger.debug(f"Selector {selector} not found: {e}")
                                continue
                        
                        # If no checkbox found, try clicking the iframe itself
                        logger.info("Clicking iframe area...")
                        await frame.click('body')
                        logger.info("✓ Clicked iframe body")
                        return True
                        
                    except Exception as e:
                        logger.warning(f"Error clicking inside iframe: {e}")
            
            # Method 2: Try to click the iframe element itself on main page
            logger.info("Trying to click iframe element on main page...")
            iframe_selectors = [
                'iframe[src*="challenges.cloudflare.com"]',
                'iframe[src*="turnstile"]',
                'iframe[id*="cf-chl-widget"]',
                'iframe[title*="Cloudflare"]',
                'iframe[title*="tantangan"]'
            ]
            
            for selector in iframe_selectors:
                try:
                    iframe_element = await self.page.wait_for_selector(selector, timeout=2000, state="visible")
                    if iframe_element:
                        logger.info(f"Found iframe with selector: {selector}")
                        # Get iframe position and click in the middle
                        box = await iframe_element.bounding_box()
                        if box:
                            click_x = box['x'] + box['width'] / 2
                            click_y = box['y'] + box['height'] / 2
                            logger.info(f"Clicking iframe at ({click_x}, {click_y})")
                            await self.page.mouse.click(click_x, click_y)
                            logger.info("✓ Clicked iframe element")
                            return True
                except Exception as e:
                    logger.debug(f"Iframe selector {selector} failed: {e}")
                    continue
            
            # Method 3: Fallback to coordinates
            logger.info(f"Using coordinate fallback: ({x}, {y})")
            await self.page.mouse.click(x, y)
            logger.info("✓ Clicked at coordinates")
            return True
            
        except Exception as e:
            logger.error(f"All CAPTCHA click methods failed: {e}")
            return False
    
    async def click_nano_button(self, x: int, y: int) -> bool:
        """Click the Nano button to start earning."""
        try:
            logger.info(f"Clicking Nano button at ({x}, {y})")
            await self.page.mouse.click(x, y)
            logger.info("Nano button clicked successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to click Nano button: {e}")
            return False
    
    async def check_success_message(self) -> bool:
        """Check if 'Success!' message is visible."""
        try:
            # Check for success text
            success_selectors = [
                'text=Success!',
                'text=success',
                '//*[contains(text(), "Success")]'
            ]
            
            for selector in success_selectors:
                try:
                    element = await self.page.wait_for_selector(
                        selector, 
                        timeout=2000, 
                        state="visible"
                    )
                    if element:
                        logger.info("Success message detected!")
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"Success check error: {e}")
            return False
    
    async def check_captcha_required(self) -> bool:
        """Check if CAPTCHA is required to continue."""
        try:
            captcha_selectors = [
                'text=Please complete the captcha below to continue',
                'text=complete the captcha',
                '//*[contains(text(), "complete the captcha")]',
                '//*[contains(text(), "captcha below")]'
            ]
            
            for selector in captcha_selectors:
                try:
                    element = await self.page.wait_for_selector(
                        selector, 
                        timeout=500, 
                        state="visible"
                    )
                    if element:
                        logger.warning("⚠️ CAPTCHA required to continue!")
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"CAPTCHA check error: {e}")
            return False
    
    async def check_click_success(self) -> bool:
        """Check if click was successful (green checkmark detected)."""
        try:
            # Method 1: Check for dollar amount increase notification (most reliable)
            try:
                # Look for text containing "+$" which indicates earning
                page_text = await self.page.text_content('body')
                if page_text and '+$' in page_text:
                    logger.info("✓ Click success detected (dollar increase +$)!")
                    return True
            except Exception as e:
                logger.debug(f"Dollar check error: {e}")
            
            # Method 2: Check for green checkmark SVG (any green color)
            success_indicators = [
                # Any SVG with green color
                'svg[style*="rgb(34, 197, 94)"]',
                'svg[style*="rgb(22, 163, 74)"]',
                'svg[style*="rgb(16, 185, 129)"]',
                'svg path[fill*="rgb(34, 197, 94)"]',
                'svg path[fill*="rgb(22, 163, 74)"]',
                'svg path[fill*="rgb(16, 185, 129)"]',
                'svg circle[fill*="rgb(34, 197, 94)"]',
                'svg circle[fill*="rgb(22, 163, 74)"]',
                'svg circle[fill*="rgb(16, 185, 129)"]',
                # Hex colors
                'svg path[fill*="#22c55e"]',
                'svg path[fill*="#16a34a"]',
                'svg path[fill*="#10b981"]',
                # Class-based
                'svg[class*="text-green"]',
                '[class*="text-green"] svg',
                'svg[class*="success"]',
                '[class*="success"] svg',
            ]
            
            for selector in success_indicators:
                try:
                    element = await self.page.wait_for_selector(
                        selector, 
                        timeout=300, 
                        state="visible"
                    )
                    if element:
                        logger.info(f"✓ Click success detected (green checkmark via {selector})!")
                        return True
                except Exception:
                    continue
            
            logger.debug("No success indicators found")
            return False
        except Exception as e:
            logger.debug(f"Click success check error: {e}")
            return False
    
    async def check_rate_limit_message(self) -> bool:
        """Check if rate limit message is visible WITHOUT green checkmark."""
        try:
            # Check for rate limit text FIRST (before checking success)
            rate_limit_selectors = [
                'text=Please wait a moment before clicking again',
                'text=Invite friends to earn more',
                'text=Please wait',
                '//*[contains(text(), "Please wait a moment")]',
                '//*[contains(text(), "wait a moment before clicking")]',
                '//*[contains(text(), "Invite friends to earn more")]'
            ]
            
            rate_limit_found = False
            for selector in rate_limit_selectors:
                try:
                    element = await self.page.wait_for_selector(
                        selector, 
                        timeout=500, 
                        state="visible"
                    )
                    if element:
                        rate_limit_found = True
                        logger.warning(f"⚠️ Rate limit message detected: {selector}")
                        break
                except Exception:
                    continue
            
            if not rate_limit_found:
                return False
            
            # Rate limit message found, now check if there's also a green checkmark
            has_success = await self.check_click_success()
            if has_success:
                # If there's green checkmark, ignore rate limit message
                logger.info("Rate limit message found BUT click is successful (green), continuing...")
                return False
            
            # Rate limit WITHOUT success
            logger.error("⚠️ Rate limit message WITHOUT green checkmark - browser needs referral!")
            return True
            
        except Exception as e:
            logger.debug(f"Rate limit check error: {e}")
            return False
    
    async def should_close_browser(self) -> bool:
        """Check if browser should be closed (rate limited without success)."""
        try:
            logger.info("Checking if browser should close...")
            
            # Check if rate limited
            is_rate_limited = await self.check_rate_limit_message()
            
            if is_rate_limited:
                # Double check - wait 2 seconds and check again
                logger.info("⚠️ Rate limit detected, double checking in 2 seconds...")
                await asyncio.sleep(2)
                
                # Check if success appeared
                has_success = await self.check_click_success()
                if has_success:
                    logger.info("✓ Success detected after rate limit, continuing...")
                    return False
                
                # Still rate limited without success
                is_still_rate_limited = await self.check_rate_limit_message()
                if is_still_rate_limited:
                    logger.warning("⚠️ Rate limited without success - browser should close (needs referral)")
                    return True
            
            logger.debug("Browser should continue (no rate limit or has success)")
            return False
        except Exception as e:
            logger.debug(f"Should close check error: {e}")
            return False

    async def clear_browser_data(self) -> bool:
        """Clear browser cache, cookies, and local storage."""
        try:
            logger.info("Clearing browser data...")
            
            # Clear local storage and session storage via JavaScript
            await self.page.evaluate("""
                () => {
                    localStorage.clear();
                    sessionStorage.clear();
                }
            """)
            
            logger.info("✓ Browser data cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear browser data: {e}")
            return False
