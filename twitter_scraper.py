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

    f = open("swearWordsValue.txt")
    keywords = {}
    for line in f:
        word, val = line.rstrip().split(",")
        keywords[word] = int(val)
    f.close()

    tweets_with_keywords = []

    for tweet in tweets:
            score = 0
            words = tweet.text.lower()
            for keyword in keywords.keys():
                count = words.count(keyword)
                length = len(words) / 6
                if count > 0:
                    score += count * (keywords.get(keyword))
                    if score >= 10 or score >= length:
                        tweets_with_keywords.append(tweet)
                        break

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


def tweet_it_out(stat):

    keys = load_keys()

    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    api = tweepy.API(auth)

    # twitter won't let you tweet out duplicates
    api.update_status(status=stat)


if __name__ == '__main__':
    pass
