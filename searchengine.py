#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      TRINITI
#
# Created:     27-01-2015
# Copyright:   (c) TRINITI 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from sqlite3 import dbapi2 as sqlite

class crawler:
#Create a list of words to ignore
    ignorewords=set(['the','of','to','and','a','in','is','it'])
    def __init__(self,dbname):
        self.con=sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def crawl(self,pages,depth=2):
        for i in range(depth):
            newpages=set()
            for page in pages:
                try:
                    c=urllib2.urlopen(page)
                except:
               # print "Could not open %s" %page
                    continue
                soup=BeautifulSoup(c.read())
                self.addtoindex(page,soup)

                links=soup('a')
                for link in links:
                    if('href' in dict(link.attrs)):
                        url=urljoin(page,link['href'])
                        if url.find("'")!=-1:
                            countinue
                        url=url.split('#')[0]  #remove location portion
                        if url[0:4]=='http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText=self.gettextonly(link)
                        self.addlinkref(page,url,linkText)

                self.dbcommit()
            pages=newpages

    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer,toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index wordidx ON wordlist(word)')
        self.con.execute('create index urlidx ON urllist(url)')
        self.con.execute('create index wordurlidx ON wordlocation(wordid)')
        self.con.execute('create index urltoidx ON link(toid)')
        self.con.execute('create index urlfromidx ON link(fromid)')
        self.dbcommit()

    def gettextonly(self,soup):
        v=soup.string
        if v==None:
            c=soup.contents
            resulttext=''
            for t in c:
                subtext=self.gettextonly(t)
                resulttext+=subtext+'\n'
            return resulttext
        else:
            return v.strip()

    def separatewords(self,text):
        splitter=re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']

    def addtoindex(self,url,soup):
        if self.isindexed(url):
            return
        print('indexing'+url)
        #get the individual words
        text=self.gettextonly(soup)
        words=self.separatewords(text)
        #get the url id
        urlid=self.getentryid('urllist','url',url)
        #link each woed to this url
        for i in range(len(words)):
            word=words[i]
            if word in ignorewords:
                continue
            wordid=self.getentryid('wordlist','word',word)
            self.con.execute("insert into wordlocation(urlid,wordid,location values(%d,%d,%d"%(urlid,wordid,i))

    def getentryid(self,table,field,value,createnew=True):
        cur=self.con.execute("select rowid from %s where %s= '%s'" % (table,field,value))
        res=cur.fetchone()
        if res==None:
            cur=self.con.execute("insert into %s (%s) values ('%s')" %(table,field,value))
            return cur.lastrowid
        else:
            return res[0]

    def isindexed(self,url):
        u=self.con.execute("select rowid from urllist where url='%s'" %url).fetchone()
        if u!=None:
            #check if it has actually been crawled
            vars=self.con.execute('select * from wordlocation where urlid=%d' % u[0]).fetchone()
            if v!=None:
                return True
            return False


class searcher:
	def __init__(self):
		self.con=sqlite.connect(dbname)
		
	def __del__(self):
		self.con.close()
		
	def getmatchrows(self,q):
		#Strings to build the query
		fieldlist='w0.urlid'
		tablelist=''
		clauselist=''
		wordids=[]
		
		#Split the words by spaces
		words=q.split('')
		tablenumber=0
		
		for word in words:
			#Get the word ID
			wordrow=self.con.execute("select rowid from wordlist where word='%s'" %word).fetchone()
			if wordrow!=None:
				wordid=wordrow[0]
				wordids.append(wordid)
				if tablenumber>0:
					tablelist+=','
					clauselist+=' and '
					clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
				fieldlist+=',w%d.location' %tablenumber
				tablelist+='wordlocation w%d' %tablenumber
				clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
				tablenumber+=1
				
		#Craete the query from separate parts
		fullquery='select %s from %s where %s' %(fieldlist,tablelist,clauselist)
		cur=self.con.execute(fullquery)
		rows=[row for row in cur]
		
		return rows,wordids
		
			
	
	


















