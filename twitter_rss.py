#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import urllib2
import re
import arrow
from jinja2 import Template

class Tweet(object):

    def __init__(self, text, meta, get_pics=False):
        self.raw_text = str(text).decode(encoding='UTF-8')
        self.set_info(meta)
        self.get_pics = get_pics

    def set_info(self, meta):
        for href in meta.findAll('a'):
            self.link = re.sub(r'\(u\'href\', u\'(.*)\'\)', r'\1', str(
                href.attrs[0]))

            span = meta.find('span')
            timestamp = re.sub(r'\(u\'data-time\', u\'(.*)\'\)', r'\1', str(span.attrs[1]))

            self.date = self.cleanTimestamp(timestamp)
            self.author = 'ton auteur que je sais pas comment tu trouves en parsant'

    def __repr__(self):
        return '<Tweet "{text}"" at {date}'.format(text=self.__str__(), date=self.date)

    def __str__(self):
        return self.clean_text(True)

    def clean_text(self, nazi=False):
        output = self.raw_text
        if not nazi:
            to_delete = self.TWIT_DELETE
            to_replace = [{'<s>@</s>': '@'},
                          {'href="/': 'href="http://twitter.com/'}]
            for item in to_delete:
                output = re.sub(item, '', output)
            for item in to_replace:
                for old, new in item.items():
                    output = re.sub(old, new, output)
        else:
            to_delete = self.TWEET_DELETE
            for item in to_delete:
                output = re.sub(item, '', output)
        return output

    def cleanTimestamp(self,timestamp):
        return arrow.Arrow.fromtimestamp(float(timestamp))

    def to_jinja2(self):
        return {
            'author'  : self.author,
            'link' : self.link,
            'date' : self.date.strftime('%a, %d %b %Y %H:%M:%S %z'),
            'content' : self.clean_text(True),
        }

    TWIT_DELETE = [
        ' class="js-tweet-text tweet-text"',
        ' class="twitter-atreply pretty-link"',
        ' class="invisible"',
        ' class="js-display-url"',
        ' class="twitter-hashtag pretty-link js-nav"',
        ' class="twitter-timeline-link"',
        ' class="tco-ellipsis"',
        ' class="invisible"',
        ' data-query-source="hashtag_click"',
        ' rel="nofollow"',
        ' target="_blank"',
        ' data-expanded-url=".*?"',
        ' title=".*?"',
        ' data-query-source="hashtag_click"',
        ' dir="ltr"',
        '<span><span>&nbsp;</span>.*</span>',
        '<span>http://</span>',
        ' data-pre-embedded="true"',
        '<p>', '</p>', '<span>', '</span>', '<strong>', '</strong>']

    TWEET_DELETE = [
        '<p>', '</p>', r'<a href=".*?">', '<s>', '</s>', r'http://twitter.com/search\?q=.*?&amp;src=hash',
        '<span>', '</span>', '</a>', '<b>', '</b>']

class TweetGetter(object):

    def parse_twitter(self):
        content = urllib2.urlopen(self.url)
        print 'Connection successful!'
        soup = BeautifulSoup(content)

        self.title = soup.title.string
        self.tweets = []

        for content in soup.findAll("div", "content"):
            for meta, text in zip(content.findAll("small", "time"), content.findAll("p", "js-tweet-text tweet-text")):
                self.tweets.append(Tweet(text, meta))

    def to_rss(self, server='localhost'):
        with open('rss-model.tpl') as template_file:
            items = list(map(lambda tweet: tweet.to_jinja2(), self.tweets))
            template = Template(template_file.read())
            return template.render(server=server, title=self.url, url=self.url, tweets=items)



class UserTweetGetter(TweetGetter):
    def __init__(self, username, get_pics = False):
        self.username = username
        self.url = "https://twitter.com/{}".format(self.username)
        self.pics = get_pics

        self.parse_twitter()

class HashtagTweetGetter(TweetGetter):
    def __init__(self, hashtag, get_pics = False):
        self.hashtag = hashtag
        self.url = "https://twitter.com/search?q=%23{}&src=typd".format(self.hashtag)
        self.pics = get_pics

        self.parse_twitter()

if __name__ == '__main__':
    tweets = UserTweetGetter('framasoft')
    print tweets.to_rss()
    #import pdb; pdb.set_trace()


#     def generateHtml(self):
#         ''' Create a html file with all the tweets '''
#         try:
#             with open(config.DIR + self.nick + '.html', 'w') as html:
#                 html.write(
#                     '<meta http-equiv="Content-type" content="text/html; charset=UTF-8"/>\n\n')
#                 for tweet in self.tweets:

#                     html.write(str(tweet[1]) + '\n\n')

#             html.close()
#         except IOError:
#             print 'Error: The file ' + self.nick + '.html could not be written into ' + config.DIR + '.'
#             pass

#     def backupTweet(self):
#         ''' Save all the tweets if they are not already saved '''
#         update = True
#         data = ''
#         try:
#             with open(config.DIR + self.nick + '-backup.xml', 'r') as original:
#                 first_tweet = []
#                 first_tweet.append(original.readline())
#                 if first_tweet[0]:
#                     first_tweet = first_tweet[0].split('\'')[1]

#                     for i, tweet in enumerate(self.tweets):
#                         if first_tweet in self.tweets[i][0][0]:
#                             update = False
#                             data = original.read()

#         except IOError:
#             print 'Error: The file ' + self.nick + '-backup.xml could not be read from ' + config.DIR + '.'
#             pass

#         if update:
#             try:
#                 with open(config.DIR + self.nick + '-backup.xml', 'w') as modified:
#                     print 'Update in progress'

#                     for tweet in self.tweets:
#                         modified.write(str(tweet) + '\n\n')
#                     modified.write(str(data))
#                     print 'Update done'
#             except IOError:
#                 print 'Error: The file ' + self.nick + '-backup.xml could not be written into ' + config.DIR + '.'
#                 pass
#         else:
#             print self.nick + ': Already updated, nothing to do'

#     def isRssValid(self):
#         ''' Debug function: check through W3C Feed Validator if feed valid '''

#         url = "http://validator.w3.org/feed/check.cgi?url={}/{}.xml".format(self.server, self.nick)
#         print url
#         content = urllib2.urlopen(url)
#         soup = BeautifulSoup(content)
#         if 'This is a valid RSS feed.' in str(soup.text):
#             print 'This is a valid RSS feed.'
#         elif 'This feed does not validate.' in str(soup.text):
#             print 'This feed does not validate.'
#         elif '404: Not Found' in str(soup.text):
#             print 'Server returned HTTP Error 404: Not Found for URL ' + url

#     def activatePics(self):
#         ''' If PICS == True, will append in RSS-feed pic.twitter.com image '''

#         for i, item in enumerate(self.tweets):
#             tweet = str(self.tweets[i][1])
#             if 'pic.twitter.com' in tweet:
#                 url = re.findall(r'(\S+.com/\S+)', tweet)
#                 for j in url:
#                     if 'pic.twitter.com' in j:
#                         url = 'http://' + str(re.sub(r'.*pic.twitter.com/(\S+)</a>.*', r'pic.twitter.com/\1', j))
#                         content = urllib2.urlopen(url)
#                         soup = BeautifulSoup(content)
#                         pics = re.findall(r'(https?://pbs.twimg.com/media/\S+.jpg:large)', str(soup))
#                         title = soup.title.string
#                         self.tweets[i][2] = [pics[0], title]