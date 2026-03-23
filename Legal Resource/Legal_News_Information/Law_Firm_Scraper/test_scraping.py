# test_bot_report.py
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from scraper import scrape_all_firms

async def test():
    print("Sending bot test to the 6 target law firms...")
    results = await scrape_all_firms("test")
    print("Bot test finished.")

if __name__ == "__main__":
    asyncio.run(test())
