import praw

def post_reddit():
    r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                    'Url: https://github.com/whiteknightinc/white-knight')
    r.login(username='whiteknightinc', password='whiteknight123')
    r.submit('whiteknighttest', 'Test Submission', text='Failed Captcha Test')

if __name__ == '__main__':
    post_reddit()
