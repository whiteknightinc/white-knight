import praw


def get_comments(subreddit, subnumber):
    r = praw.Reddit('Whiteknight scrapping reddit for nasty comments'
                    'Url: https://github.com/whiteknightinc/white-knight')

    top_posts = r.get_subreddit(subreddit).get_hot(limit=subnumber)
    comments_with_keywords = []
    f = open("swearWordsValue.txt")
    keywords = {}
    for line in f:
        word, val = line.rstrip().split(",")
        keywords[word] = int(val)
    f.close()

    for top_post in top_posts:
        submission = r.get_submission(submission_id=top_post.id)
        submission.replace_more_comments(limit=32, threshold=0)
        all_comments = submission.comments
        comments = praw.helpers.flatten_tree(all_comments)

        for comment in comments:
            score = 0
            words = comment.body.lower()
            for keyword in keywords.keys():
                count = words.count(keyword)
                length = len(words) / 6
                if count > 0:
                    score += count * (keywords.get(keyword))
                    if score >= 10 or score >= length:
                        comments_with_keywords.append(comment)
                        break

    result = {}
    for num in range(len(comments_with_keywords)):
        result[num] = {}
        result[num]['text'] = comments_with_keywords[num].body
        result[num]['user'] = comments_with_keywords[num].author.name
        result[num]['permalink'] = comments_with_keywords[num].permalink
    return result

if __name__ == '__main__':
    entries = get_comments('whiteknighttest', 1)
    for num in entries:
        print entries[num]['text']
