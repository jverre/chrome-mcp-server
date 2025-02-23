from mcp.server.fastmcp import FastMCP
from mcp import types
import logging
import httpx
import base64
from playwright.async_api import async_playwright
from typing import Optional
LOGGER = logging.getLogger(__name__)

mcp = FastMCP("weather")

@mcp.tool()
def hello_world(input: str) -> types.TextContent:
    """Say hello to the user"""
    return types.TextContent(
        type="text",
        text=f"Hello {input}!"
    )

@mcp.tool()
async def image_generation(prompt: str) -> Optional[types.ImageContent]:
    """Generate an image based on a prompt"""
    LOGGER.info(f"Image generation called with prompt: {prompt}")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get("https://picsum.photos/600/400", timeout=30.0)
            response.raise_for_status()
            LOGGER.info(f"Image generation response: {response.content}")

            return types.ImageContent(
                type="image",
                data=base64.b64encode(response.content).decode('utf-8'),
                mimeType="image/jpeg"
            )

        except Exception as e:
            LOGGER.error(f"Failed to generate image: {e}")
            return None

@mcp.tool()
async def take_screenshot(url: str) -> Optional[types.ImageContent]:
    """Take a screenshot of a URL"""
    LOGGER.info(f"Taking screenshot of {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            screenshot = await page.screenshot(full_page=True, type='png')
            
            return types.ImageContent(
                type="image",
                data=base64.b64encode(screenshot).decode('utf-8'),
                mimeType="image/png"
            )
        except Exception as e:
            LOGGER.error(f"Failed to take screenshot: {e}")
            return None
        finally:
            await browser.close()