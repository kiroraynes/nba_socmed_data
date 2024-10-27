from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, Iterator, Optional
import asyncio
if TYPE_CHECKING:
    from ..main import TwitterScrape

from .base import Base
from ..exceptions import TimeoutException, EmptyResponseException

class User(Base):
    parent : ClassVar['TwitterScrape']

    _userInfo : dict
    def __init__(self, url):
        self._url = url
        self.page = self.parent.page
        self._delay = self.parent._delay
        self.responses = self.parent.responses

        
            

    async def scrape(self) -> dict:
        async with self.page.expect_request(self._url) as event:
            await self.page.goto(self._url)
            request = await event.value
            response = await request.response()
            if response.status >= 300:
                print("Content is not available")
        
            
        await asyncio.sleep(self._delay)
        data_responses = [i for i in self.responses if '/UserByScreenName?' in i.url]

        data_response = data_responses[-1]
        data = await data_response.json()

        userInfo = {}
        userInfo['username'] = data['data']['user']['result']['legacy']['screen_name']
        userInfo['total_favorites'] = data['data']['user']['result']['legacy']['favourites_count']
        userInfo['follower_count'] = data['data']['user']['result']['legacy']['followers_count']
        userInfo['following_count'] = data['data']['user']['result']['legacy']['friends_count']
        userInfo['media_count'] = data['data']['user']['result']['legacy']['media_count']
        userInfo['statuses_count'] = data['data']['user']['result']['legacy']['statuses_count']
        
        self._userInfo = userInfo
        return userInfo
    
    async def tweets(self, count) -> list:
        data_request_path = '/UserTweets?'
        amount_yielded = 0
        i = 0
        tweets = []
        data_urls = set()
        tries = 3
        MAX_TRIES = 10

        while amount_yielded < count:
        # Assume self.responses gets updated with new responses dynamically
            new_responses = [response for response in self.responses if data_request_path in response.url and response.url not in data_urls]

            for response in new_responses:
                data_urls.add(response.url)  # Mark this URL as processed
                data = await response.json()  # Assuming response.json() is the correct method to get JSON data

                for tweet_data in self.extract_tweets(data):  # Assuming this method extracts tweet information correctly
                    tweets.append(tweet_data)
                    amount_yielded += 1
                    if amount_yielded >= count:
                        return tweets  # Return immediately if the count is reached

            # Trigger new data loading if necessary
            try:
                await self.trigger_new_data_loading()
                tries +=1
            except TimeoutException:
                raise

            if tries > MAX_TRIES:
                raise EmptyResponseException('Backend broke, you may need to log in')


        return tweets
        # while (i == 0) or (amount_yielded < count):
        #     data_responses = [response for response in self.responses if data_request_path in response.url]
        #     try:
        #         data_response = data_responses[-1]
        #         data_urls.extend([data_response.url])
        #         data = await data_response.json()
        #         for i in self.extract_tweets(data):
        #             tweets.append(i)
        #             amount_yielded+=1
        #     except Exception as e:
        #         raise e
        #     i = 1
        # if amount_yielded < count:
        #     valid_data_request = False
        #     tries = 1
        #     MAX_TRIES = 10
        #     while not valid_data_request and amount_yielded < count:
        #         for _ in range(tries):
        #             await self.parent.request_delay()
        #             await self.slight_scroll_up()
        #             await self.parent.request_delay()
        #             await self.scroll_to_bottom()
        #         try:
        #             await self.wait_for_requests(data_request_path, timeout=tries*4)
        #         except TimeoutException:
        #             tries += 1
        #             if tries > MAX_TRIES:
        #                 raise
        #             continue
        #         for response in self.responses:
        #             if data_request_path in response.url and response.url not in data_urls:
        #                 data = response.json()

        #                 try:
        #                     for i in self.extract_tweets(data):
        #                         tweets.append(i)
        #                         amount_yielded+=1
        #                     valid_data_request = True
                        
        #                 except Exception as e:
        #                     raise e
        #             else:
        #                 tries += 1
        #                 break

        # return tweets

    async def trigger_new_data_loading(self):
        # Slightly scroll up first to mimic user behavior
        await self.parent.request_delay()
        await self.slight_scroll_up()
        await self.parent.request_delay()
        # Then scroll back down to the bottom to trigger loading new data
        await self.scroll_to_bottom()
                    


