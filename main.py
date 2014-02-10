from google.appengine.ext import deferred
from google.appengine.api import urlfetch
import re
import urllib
import webapp2
import rdbms
import logging

re_keywords = re.compile(r'<a href=\"/(.*)/\">')

def grap_keywords(url):
    #import pdb; pdb.set_trace()
    r = urlfetch.fetch(url)
    pages = re_keywords.findall(r.content)

    for k in pages:
        try:
            deferred.defer(grap_keywords, 'http://www.sitebro.net/%s/'%k, _name=str(abs(hash(k))))
        except:
            pass

    keywords = [urllib.unquote(k).decode('utf8').replace('+', ' ') for k in pages]
    keywords = [k.strip() for k in keywords]
    keywords = [k for k in keywords if k]

    # logging.debug(r.content)
    logging.info("url %s grep keywords %s, %s" % (url, len(keywords), keywords[:10]))

    if not keywords:
        return

    with rdbms.Connection('tagtoosql:tagtoo', 'tagtooads') as connect:
        cursor = connect.cursor()
        cursor.executemany('insert ignore into keywords(keyword) values (%s)', keywords)


class SitebroHandler(webapp2.RequestHandler):
    def get(self):
        deferred.defer(grap_keywords, 'http://www.sitebro.net/')

import random
import json

class SearchFarmAPI(webapp2.RequestHandler):
    def wrap_content(self, content, keyword):
        pos = [random.randint(0, len(content)) for k in range(10)]
        pos.sort()
        q = []
        j = 0
        for i in pos:
            q.append(content[j:i])
            j = i
        q.append(content[j:])
        return ("<strong>%s</strong>" % keyword).join(q)

    def get(self):
        keyword = self.request.get("keyword")

        with rdbms.Connection("tagtoosql:tagtoo", "tagtooaffiliate") as connect:
            cursor = connect.cursor()
            ids = [str(random.randint(16525, 42502)) for k in range(25)]
            cursor.execute('select link, title, content from nownews where id in (%s)' % (','.join(ids)))
            results = cursor.fetchall()

        self.response.out.write(json.dumps([{'link': k[0], 'title': k[1], 'content': self.wrap_content(k[2], keyword)} for k in results]))

class KeywordAPI(webapp2.RequestHandler):
    def get(self):
        import json
        offset = self.request.get_range("offset")

        with rdbms.Connection('tagtoosql:tagtoo', 'tagtooads') as connect:
            cursor = connect.cursor()
            cursor.execute('select keyword from keywords order by id limit 100 offset %s', offset)
            keywords = [k[0] for k in cursor.fetchall()]

        self.response.out.write(json.dumps(keywords))

app = webapp2.WSGIApplication([
    (r'/search_farm', SearchFarmAPI),
    (r'/sitebro', SitebroHandler),
    (r'/api', KeywordAPI),
])


