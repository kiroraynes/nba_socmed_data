data = async() => {
    const request = await fetch("https://api.twitter.com/graphql/k5XapwcSikNsEsILW5FvgA/UserByScreenName?variables=%7B%22screen_name%22%3A%22celtics%22%2C%22withSafetyModeUserFields%22%3Atrue%7D&features=%7B%22hidden_profile_likes_enabled%22%3Atrue%2C%22hidden_profile_subscriptions_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22subscriptions_verification_info_is_identity_verified_enabled%22%3Atrue%2C%22subscriptions_verification_info_verified_since_enabled%22%3Atrue%2C%22highlights_tweets_tab_ui_enabled%22%3Atrue%2C%22responsive_web_twitter_article_notes_tab_enabled%22%3Atrue%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D&fieldToggles=%7B%22withAuxiliaryUserLabels%22%3Afalse%7D", {
    "headers": {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "content-type": "application/json",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "x-client-transaction-id": "OPG5MFJg4YfKnhk6MCzHpKSXaT89QtfU9jjxtokn/5KqcPUQ9PxA7aHKZKsMkKw1hW13RjmT3sBMMIvEKZBijsxY+a1oOQ",
        "x-guest-token": "1758019320817582153",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "en",
        "cookie": "guest_id=v1%3A170130925385408257; _ga=GA1.2.1170874524.1701309254; guest_id_marketing=v1%3A170130925385408257; guest_id_ads=v1%3A170130925385408257; _gid=GA1.2.9267356.1707975124; external_referer=8e8t2xd8A2w%3D|0|ziZgIoZIK4nlMKUVLq9KcnBFms0d9TqBqrE%2FyjvSFlFJR45yIlYF%2Bw%3D%3D; gt=1758019320817582153; personalization_id=\"v1_DX3DR75yOJYJzZ2U/R42OA==\"",
        "Referer": "https://twitter.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    },
    "body": null,
    "method": "GET"
    });
    const response = await request.json();
    console.log(response);
}

data()
