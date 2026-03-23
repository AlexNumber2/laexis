import asyncio
import sys
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_nishimura():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Goto knowledge page...")
            await page.goto("https://www.nishimura.com/ja/knowledge")
            search_input_selector = 'input[id^="edit-search-keywords-all"]'
            print("Waiting for selector...")
            await page.wait_for_selector(search_input_selector, timeout=10000)
            print("Filling search query...")
            await page.fill(search_input_selector, "個人情報")
            print("Pressing enter...")
            await page.press(search_input_selector, 'Enter')
            print("Wait for load state networkidle")
            await page.wait_for_load_state("networkidle")
            print("Querying results...")
            items = await page.query_selector_all('a:has(h3)')
            print(f"Found {len(items)} results.")
            await page.screenshot(path="nishimura_debug.png", full_page=True)
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="nishimura_error.png", full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_nishimura())
