import asyncio
from playwright.async_api import async_playwright, Playwright
from playwright_stealth import stealth_async
from typing import Optional
from .api.user import User
# import os
# os.environ["no_proxy"] = "127.0.0.1,localhost"

class TwitterScrape:
    user = User
    def __init__(self, delay: Optional[int] = 5, headless:Optional[bool] = False, username: Optional[str] = None, password: Optional[str] = None):
        self._delay = delay
        self._headless = headless

        User.parent = self
        self.username = username
        self.password = password
        

    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        device_config = self.playwright.devices['Desktop Firefox']
        self.firefox = self.playwright.firefox # or "firefox" or "webkit".
        self.browser = await self.firefox.launch(headless=self._headless)
        self.context = await self.browser.new_context(**device_config, bypass_csp=True)
        self.page = await self.context.new_page()
        
        await stealth_async(self.page)
        

        self.requests = []
        self.responses = []

        self.page.on("request", lambda request: self.requests.append(request))

        async def save_responses_and_body(response): 
            try:
                response._body = await response.body()
                self.responses.append(response)
            except Exception as e:
                pass
        self.page.on("response", save_responses_and_body)
        self._user_agent = await self.page.evaluate("() => navigator.userAgent")
        print(self._user_agent)
        if self.username and self.password:
            await self.login()
        


        
        return self
    async def request_delay(self):
        if self._delay is not None:
            await self.page.wait_for_timeout(self._delay * 1000)
    async def __aexit__(self, type, value, traceback):
        await self.shutdown()


    async def shutdown(self) -> None:
        try:
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
        except Exception:
            pass
        finally:
            if self._headless:
                display = getattr(self, "_display", None)
                if display:
                    display.stop()

    async def __aexit__(self, type, value, traceback):
        await self.shutdown()


    async def login(self):
        await self.page.goto('https://twitter.com/login')

        # Wait for the username input and fill it
        await self.page.fill('input[autocomplete="username"]', self.username)
        
        # Click the Next button
        await self.page.click('text="Next"')
        await self.page.wait_for_timeout(2000)
        # Wait for the password input to be visible and fill it
        await self.page.fill('input[name="password"]', self.password)
        
        # Click the login button
        await self.page.click('text="Log in"')
        await self.page.wait_for_timeout(3000)
        
        # Add a wait here to ensure login is complete, could be a wait for navigation or specific element that indicates you're logged in
        await self.page.wait_for_selector('a[aria-label="Profile"]', timeout=20000)