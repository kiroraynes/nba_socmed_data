import asyncio
import random

from playwright.async_api import expect
from .. import exceptions

TOK_DELAY = 30

class Base:
    
    async def slight_scroll_up(self, speed=4):
        page = self.parent.page
        desired_scroll = -500
        current_scroll = 0
        while current_scroll > desired_scroll:
            current_scroll -= speed + random.randint(-speed, speed)
            await page.evaluate(f"() => window.scrollBy(0, {-speed});")

    async def scroll_to_bottom(self, speed=4):
        page = self.parent.page
        current_scroll_position = await page.evaluate("() => document.documentElement.scrollTop || document.body.scrollTop;")
        new_height = current_scroll_position + 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed + random.randint(-speed, speed)
            await page.evaluate(f"() => window.scrollTo(0, {current_scroll_position});")
            new_height = await page.evaluate("() => document.body.scrollHeight;")

    async def scroll_to(self, position, speed=5):
        page = self.parent.page
        current_scroll_position = await page.evaluate("() => document.documentElement.scrollTop || document.body.scrollTop;")
        new_height = current_scroll_position + 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed + random.randint(-speed, speed)
            await page.evaluate(f"() => window.scrollTo(0, {current_scroll_position});")
            new_height = await page.evaluate("() => document.body.scrollHeight;")
            if current_scroll_position > position:
                break

    async def wait_for_requests(self, api_path, timeout=TOK_DELAY):
        page = self.parent.page
        try:
            async with page.expect_request(api_path, timeout=timeout * 1000) as first:
                return await first.value
        except Exception as e:
            raise exceptions.TimeoutException(str(e))
        
    def extract_tweets(self, data):

        # CONSIDER Presence of note_tweet: is_expandable:true under tweet_results   
        for i in data['data']['user']['result']['timeline_v2']['timeline']['instructions']:
            if i['type'] == 'TimelineAddEntries':
                data = i

        for i in data['entries']:
            if i['entryId'].startswith('profile-conversation'):
                for j in i['content']['items']:
                    block = j['item']['itemContent']['tweet_results']['result']
                    yield ((block['legacy']['full_text'],block['views']))
                    
            if i['entryId'].startswith('tweet'):
                block = i['content']['itemContent']['tweet_results']['result']
                yield ((block['legacy']['full_text'],block['views']))

                