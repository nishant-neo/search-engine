# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      TRINITI
#
# Created:     27-01-2015
# Copyright:   (c) TRINITI 2015
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from sqlite3 import dbapi2 as sqlite

ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


class crawler:
    # Create a list of words to ignore

    def __init__(self, dbname):
        self.con = sqlite.connect(dbname, timeout=10)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # Add a link between two pages
    def addlinkref(self, urlFrom, urlTo, linkText):
        pass

    # Starting with a list of pages, do a BFS to a given depth, indexing pages as we go
    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print "Could not open %s" % page
                    continue
                try:
                    soup = BeautifulSoup(c.read())
                except:
                    continue
                self.addtoindex(page, soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]  # remove location portion
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)

                self.dbcommit()
            pages = newpages

    # Create the database tables
    def createindextables(self):
        self.con.execute('CREATE TABLE urllist(url)')
        self.con.execute('CREATE TABLE wordlist(word)')
        self.con.execute('CREATE TABLE wordlocation(urlid,wordid,location)')
        self.con.execute('CREATE TABLE link(fromid INTEGER,toid INTEGER)')
        self.con.execute('CREATE TABLE linkwords(wordid,linkid)')
        self.con.execute('CREATE INDEX wordidx ON wordlist(word)')
        self.con.execute('CREATE INDEX urlidx ON urllist(url)')
        self.con.execute('CREATE INDEX wordurlidx ON wordlocation(wordid)')
        self.con.execute('CREATE INDEX urltoidx ON link(toid)')
        self.con.execute('CREATE INDEX urlfromidx ON link(fromid)')
        self.dbcommit()

    # Extract text from an HTML page
    def gettextonly(self, soup):
        v = soup.string
        if v == None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    # separate the words by any non space whitespace character
    def separatewords(self, text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '']

    # Index an individual page
    def addtoindex(self, url, soup):
        if self.isindexed(url):
            return
        print('indexing' + url)
        # get the individual words
        text = self.gettextonly(soup)
        words = self.separatewords(text)
        # get the url id
        urlid = self.getentryid('urllist', 'url', url)
        # link each woed to this url
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) values(%d,%d,%d)" % (urlid, wordid, i))

    # Auxilliary function for getting an entry id and adding
    # if it's not present
    def getentryid(self, table, field, value, createnew=True):
        cur = self.con.execute("select rowid from %s where %s= '%s'" % (table, field, value))
        res = cur.fetchone()
        if res == None:
            cur = self.con.execute("insert into %s (%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    # return true if this link is already indexed
    def isindexed(self, url):
        u = self.con.execute("select rowid from urllist where url='%s'" % url).fetchone()
        if u != None:
            # check if it has actually been crawled
            v = self.con.execute('select * from wordlocation where urlid=%d' % u[0]).fetchone()
            if v != None:
                return True
            return False


class searcher:

    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def getmatchrows(self, q):
        # Strings to build the query
        fieldlist = 'w0.urlid'
        tablelist = ''
        clauselist = ''
        wordids = []

        # Split the words by spaces
        words = q.split(' ')
        tablenumber = 0

        for word in words:
            # Get the word ID
            wordrow = self.con.execute("select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow != None:
                wordid = wordrow[0]
                wordids.append(wordid)
                if tablenumber > 0:
                    tablelist += ','
                    clauselist += ' and '
                    clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber - 1, tablenumber)
                fieldlist += ',w%d.location' % tablenumber
                tablelist += 'wordlocation w%d' % tablenumber
                clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
                tablenumber += 1

        # Craete the query from separate parts
        fullquery = 'select %s from %s where %s' % (fieldlist, tablelist, clauselist)
        cur = self.con.execute(fullquery)
        rows = [row for row in cur]

        return rows, wordids

    def getscoredlist(self, rows, wordids):
        totalscores = dict([(row[0], 0) for row in rows ])

        weights = []
        for( weight, scores ) in weights:
            for url in totalscores:
                totalscores[url] += weight *scores[url]
        return totalscores

    def geturlname(self, id):
        return self.con.execute("select url from urllist where rowid = %d" %id).fetchone()[0]

    def query(self, q):
        rows, wordids = self.getmatchrows( q)
        scores = self.getscoredlist(rows, wordids)
        rankedscores = sorted([(score, url) for (url,score) in scores.items()], reverse=1)
        for( score, urlid) in rankedscores[0:10]:
            print '%f\t%s' % (score,self.geturlname(urlid))


