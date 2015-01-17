import requests
import sys
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv

driver = webdriver.Firefox()
base_facebook = "https://graph.facebook.com/v1.0/"

infile = open('urls.csv', 'r')
urls = []
for row in infile:
  dom = row.split("\n")[0]
  urls.append(dom)


#urls = ["http://fivethirtyeight.com/datalab/everything-steven-soderbergh-watched-and-read-in-2014/","http://fivethirtyeight.com/datalab/chris-christie-2016-president-republican-primary-overrated/","http://fivethirtyeight.com/datalab/13-nba-teams-have-benches-better-than-the-knicks/","http://fivethirtyeight.com/features/how-much-fuel-we-need-to-leave-buried-to-beat-climate-change/", "http://fivethirtyeight.com/datalab/chris-christie-2016-president-republican-primary-overrated/"]

def fte_fetch_comments(url):

  driver.get(url)
  elem = driver.find_elements_by_class_name("fte-expandable-title")[-1]
  elem2 = driver.find_element_by_class_name("entry-comments-content")
  author = driver.find_element_by_class_name("author")
  title = driver.find_element_by_class_name("article-title")


  author = author.text
  title = title.text

  elem.click()
  elem2.click()

  source = driver.page_source
  index = source.find("iframe id=\"")
  idstring = source[index:index+30]
  spl = idstring.split("\"")
  fid = spl[1]
  
  driver.switch_to.frame(fid)
  
  comments = driver.find_elements_by_class_name("postText")
  commenters = driver.find_elements_by_class_name("profileName")
  posts = driver.find_elements_by_class_name("postContainer")
  locations = [post.find_elements_by_class_name("fsm")[0] for post in posts]


  morec = True
  while morec:
    try:
      morec = driver.find_element_by_class_name("pam")
      morec.click()
      time.sleep(1)
  
      comments = driver.find_elements_by_class_name("postText")
      commenters = driver.find_elements_by_class_name("profileName")

    except:
      comments = driver.find_elements_by_class_name("postText")
      commenters = driver.find_elements_by_class_name("profileName")
      posts = driver.find_elements_by_class_name("postContainer")
      locations = [post.find_elements_by_class_name("fsm")[0] for post in posts]
      return comments, commenters, locations, author, title

  return comments, commenters, locations, author, titles

def print_coms(comments, commenters, locations, author, title):

  coms = []
  ppl = []
  authors = []
  titles = []
  locs = []

  author = author.encode("ascii", "ignore")
  title = title.encode("ascii", "ignore")

  for com in comments:
    text = com.text
    print text
    coms.append(text)
    authors.append(author)
    titles.append(title)

  for com in commenters:
    per = com.get_attribute("href")
    print per
    ppl.append(per)

  for location in locations:
    loc = location.text.encode("ascii","ignore")
    if " at " in loc:
      loc = loc.split(" at ")[1].strip()
      
    elif "menter " in loc:
      loc = loc.split("menter ")[1].strip()
    
    else:
      loc = loc.strip()

    locs.append(loc)


  zipped = (zip(coms, ppl, locs, authors, titles))
  print zipped

  return zipped 

def setup(outfile):
  try:
    f = open(outfile, "a")
    writer = csv.writer(f)
    writer.writerow(("full_name", "gender", "facebook_id", "article_url", "author", "article_title", "comment"))
    f.close()

  except:
    print "IOError"

def write_coms(zipped, url, outfile):
  names = []
  text = []
  f = open(outfile, "a")
  writer = csv.writer(f)


  for fid, com, loc, auth, title in zipped:
    try:
      if len(fid) > 100:
        continue

      fid = fid.split("/")[-1]
    
    except:
      continue


    fb_url = base_facebook + fid
     
    try:
      fbinfo = requests.get(fb_url).json()    
      print fbinfo
      comwrite = str(com).rstrip("\n")      
      tup = (fbinfo["name"],fbinfo["gender"],loc,fid,url,auth,title,comwrite)
      if len(tup) < 4:
        continue
 
      writer.writerow(tup)
    

    except:
      print "Error", sys.exc_info()[0]

    f.flush()

def sample(fname):

  for url in urls:
    try: 
      c, cs, locs, auth, title = fte_fetch_comments(url)
      zi = print_coms(c, cs, locs, auth, title) 
      write_coms(zi, url, fname)
      print len(c)
      print len(cs)

    except:
      continue

if __name__ == "__main__":

  fname = sys.argv[1]
  setup(fname)
  sample(fname)
