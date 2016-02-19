# Search-Engine
A Basic Search Engine implemented in Python
The search engine has the basic functionality of crawling the web pages, reachable through the seed url and the crawled pages are indexed into the database using sqlite3. The keywords thus indexed can be quereyed through the commannds. The search capabilities are limited to a keyword search. The pages are then ranked according to various algorithm. Neural nets are also used to result better query results.

# To Crawl the particular sites:

Edit the crawl.py and change the seed url and the depth.


# To query the index:

In the command prompt 

import searchengine
e = searchengine.searcher('searchindex.db')
print e.query('<your keyword>')


