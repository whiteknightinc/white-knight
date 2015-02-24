import tweepy


def tweep():
    consumer_key = 'KSupNP0wNh1PfqdSt1qL2Fj6S'
    consumer_secret = 'cu2pRz6NhA7suKK4oncHOYeNbnriMk5t2E75AFJ22nxWE8Dj5w'
    access_token = '3038413908-HkP56dcQINHOOdn0O3AhCOvj5qrI9SQ5MmN4Fo9'
    access_token_secret = 'cTI9JYIjRAbKWyScbAtvjGTUEqIMhKdupmhGBpNBlY8lO'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    tweet = api.home_timeline(count=1)
    print tweet[0].text

if __name__ == '__main__':
    tweep()