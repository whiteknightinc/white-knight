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

    # tweets_with_keywords = []
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

    # for i in range(len(tweets_with_keywords)):
    #     user = tweets_with_keywords[i].user.name
    #     ident = tweets_with_keywords[i].id
    #     permalink = "www.twitter.com/" + user + "/status/" + str(ident)
    #     text = tweets_with_keywords[i].text
    #     shitty_tweets[i] = {
    #         'text': text,
    #         'user': user,
    #         'permalink': permalink
    #     }
    return shitty_tweets


def tweet_it_out(stat):

    keys = load_keys()

    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    api = tweepy.API(auth)

    # twitter won't let you tweet out duplicates
    api.update_status(status=stat)


def make_nasty_tweet(tweet):
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
