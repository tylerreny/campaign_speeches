####
# Election campaign speech scraper
####

'''This scraper collects campaign remarks from all candidates from 
the 2016, 2012, and 2008 elections from the UCSB American Presidency Project
website http://www.presidency.ucsb.edu/2016_election.php'''

from lxml.cssselect import CSSSelector
import lxml.html
import csv
import unidecode

def get_speech_urls(year):
    
    #get candidates
    url = "http://www.presidency.ucsb.edu/{}_election.php".format(year)
    r = requests.get(url)
    tree = lxml.html.fromstring(r.text)
    sel = CSSSelector("a")
    res = sel(tree)
    lnks = [x.get('href') for x in res]
    
    #find just candidate speech links
    save = []
    for link in lnks:
        if re.findall('election_speeches',link) and re.findall('5000',link) or re.findall('1150',link):
            save.append(link)
        else:
            pass
            
    #subset to just campaign remarks        
    ids = []
    for link in save:
        url = 'http://www.presidency.ucsb.edu/' + link
        r = requests.get(url)
        id2 = re.findall("pid=([0-9]+)\">Remarks",r.text)
        ids.append(id2)
        
    #flatten list of urls and append to proper baseurl
    allid = [item for sublist in ids for item in sublist]
    urlout = []
    for id in allid:
        urls = "http://www.presidency.ucsb.edu/ws/index.php?pid={}".format(id)
        urlout.append(urls)
    return urlout
    


def scrape_pres_speeches(filename,year):
    
    #fetch urls for year
    urls = get_speech_urls(year)
    
    #open csv
    file = open(filename,'w')
    writer=csv.writer(file, delimiter=",", quoting=csv.QUOTE_ALL)
    writer.writerow(['candidate','date','speechtitle','text'])

    #parse each page
    i = 1
    for x in urls:
        r = requests.get(x)
        tree=lxml.html.fromstring(r.text)
        date=tree.xpath("//span[@class='docdate']")
        date=date[0].text_content()
        candidate=tree.xpath("//span[@class='ver10'][2]")
        candidate=unidecode.unidecode(candidate[0].text_content().replace(": ",""))
        speechtitle=tree.xpath("//span[@class='paperstitle']")
        speechtitle=unidecode.unidecode(speechtitle[0].text_content())
        text = tree.xpath("//span[@class='displaytext']")
        text = unidecode.unidecode(text[0].text_content()).replace("\n"," ").replace("\r","")
        print x,i+1
        writer.writerow([candidate,date,speechtitle,text])
    
scrape_pres_speeches('pres_campaign_speeches_2016.csv',2016)
scrape_pres_speeches('pres_campaign_speeches_2012.csv',2012)
scrape_pres_speeches('pres_campaign_speeches_2008.csv',2008)
