from playwright.async_api import Playwright, async_playwright, expect
import pandas as pd
import asyncio

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

async def facebook(playwright: Playwright, url) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url, timeout=2000)
    elem = page.locator(f'a[href="{url}/followers/"]')
    text = await elem.inner_text()
    # ---------------------
    await context.close()
    await browser.close()

    return text

ref = pd.read_excel('ligue.xlsx')

async def facebook_main():
    async with async_playwright() as playwright:
        for index, row in ref.iterrows():
            try:
                elem = await facebook(playwright,row['Facebook'])
                ref.at[index, 'Facebook (followers)'] = text_to_int(elem)
            except:
                continue

asyncio.run(facebook_main())

ref.to_excel('ligue.xlsx', index=False)