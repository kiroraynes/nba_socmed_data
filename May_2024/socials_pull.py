from twitter_scrape.main import TwitterScrape
from playwright.async_api import Playwright, async_playwright, expect
from playwright_stealth import stealth_async
import pandas as pd
import asyncio
import requests
import json
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException
from seleniumwire.utils import decode as sw_decode

from webdriver_manager.chrome import ChromeDriverManager
from fake_headers import Headers
import time
import numpy as np
import re
import argparse

load_dotenv('.env')
API_KEY = os.getenv("API_KEY")

def chrome_driver(webdriver_path=None):
    # Generate a fake user agent
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    ua = user_agent_rotator.get_random_user_agent()

    browser_options = ChromeOptions()
    browser_options.add_argument("--headless")
    # browser_options.add_argument("--incognito")
    # browser_options.add_argument("--log-level=3")
    # browser_options.add_argument("--disable-gpu")
    # browser_options.add_argument("--disable-extensions")
    # browser_options.add_argument("--disable-notifications")
    # browser_options.add_argument("--disable-popup-blocking")
    browser_options.add_argument(f"user-agent={ua}")

    if webdriver_path is not None:
        driver = webdriver.Chrome(
            service=ChromeService(executable_path=f"{webdriver_path}"),
            options=browser_options
        )
    else:
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=browser_options)

    return driver

def text_to_int(text):
    # Initialize a multiplier
    multiplier = 1
    text = str(text)
    
    # Check if 'M' is in the text, indicating millions
    if 'na' in text:
        if 'M' in text:
            multiplier = 1000000
            text = text.replace('M (na) follower', '')  # Remove 'M' for conversion
        elif 'K' in text:
            multiplier = 1000
            text = text.replace('K (na) follower', '')
    else:
        if 'M' in text:
            multiplier = 1000000
            text = text.replace('M followers', '')  # Remove 'M' for conversion
        elif 'K' in text:
            multiplier = 1000
            text = text.replace('K followers', '')
    return int(float(text) * multiplier)

def is_social_media_link(url):
    # Regular expression patterns for matching social media URLs
    patterns = {
        'Facebook': r'https?://(www\.)?facebook\.com/[\w.]+/?',
        'X (Twitter)': r'https?://(www\.)?twitter\.com/[\w.]+/?',
        'Instagram': r'https?://(www\.)?instagram\.com/[\w.]+/?',
        'Youtube': r'https?://(www\.)?(youtube\.com|youtu\.be)/[\w.]+/?',
        'TikTok':r'https?://(www\.)?tiktok\.com/@[\w.]+/?'
    }
    # Check each social media pattern to see if it matches the URL
    for platform, pattern in patterns.items():
        if re.match(pattern, url):
            return True, platform
    
    # If no pattern matches, the URL is not recognized as a social media link
    return False, None

async def run(url):
    async with TwitterScrape(delay=5, headless=False) as api:
        init_user = api.user(url=url)
        profile = await init_user.scrape()
        return profile

async def facebook(playwright: Playwright, url) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await stealth_async(page)
    await page.goto(url)
    await page.wait_for_timeout(2000)
    await page.get_by_label("Close").wait_for()
    await page.get_by_label("Close").click()
    if url.endswith("/"):
        url = url.rstrip(url[-1])
    if 'profile.php' in url:
        elem = page.locator(f'a[href="{url}&sk=followers"]')
    else:
        elem = page.locator(f'a[href="{url}/followers/"]')
    text = await elem.inner_text()
    # ---------------------
    await context.close()
    await browser.close()

    return text

files = []
parser = argparse.ArgumentParser(description='Read an Excel file.')
parser.add_argument('-f','--filename', type=str, help='The path to the Excel file you want to read')
args = parser.parse_args()
if args.filename != None:
    files.append(args.filename)
else:
    current_directory = os.getcwd()
    for filename in os.listdir(current_directory):
        if filename.endswith(".xlsx"):

            files.append(filename)

for filename in files:
    print("WORKING---------------",filename)
    ref = pd.read_excel(filename)
    # ref['YouTube (subscribers)'] = ''
    # ref['Instagram (followers)'] = ''
    # ref['Facebook (followers)'] = ''
    # ref['TikTok (followers)'] =''
    # ref['X (Twitter) (followers)'] = ''
    print("----------------------------------------In Twitter")
    if __name__ == "__main__":
        for index, row in ref.iterrows():
            if np.isnan(row['X (Twitter) (followers)']):
                try:
                    profile = asyncio.run(run(row['X (Twitter)']))     
                    print(row['X (Twitter)'], profile)
                    ref.at[index, 'X (Twitter) (followers)'] = int(profile['follower_count'])
                except:
                    continue
    ref.to_excel(filename, index=False)


    #fix yt links
    # for index, row in ref.iterrows():
    #     if row['Youtube']:
    #         try:
    #             response = requests.get(row['Youtube'])
    #             html_content = response.content

    #             # Parse the HTML content
    #             soup = BeautifulSoup(html_content, 'html.parser')

    #             # Find all divs with the class 'p-forge-list-item'
    #             list_items = soup.find('link', rel='canonical')
    #             ref.at[index,'Youtube'] = list_items.get('href')
    #         except Exception as e:
    #             print(e)
    #             continue
    #youtube
    print("----------------------------------------In YouTube")
    ids = [elem.replace("https://www.youtube.com/channel/","") for elem in ref['Youtube'].values]
    yt_followers = []
    batch_size = 50
    for start in range (0, len(ref['Youtube']), batch_size):
        string = ",".join(ids[start: start+batch_size])
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "statistics",
            "id": string,
            "key": API_KEY
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            file = response.json()
            for i in file['items']:
                index_number = ref.index[ref['Youtube'] == ("https://www.youtube.com/channel/" + str(i['id']))].tolist()
                ref.at[index_number[0],'YouTube (subscribers)'] = i['statistics']['subscriberCount']


    # Tiktok
    print("----------------------------------------In TikTok")
    for index, row in ref.iterrows():
        if np.isnan(row['TikTok (followers)']):
            try:
                driver = chrome_driver()
                driver.get(row['TikTok'])
                state_data = json.loads(driver.execute_script("return document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__').textContent"))
                driver.close()
                driver.quit()
                stats_data = state_data['__DEFAULT_SCOPE__']["webapp.user-detail"]["userInfo"]['stats']
                print(row['TikTok'], " ", stats_data['followerCount'])
                ref.at[index, 'TikTok (followers)'] = stats_data['followerCount']
                time.sleep(2)
            except:
                continue


    #Instagram

    # for index,row in ref.iterrows():
    #     try:
    #         driver = chrome_driver()
    #         driver.get(row['Instagram'])
    #         time.sleep(5)
            
    #         for i in driver.requests:
    #             if str(i).startswith('https://www.instagram.com/api/v1/users/web_profile_info'):
    #                 data = sw_decode(i.response.body, i.response.headers.get('Content-Encoding', 'identity'))
    #                 data = data.decode("utf-8")
    #                 data = json.loads(data)
    #                 ref.at[index, 'Instagram (followers)'] = data['data']['user']['edge_followed_by']['count']
    #         driver.close()
    #         driver.quit()
    #     except:
    #         continue

    # Facebook
    print("----------------------------------------In Facebook")
    async def facebook_main():
        async with async_playwright() as playwright:
            for index, row in ref.iterrows():
                if np.isnan(row['Facebook (followers)']):
                    try:
                        elem = await facebook(playwright,row['Facebook'])
                        ref.at[index, 'Facebook (followers)'] = text_to_int(elem)
                    except:
                        continue
    asyncio.run(facebook_main())

    ref.to_excel(filename, index=False)