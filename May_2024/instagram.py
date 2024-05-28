from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from webdriver_manager.chrome import ChromeDriverManager
import time
from twitter_scrape.main import TwitterScrape
from playwright.async_api import Playwright, async_playwright, expect
from playwright_stealth import stealth_async
import json
import pandas as pd
import os
import asyncio
import logging
import numpy as np

logging.basicConfig(filename="run.log", level=logging.INFO)


async def run(playwright: Playwright):
    browser = await playwright.chromium.launch(headless=False, slow_mo=50)
    context = await browser.new_context()
    page = await context.new_page()
    await stealth_async(page)


    await page.goto("https://www.instagram.com/")
    await page.get_by_label("Phone number, username, or").click()
    await page.get_by_label("Phone number, username, or").fill("kiroraynes")
    await page.get_by_label("Phone number, username, or").press("Tab")
    await page.get_by_label("Password").fill("K1rtK1rt")
    await page.get_by_role("button", name="Log in", exact=True).click()

    await page.get_by_role("button", name="Not now").wait_for()
    await page.wait_for_timeout(1000)
    await page.get_by_role("button", name="Not now").click()
    await page.get_by_role("button", name="Not now").wait_for()
    await page.wait_for_timeout(1000)
    await page.get_by_role("button", name="Not Now").click()
    await page.wait_for_timeout(1000)

    files = []

    current_directory = os.getcwd()
    for filename in os.listdir(current_directory):
        if filename.endswith(".xlsx"):
            files.append(filename)

    for filename in files:
        ref = pd.read_excel(filename)
        for index,row in ref.iterrows():
            responses = []

            page.on("response", lambda response: responses.append(response))
            if np.isnan(row['Instagram (followers)']):
                try:
                    await page.goto(row['Instagram'])
                    await page.wait_for_timeout(3000)
                    data_responses = [i for i in responses if 'graphql' in i.request.url]
                    for response in data_responses:
                        data = await response.json()
                        try:
                            ref.at[index, 'Instagram (followers)'] = data['data']['user']['follower_count']
                            print(data['data']['user']['full_name'],data['data']['user']['follower_count'])
                            logging.info("Good response from %s",data['data']['user']['full_name'])
                            break
                        except:
                            logging.error('error with %s', row['Instagram'])
                except:
                    logging.error('error with %s', row['Instagram'])
        ref.to_excel(filename, index=False)

        
        await page.wait_for_timeout(1000)

    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)
        
asyncio.run(main())