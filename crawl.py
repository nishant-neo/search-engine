import searchengine

#The following two lines are to create the database schema
#Uncomment the lines to define a new schema
crawler = searchengine.crawler("searchindex.db")
#crawler.createindextables()


#this list contains the seed url(s)
pages = ["http://gbpuat.ac.in/"]
depth = 2
crawler.crawl(pages , depth)