import base64
import httpx
from ..models import messages
from playwright.async_api import async_playwright
import logging

LOGGER = logging.getLogger(__name__)

async def hello_world(input: str) -> str:
    LOGGER.info(f"Hello world called with input: {input}")
    return {
        "content": [
            {
                "type": "text",
                "text": "Hello, world!"
            }
        ],
        "isError": False
    }

async def image_generation(prompt: str) -> str:
    LOGGER.info(f"Image generation called with prompt: {prompt}")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get("https://picsum.photos/600/400", timeout=30.0)
            response.raise_for_status()
            
            return {
                "content": [
                    {
                        "type": "image",
                        "data": base64.b64encode(response.content).decode('utf-8'),
                        "mimeType": "image/jpeg"
                    }
                ],
                "isError": False
            }

        except Exception as e:
            LOGGER.error(f"Failed to generate image: {e}")
            return None


    response = requests.get("https://picsum.photos/600/400")
    response.raise_for_status()  # Ensure we got a valid response

    return {
        "content": [
            {
                "type": "image",
                "data": base64.b64encode(response.content).decode('utf-8'),
                "mimeType": "image/jpeg"
            }
        ],
        "isError": False
    }

async def take_screenshot(url: str) -> str:
    """Take a full page screenshot of a URL"""
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        LOGGER.info(f"Launched browser: {browser}")

        try:
            # Create a new page
            page = await browser.new_page()
            LOGGER.info(f"Got page: {page}")

            # Go to the URL and wait for network idle
            await page.goto(url, wait_until="networkidle")
            LOGGER.info(f"Navigated to {url}")
            
            # Take a full page screenshot
            screenshot = await page.screenshot(full_page=True, type='png')
            LOGGER.info(f"Screenshot taken")

            return {
                "content": [
                    {
                        "type": "image",
                        "data": base64.b64encode(screenshot).decode('utf-8'),
                        "mimeType": "image/png"
                    }
                ],
                "isError": False
            }
        finally:
            await browser.close()

tools = [
    {
        "name": "hello_world",
        "tool_method": hello_world,
        "description": "Use this tool when the users asks for a greeting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            }
        }
    },
    {
        "name": "image_generation",
        "tool_method": image_generation,
        "description": "Generate an image based on the input",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"}
            }
        }
    },
    {
        "name": "take_screenshot",
        "tool_method": take_screenshot,
        "description": "Take a full page screenshot of a webpage, including content that requires scrolling",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"}
            },
            "required": ["url"]
        }
    }
]

def create_tools_list_response(message: messages.Request) -> messages.Response:
    return messages.Response(
        id=message.id,
        result={
            "tools": [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": tool["inputSchema"]
                } for tool in tools
            ],
            "nextCursor": "1"
        }
    )

async def create_tool_response(message: messages.Request) -> messages.Response:
    """Create a response for a tool call"""
    tool_name = message.params["name"]
    tool = next((tool for tool in tools if tool["name"] == tool_name), None)
    LOGGER.info(f"Tool name: {tool_name}")
    
    if tool is None:
        return messages.Response(
            id=message.id,
            error=messages.Error(
                code=messages.ErrorCodes.METHOD_NOT_FOUND,
                message=f"Tool not found: {tool_name}"
            )
        )
    else:
        response = await tool["tool_method"](**message.params["arguments"])
        return messages.Response(
            id=message.id,
            result=response
        )
