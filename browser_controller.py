from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from typing import Optional
import random
import config
from logger import logger

class BrowserController:
    """Manages browser lifecycle and page navigation."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.dns_servers = self._select_dns()
        self.proxy_config = self._select_proxy()
    
    def _select_dns(self) -> list:
        """Select random DNS servers for IP variation."""
        if config.USE_DNS_ROTATION and config.DNS_SERVERS:
            dns = random.choice(config.DNS_SERVERS)
            logger.info(f"Selected DNS servers: {dns}")
            return dns
        return []
    
    def _select_proxy(self) -> dict:
        """Select random proxy for IP variation."""
        if config.USE_PROXY_ROTATION and config.PROXY_LIST:
            proxy = random.choice(config.PROXY_LIST)
            logger.info(f"Selected proxy: {proxy.get('server', 'N/A')}")
            return proxy
        elif config.USE_PROXY and config.PROXY_SERVER:
            proxy = {
                "server": config.PROXY_SERVER,
                "username": config.PROXY_USERNAME,
                "password": config.PROXY_PASSWORD
            }
            logger.info(f"Using configured proxy: {proxy['server']}")
            return proxy
        return {}
    
    async def launch(self) -> Page:
        """Launch browser and create a new page with temporary profile."""
        logger.info("Launching browser...")
        
        try:
            self.playwright = await async_playwright().start()
            
            # Browser launch arguments with cache/data clearing
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--disable-default-apps",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-popup-blocking",
                "--disable-infobars",
                "--disable-notifications",
                "--disable-save-password-bubble",
                "--incognito"  # Force incognito mode
            ]
            
            # Add DNS configuration if enabled (simplified approach)
            if self.dns_servers:
                dns_string = ",".join(self.dns_servers)
                logger.info(f"Selected DNS servers: {dns_string}")
            
            launch_options = {
                "headless": config.HEADLESS,
                "args": browser_args,
                "slow_mo": 100 if not config.HEADLESS else 0
            }
            
            # Add proxy if configured
            if self.proxy_config and self.proxy_config.get('server'):
                launch_options["proxy"] = {
                    "server": self.proxy_config['server'],
                    "username": self.proxy_config.get('username', ''),
                    "password": self.proxy_config.get('password', '')
                }
                logger.info(f"Using proxy: {self.proxy_config['server']}")
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            logger.info("Browser process started")
            
            # Create browser context with NO storage (temporary session)
            self.context = await self.browser.new_context(
                viewport=config.VIEWPORT,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="id-ID",
                timezone_id="Asia/Jakarta",
                # Disable storage to ensure clean session
                accept_downloads=False,
                ignore_https_errors=True,
                # No persistent storage
                storage_state=None
            )
            
            self.page = await self.context.new_page()
            self.page.set_default_timeout(config.TIMEOUT)
            
            logger.info("Browser launched successfully (temporary profile)")
            return self.page
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            raise
    
    async def navigate(self, url: str) -> None:
        """Navigate to URL and wait for page load."""
        logger.info(f"Navigating to: {url}")
        await self.page.goto(url, wait_until="domcontentloaded")
        logger.info("Page loaded")
    
    async def wait_for_stability(self, timeout: int = 5000) -> None:
        """Wait for network to be idle."""
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.info("Network idle - page stable")
        except Exception as e:
            logger.warning(f"Network idle timeout: {e}")
    
    async def close(self) -> None:
        """Close browser and cleanup all resources including cache and data."""
        try:
            logger.info("Closing browser and clearing data...")
            
            # Clear cookies and storage before closing
            if self.context:
                try:
                    logger.debug("Clearing cookies and storage...")
                    await asyncio.wait_for(
                        self.context.clear_cookies(),
                        timeout=5
                    )
                    await asyncio.wait_for(
                        self.context.clear_permissions(),
                        timeout=5
                    )
                except asyncio.TimeoutError:
                    logger.warning("Clear storage timeout, forcing close...")
                except Exception as e:
                    logger.debug(f"Clear storage error: {e}")
            
            # Close page with timeout
            if self.page:
                try:
                    await asyncio.wait_for(
                        self.page.close(),
                        timeout=5
                    )
                    logger.debug("Page closed")
                except asyncio.TimeoutError:
                    logger.warning("Page close timeout, forcing...")
                except Exception as e:
                    logger.debug(f"Page close error: {e}")
            
            # Close context with timeout (this removes all session data)
            if self.context:
                try:
                    await asyncio.wait_for(
                        self.context.close(),
                        timeout=5
                    )
                    logger.debug("Context closed (all data cleared)")
                except asyncio.TimeoutError:
                    logger.warning("Context close timeout, forcing...")
                except Exception as e:
                    logger.debug(f"Context close error: {e}")
            
            # Close browser with timeout
            if self.browser:
                try:
                    await asyncio.wait_for(
                        self.browser.close(),
                        timeout=10
                    )
                    logger.debug("Browser closed")
                except asyncio.TimeoutError:
                    logger.warning("Browser close timeout, force killing process...")
                    # Force kill browser process if timeout
                    try:
                        import psutil
                        import os
                        current_process = psutil.Process(os.getpid())
                        children = current_process.children(recursive=True)
                        for child in children:
                            if 'chrome' in child.name().lower() or 'chromium' in child.name().lower():
                                logger.warning(f"Force killing browser process: {child.pid}")
                                child.kill()
                    except Exception as kill_error:
                        logger.debug(f"Force kill error: {kill_error}")
                except Exception as e:
                    logger.debug(f"Browser close error: {e}")
            
            # Stop playwright with timeout
            if self.playwright:
                try:
                    await asyncio.wait_for(
                        self.playwright.stop(),
                        timeout=5
                    )
                    logger.debug("Playwright stopped")
                except asyncio.TimeoutError:
                    logger.warning("Playwright stop timeout")
                except Exception as e:
                    logger.debug(f"Playwright stop error: {e}")
            
            logger.info("Browser closed successfully (all data cleared)")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
