from playwright.async_api import Playwright, async_playwright, expect
import requests
import asyncio
import re
import pandas as pd

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
async def run(playwright: Playwright):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto('https://www.wnba.com/tickets')
    await page.wait_for_selector('section.Tickets_ticketsPage__content__zLSRW')
    sections = await page.query_selector_all('section.Tickets_ticketsPage__content__zLSRW li')

    links = []
    names = []

    for li in sections:
            # Extract h3 text
            h3_element = await li.query_selector('h3')
            h3_text = await h3_element.text_content()
            names.append(h3_text)

            # Extract a tags
            a = await li.query_selector('a')
            links.append(await a.get_attribute('href'))
    for link, team in zip(links,names):
    # Retrieve the href attribute of each link
        href_links = []
        # Visit the link
        if link:
            # Open each link in a new tab or page
            try:
                new_page = await page.context.new_page()
                await new_page.goto(link)
                await new_page.wait_for_timeout(1000)

                a_tags = await new_page.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a'));
                    return links.map(link => link.href);
                }''')
                    # Extract the 'href' attribute from each 'li' item found
                for item in a_tags:
                    if item:
                        is_valid, platform = is_social_media_link(item)
                        if is_valid:
                            href_links.append(item)
                await new_page.close()
                
            except Exception as e:
                print(e)
                continue
        yield team, href_links
    
        # ---------------------
    await context.close()
    await browser.close()



teams = []
concatenated_urls = []
url_to_follow_items = {}

async def main():
    async with async_playwright() as playwright:  
        async for team, href_links in run(playwright):
        # Fetch the webpage
            try:
                href_links.reverse()
                url_to_follow_items[team] = href_links
            except Exception as e:
                print(e)
                print("check", team)
        
        for team, hrefs in url_to_follow_items.items():
            print(f"{team}: {hrefs}")

        sorted_teams = dict(sorted(url_to_follow_items.items()))
        sorted_teams

        ref = pd.read_excel("wnba.xlsx")

        for (index, row),(key, val)  in zip(ref.iterrows(), sorted_teams.items()):
            try:
                print(key)
                columns = ['Instagram', 'Facebook', 'TikTok','X (Twitter)','Youtube']
                for j in columns:
                    for i in val:
                        is_valid, platform = is_social_media_link(i)
                        if is_valid and j==platform:
                            ref.at[index, platform] = i
                            break
                ref.at[index, 'Teams'] = key
            except:
                continue
            # row['Youtube'] = ([i for i in value if "youtube" in str(i)] + [""])[0]
            # row['Instagram'] = ([i for i in value if "instagram" in str(i)] + [""])[0]
            # row['Facebook'] = ([i for i in value if "facebook" in str(i)] + [""])[0]
            # row['TikTok'] = ([i for i in value if "tiktok" in str(i)] + [""])[0]
            # row['X (Twitter)'] = ([i for i in value if "twitter" in str(i)] + [""])[0]

        ref.to_excel('wnba.xlsx', index=False)

asyncio.run(main())