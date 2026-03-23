import asyncio
import sys
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        urls = {
            "mhm": "https://www.morihamada.com/ja/insights/newsletters",
            "cityyuwa": "https://www.city-yuwa.com/publications/?cp=newsletters",
            "miura": "https://www.miura-partners.com/topics_category/major_news/",
            "oneasia": "https://oneasia.legal/category/letter"
        }
        
        for name, url in urls.items():
            try:
                print(f"Inspecting {name}...")
                await page.goto(url, timeout=20000)
                await page.wait_for_load_state("networkidle", timeout=15000)
                await page.screenshot(path=f"C:\\Users\\Alex\\.gemini\\antigravity\\brain\\a67276d9-1f6d-48dc-9cdc-583101eccf49\\{name}_accurate_results.png", full_page=True)
                with open(f"C:\\Users\\Alex\\.gemini\\antigravity\\brain\\a67276d9-1f6d-48dc-9cdc-583101eccf49\\{name}_accurate_dump.html", "w", encoding="utf-8") as f:
                    f.write(await page.content())
            except Exception as e:
                print(f"Error on {name}: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
