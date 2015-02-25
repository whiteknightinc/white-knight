import tweepy
import pdb


def load_keys():
    keydict = {}
    with open('twitterkeys.txt', 'r') as f:
        keydict['consumer_key'] = f.readline().rstrip()
        keydict['consumer_secret'] = f.readline().rstrip()
        keydict['access_token'] = f.readline().rstrip()
        keydict['access_token_secret'] = f.readline().rstrip()

    f.close()
    return keydict


def get_nasty_tweets():

    keys = load_keys()

    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    api = tweepy.API(auth)
    tweets = api.home_timeline(count=25)


    f = open("swearWords.txt")
    keywords = []
    for line in f:
        keywords.append(line.rstrip())
    f.close()

    tweets_with_keywords = []

    for tweet in tweets:
        print tweet.text
        for keyword in keywords:
            if keyword in unicode(tweet.text).lower():
                tweets_with_keywords.append(tweet)

    shitty_tweets = {}
    for i in range(len(tweets_with_keywords)):
        user = tweets[i].user.name
        ident = tweets[i].id
        permalink = "www.twitter.com/" + user + "/status/" + str(ident)
        text = tweets[i].text
        shitty_tweets[i] = {
            'text': text,
            'user': user,
            'permalink': permalink
        }
    return shitty_tweets


def tweet_it_out():

    keys = load_keys()

    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    api = tweepy.API(auth)

    # twitter won't let you tweet out duplicates
    api.update_status(status="test tweet")


if __name__ == '__main__':
    pass
