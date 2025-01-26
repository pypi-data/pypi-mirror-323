from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright
import asyncio
import logging

logger = logging.getLogger(__name__)

class WebBrowserTool:
    """
    A tool for performing browser automation tasks using Playwright.
    """

    def __init__(self, headless: bool = True):
        """
        Initialize the WebBrowserTool.

        Args:
            headless (bool): Whether to run the browser in headless mode (default: True).
        """
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        """
        Start the browser and create a new context and page.
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        logger.info("Browser started successfully.")

    async def close(self):
        """
        Close the browser and cleanup resources.
        """
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()
        logger.info("Browser closed successfully.")

    async def navigate(self, url: str) -> str:
        """
        Navigate to a specific URL.

        Args:
            url (str): The URL to navigate to.

        Returns:
            str: The page title after navigation.
        """
        if not self.page:
            raise RuntimeError("Browser is not started. Call start() first.")

        await self.page.goto(url)
        title = await self.page.title()
        logger.info(f"Navigated to {url}. Page title: {title}")
        return title

    async def fill_form(self, fields: Dict[str, str]) -> str:
        """
        Fill a form with the provided fields.

        Args:
            fields (Dict[str, str]): A dictionary of field names and values to fill.

        Returns:
            str: A success message.
        """
        if not self.page:
            raise RuntimeError("Browser is not started. Call start() first.")

        for field, value in fields.items():
            await self.page.fill(f'input[name="{field}"]', value)
            logger.info(f"Filled field '{field}' with value '{value}'.")

        return "Form filled successfully."

    async def click(self, selector: str) -> str:
        """
        Click an element on the page.

        Args:
            selector (str): The CSS selector of the element to click.

        Returns:
            str: A success message.
        """
        if not self.page:
            raise RuntimeError("Browser is not started. Call start() first.")

        await self.page.click(selector)
        logger.info(f"Clicked element with selector '{selector}'.")
        return f"Clicked element: {selector}"

    async def scrape(self, selector: str) -> List[Dict[str, str]]:
        """
        Scrape data from the page.

        Args:
            selector (str): The CSS selector of the elements to scrape.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the scraped data.
        """
        if not self.page:
            raise RuntimeError("Browser is not started. Call start() first.")

        elements = await self.page.query_selector_all(selector)
        scraped_data = []
        for element in elements:
            text = await element.inner_text()
            scraped_data.append({"text": text.strip()})
            logger.info(f"Scraped text: {text.strip()}")

        return scraped_data

    async def execute_step(self, step: Dict[str, Any]) -> str:
        """
        Execute a browser automation step.

        Args:
            step (Dict[str, Any]): A dictionary containing the step details.
                - "action": The action to perform (e.g., "navigate", "fill_form", "click", "scrape").
                - "details": The details required for the action (e.g., URL, form fields, selector).
                - "website": The website to perform the action on (optional).

        Returns:
            str: The result of the step execution.
        """
        action = step.get("action")
        details = step.get("details")
        website = step.get("website", "https://www.google.com")

        if not self.page:
            await self.start()

        try:
            if action == "navigate":
                return await self.navigate(details)
            elif action == "fill_form":
                return await self.fill_form(details)
            elif action == "click":
                return await self.click(details)
            elif action == "scrape":
                return str(await self.scrape(details))
            else:
                return f"Unknown action: {action}"
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            return f"Error executing step: {e}"