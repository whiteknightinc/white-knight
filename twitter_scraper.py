import tweepy


def load_keys():
    keydict = {}
    with open('twitterkeys.txt', 'r') as f:
        keydict['consumer_key'] = f.readline().rstrip()
        keydict['consumer_secret'] = f.readline().rstrip()
        keydict['access_token'] = f.readline().rstrip()
        keydict['access_token_secret'] = f.readline().rstrip()

    f.close()
    return keydict


def get_nasty_tweets(handle, tweet_number):
    """
    Get most recent [number] tweets from the specified handle. If handle
    is not specified, grab the feed from DouserBot. Return a dictionary of
    tweets. Each tweet is its own dictionary with user, text, and permalink.
    """

    keys = load_keys()

    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    api = tweepy.API(auth)
    if handle == "":
        tweets = api.home_timeline(count=tweet_number)
    else:
        tweets = api.user_timeline(handle, count=tweet_number)

    f = open("swearWordsValue.txt")
    keywords = {}
    for line in f:
        word, val = line.rstrip().split(",")
        keywords[word] = int(val)
    f.close()

    shitty_tweets = {}
    count = 0
    for tweet in tweets:
        if tweet.user.name == 'Douser':
            continue
        score = 0
        comment_body = tweet.text.lower()
        words = comment_body.split(' ')
        for word in words:
            word = word.rstrip('.')
            word = word.strip('"')
            word = word.rstrip('?')
            if word in keywords:
                score += keywords.get(word)
                if score >= 10:
                    # tweets_with_keywords.append(tweet)
                    shitty_tweets[count] = make_nasty_tweet(tweet)
                    count += 1
                    break

    return shitty_tweets


def tweet_it_out(stat):
    """Tweet the given text to DouserBot's timeline."""
    keys = load_keys()

    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    api = tweepy.API(auth)

    # twitter won't let you tweet out duplicates
    api.update_status(status=stat)


def make_nasty_tweet(tweet):
    """
    Turn a tweet into a dictionary with its username, body, and permalink.
    """
    user = tweet.user.name
    ident = tweet.id
    permalink = "www.twitter.com/" + user + "/status/" + str(ident)
    dicttweet = {
            'text': tweet.text,
            'user': user,
            'permalink': permalink
            }
    return dicttweet

if __name__ == '__main__':
    print get_nasty_tweets()
