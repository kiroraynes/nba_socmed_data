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
    browser = await playwright.chromium.launch(headless=False, slow_mo=50)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto('https://www.ligue1.com/clubs/List')
    links = await page.locator('div.ClubListPage-list a').element_handles()
    names = await page.evaluate('''() => {
        const links = Array.from(document.querySelectorAll('#CompetitionClubsListPage > div.ClubListPage-container.container > div > a > div > div.ClubListPage-name > h3'));
        return links.map(link => link.innerText);
    }''')
    i = 0
    for link, team in zip(links,names):
    # Retrieve the href attribute of each link
        href = await link.get_attribute('href')
        href_links = []

        # Visit the link
        if href:
            # Open each link in a new tab or page
            try:
                new_page = await page.context.new_page()
                await new_page.goto('https://www.ligue1.com'+href)
                if i == 0:
                    try:
                        await new_page.get_by_label("Disagree and close: Disagree").click()
                    except TimeoutError:
                        print("no cookie popup")
                
                async with new_page.expect_popup() as page1_info:
                    await new_page.locator('i[class="Icon Icon-globe"]').click()
                page1 = await page1_info.value
                await page1.wait_for_timeout(10000)
                await page1.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                a_tags = await page1.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a'));
                    return links.map(link => link.href);
                }''')
                    # Extract the 'href' attribute from each 'li' item found
                for item in a_tags:
                    if item:
                        is_valid, platform = is_social_media_link(item)
                        if is_valid:
                            href_links.append(item)
                await page1.close()
                await new_page.close()
                i+=1
                
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

        ref = pd.read_excel("ligue.xlsx")

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
                ref.at[index, 'Unnamed: 0'] = key
            except:
                continue
            # row['Youtube'] = ([i for i in value if "youtube" in str(i)] + [""])[0]
            # row['Instagram'] = ([i for i in value if "instagram" in str(i)] + [""])[0]
            # row['Facebook'] = ([i for i in value if "facebook" in str(i)] + [""])[0]
            # row['TikTok'] = ([i for i in value if "tiktok" in str(i)] + [""])[0]
            # row['X (Twitter)'] = ([i for i in value if "twitter" in str(i)] + [""])[0]

        ref.to_excel('ligue.xlsx', index=False)

asyncio.run(main())

