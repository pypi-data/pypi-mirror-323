# _session.py
import asyncio

from playwright.async_api import async_playwright
import json
import os
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BrowserSession:
    def __init__(self, cookies_file: str | None = "huggingchat_cookies.json",
                 url: str | None = None,
                 username: str | None = None,
                 password: str | None = None, headless=None):
        self.cookies_file = cookies_file
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    @classmethod
    async def create(cls, cookies_file: str | None = "huggingchat_cookies.json",
                     url: str | None = None,
                     username: str | None = None,
                     password: str | None = None,
                     headless=None):
        instance = cls(cookies_file)
        await instance.start(url, username, password, headless)
        return instance

    async def start(self, url, username, password, headless=None):
        """Start a browser session with cookie management"""
        logger.debug(f"Starting browser session for {url}")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True if headless is None else headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        # Try to load existing cookies
        if await self._load_cookies():
            logger.debug("Found existing cookies, attempting to use them...")
            try:
                await self._try_existing_session(url)
            except Exception as e:
                logger.debug(f"Session expired or invalid: {e}")
                await self._login_and_save_cookies(url, username, password)
        else:
            logger.debug("No existing cookies found")
            await self._login_and_save_cookies(url, username, password)

    async def _load_cookies(self):
        """Load cookies from file if they exist"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                logger.debug(f"Loading {len(cookies)} cookies from {self.cookies_file}")
                await self.context.add_cookies(cookies)
                return True
            except Exception as e:
                logger.debug(f"Error loading cookies: {e}")
                return False
        return False

    async def _save_cookies(self):
        """Save current cookies to file"""
        cookies = await self.context.cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)
        logger.debug(f"Saved {len(cookies)} cookies to {self.cookies_file}")

    async def _try_existing_session(self, url):
        """Try to use existing session"""
        logger.debug("Attempting to use existing session...")
        await self.page.goto(url)
        await self.page.wait_for_load_state('networkidle')

        sign_in_button = self.page.locator(
            'button.flex.w-full.flex-wrap.items-center.justify-center.whitespace-nowrap.rounded-full')
        if await sign_in_button.is_visible():
            raise Exception("Session expired - need to login again")

        logger.debug("Existing session valid!")

    async def _login_and_save_cookies(self, url, username, password):
        """Perform login and save new cookies"""
        logger.debug("Performing fresh login...")
        await self.page.goto(url)
        await self.page.wait_for_selector(
            'button.flex.w-full.flex-wrap.items-center.justify-center.whitespace-nowrap.rounded-full')
        await self.page.click('button.flex.w-full.flex-wrap.items-center.justify-center.whitespace-nowrap.rounded-full')

        await self.page.wait_for_load_state('networkidle')
        await self.page.wait_for_selector('input[name="username"]', timeout=10000)

        await self.page.fill('input[name="username"]', username)
        await self.page.fill('input[name="password"]', password)
        await self.page.click('button[type="submit"]')

        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(5)

        await self._save_cookies()
        logger.debug("Login successful, new cookies saved")

    async def close(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.debug("Browser session closed")


class HFBrowserSession(BrowserSession):
    @classmethod
    async def create(cls, cookies_file="huggingchat_cookies.json",
                    url="https://huggingface.co/chat/",
                    username=None,
                    password=None,
                    headless=True):
        try:
            username =  username or os.environ['HUGGINGFACE_USERNAME']
            password = password or os.environ['HUGGINGFACE_PASSWORD']
        except Exception as e:
            raise ValueError("Invalid username or password, set environment variable for \n"
                             "HUGGINGFACE_USERNAME, HUGGINGFACE_PASSWORD")
        return await super().create(cookies_file, url, username, password, headless)