import tweepy


def get_nasty_tweets():
    consumer_key = 'KSupNP0wNh1PfqdSt1qL2Fj6S'
    consumer_secret = 'cu2pRz6NhA7suKK4oncHOYeNbnriMk5t2E75AFJ22nxWE8Dj5w'
    access_token = '3038413908-HkP56dcQINHOOdn0O3AhCOvj5qrI9SQ5MmN4Fo9'
    access_token_secret = 'cTI9JYIjRAbKWyScbAtvjGTUEqIMhKdupmhGBpNBlY8lO'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    tweets = api.home_timeline(count=25)

    f = open("swearWords.txt")
    keywords = []
    for line in f:
        keywords.append(line.rstrip())
    f.close()

    tweets_with_keywords = []

    for tweet in tweets:
        text = tweet.text
        for keyword in keywords:
            if keyword in text:
                tweets_with_keywords.append(tweet)
                break

    shitty_tweets = {}
    for i in range(len(tweets_with_keywords)):
        user = tweets[i].user.name
        ident = tweets[i].id
        permalink = "www.twitter.com/"+user+"/status/"+str(ident)
        text = tweets[i].text
        shitty_tweets[i] = {
            'text': text,
            'user': user,
            'permalink': permalink
            }
    return shitty_tweets

if __name__ == '__main__':
    print get_nasty_tweets()