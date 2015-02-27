from scraper import get_comments
import time

def auto_scrape(subreddits):
    for sub in subreddits:
        subreddits[sub] += len(get_comments(sub, 100))
    return subreddits

if __name__ == '__main__':
    subreddits = {'pics':0, 'funny':0, 'politics':0, 
    'gaming':0, 'askreddit':0}
    try:
        while True:
            for num in range(1, 11):
                subreddits = auto_scrape(subreddits)
                for sub in subreddits:
                    print "{} {}: {}".format(num, sub, subreddits[sub])
                time.sleep(30)
    except KeyboardInterrupt:
        for sub in subreddits:
            print "final {}: {}".format(sub, subreddits[sub])
