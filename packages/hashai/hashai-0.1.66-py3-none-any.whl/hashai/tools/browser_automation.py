import logging
import json
from playwright.sync_api import sync_playwright
from sentence_transformers import util
from .session_memory import SessionMemory
from .base_tool import BaseTool

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BrowserAutomationTool(BaseTool):
    name = "BrowserAutomation"
    description = "Performs dynamic browser automation tasks based on user queries."

    def __init__(self, llm, semantic_model):
        super().__init__()
        self.llm = llm
        self.semantic_model = semantic_model
        self.memory = SessionMemory()  # Store session memory

    def parse_query(self, query: str, context: dict = None) -> str:
        """
        Parse the query to understand what action is required (e.g., search job, buy product, etc.)
        Generate dynamic code based on the query.
        
        Args:
            query (str): The user's query.
            context (dict): Current session context, including memory.

        Returns:
            str: Playwright-compatible Python code to perform the task.
        """
        # Pass the user's query and context to the LLM to generate dynamic code.
        context_text = f"Current URL: {context.get('current_url', 'None')}" if context else "No context available."
        prompt = f"""
        You are a browser automation assistant. Below is the user's query and the current webpage context:
        
        Context: {context_text}

        User Query: "{query}"

        Based on the context, generate the necessary Playwright code to perform the action.

        The action could be: 
        - Searching for products
        - Filling out forms
        - Clicking buttons
        - Extracting data
        - Any other action the user requests.

        Provide only the Playwright code to execute this action.
        """
        try:
            logger.debug(f"Sending prompt to LLM: {prompt}")
            llm_response = self.llm.generate(prompt=prompt)
            logger.debug(f"LLM response: {llm_response}")
            return llm_response.strip()
        except Exception as e:
            logger.error(f"Failed to parse query to code: {e}")
            raise ValueError("Error generating code. Please refine your query.")

    def execute_action(self, page, generated_code: str) -> str:
        """
        Execute the dynamically generated Playwright code on the webpage.
        
        Args:
            page: Playwright page object.
            generated_code: The dynamically generated code from LLM.
        
        Returns:
            str: Execution result message.
        """
        try:
            logger.debug(f"Executing dynamic code: {generated_code}")
            exec(generated_code, {"page": page, "__builtins__": __builtins__})
            return "Action executed successfully."
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return f"Execution failed with error: {e}"

    def handle_query(self, query: str) -> str:
        """
        Handle the user query, parse it, and perform the action dynamically.
        
        Args:
            query (str): The user's query.

        Returns:
            str: The result or status message.
        """
        context = {
            "current_url": self.memory.current_url,
        }

        # Step 1: Parse the query into dynamic code
        try:
            generated_code = self.parse_query(query, context=context)
        except ValueError as e:
            logger.error(f"Error in code generation: {e}")
            return str(e)

        # Step 2: Execute the generated dynamic code
        try:
            if not self.memory.browser:
                logger.debug("Launching browser...")
                with sync_playwright() as p:
                    self.memory.set_browser(p.chromium.launch(headless=False))
                    self.memory.set_page(self.memory.browser.new_page())
                logger.debug("Browser launched successfully.")

            page = self.memory.page
            result = self.execute_action(page, generated_code)
            return result
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return f"Execution failed with error: {e}"

    def close_session(self):
        """Clear the session memory."""
        logger.debug("Clearing session memory.")
        self.memory.clear()
