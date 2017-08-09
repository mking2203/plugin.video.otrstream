import mechanize, re, urllib, time
from BeautifulSoup import BeautifulSoup
import functions
import xbmc
import cookielib

class ItemClass(object):
    pass

def login(user, pw):
    
    x = ItemClass()
    
    # init browser
    br = mechanize.Browser()
    
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    
    br.set_handle_robots(False)

    br.open("http://www.onlinetvrecorder.com/v2/?go=home")

    # login
    br.select_form('fhomelogin')

    br['email'] = user
    br['password'] = pw
    
    br.submit().read()
    
    response = br.open('   ')
    result = response.read()  
    
    # now check state
    x.state = 'not loged in'
    x.id = ''
      
    # info on java scipt
    match = re.search('my_user_id="(?P<id>.*?)";.*?my_ut="(?P<state>.*?)"', result)
    if(match != None):
        x.id = match.group('id')
        x.state = match.group('state')
           
    x.decode = 'n.v.' 
        
    # info on html
    match = re.search('<a.href=".?go=history&tab=decodings(.*?)<\/i>(?P<value>[^<]*)<', result)
    if(match != None):
        x.decode = match.group('value')
            
    x.value = 'n.a.'
            
    match = re.search('<div.id="cssmenuright">.*?<a.href=".go=points.*?>(?P<value>[^<]*)<', result, re.DOTALL)
    if(match != None):
        x.value = match.group('value')
            
    return x
    
def loginCookie(user, pw, path):
    
    x = ItemClass()
    
    # init browser
    br = mechanize.Browser()
    
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    
    br.set_handle_robots(False)

    br.open("http://www.onlinetvrecorder.com/v2/?go=home")

    # login
    br.select_form('fhomelogin')

    br['email'] = user
    br['password'] = pw
    
    br.submit().read()
    
    response = br.open('   ')
    result = response.read()  
    
    cj.save(path, ignore_discard=True, ignore_expires=True)
    
    # now check state
    x.state = 'not loged in'
    x.id = ''
      
    # info on java scipt
    match = re.search('my_user_id="(?P<id>.*?)";.*?my_ut="(?P<state>.*?)"', result)
    if(match != None):
        x.id = match.group('id')
        x.state = match.group('state')
           
    x.decode = 'n.v.' 
        
    # info on html
    match = re.search('<a.href=".?go=history&tab=decodings(.*?)<\/i>(?P<value>[^<]*)<', result)
    if(match != None):
        x.decode = match.group('value')
            
    x.value = 'n.a.'
            
    match = re.search('<div.id="cssmenuright">.*?<a.href=".go=points.*?>(?P<value>[^<]*)<', result, re.DOTALL)
    if(match != None):
        x.value = match.group('value')
            
    return x

def getData(user, pw):

    itemlist = []
    
    # get HTML
    link = 'http://www.onlinetvrecorder.com/v2/?go=home'
    data = functions.getHTML(user, pw, link)    
 
    # logged in
    result = data.replace('\'','\"')
    soup = BeautifulSoup(result)

    # search for highlights
    
    tables = soup.findAll('div' , {'class' : 'content'} ) 
    
    for table in tables:
        # check its the right table
        taList = table.find('div' , {'class' : 'homedoublehighlight'})
        if taList is not None:

            x = ItemClass()
        
            taList = table.find('td')
            sStyle = taList['style'].encode()
             
            m = re.search('background-image:url\((?P<thumb>.*?)\)', sStyle)
            if(m is not None):
                x.thumb = m.group('thumb')
            else:
                x.thumb = 'DefaultVideo.png' 
        
            h1 = table.find('a')            
            x.url = h1['href']
            
            # we just want the id   
            s = x.url.index('id=')
            x.url = x.url[s+3:]
            
            sp = table.find('span')
            x.title = sp.text

            text1 = table.find('div' , {'class' : 'homedoublehighlight'} )
            x.text = text1.text
            
            x.vid = ''
            
            x.text = x.text.replace('|','\n')
            
            itemlist.append(x)

    # search for actual movies
    
    content = soup.findAll ('div' , {'class' : 'homethree'} )

    for c in content:
        
        x = ItemClass()
    
        link = c.find('a', {'class' : 'homethreehredbig'} )
        if link is None:
            break
        
        x.url = link['href']
        
        # we just want the id   
        s = x.url.index('id=')
        x.url = x.url[s+3:]

        title = c.find('div' , {'class' : 'toolbardiv'} )
        x.title = title.text
    
        data = c.findAll('div', {'class' : 'homethreee'} )

        x.thumb = 'DefaultVideo.png' 
        x.vid = ''

        for e in data:
            img = e.find('img')
            if img is not None:
                x.thumb = img['src']
            else:
                sty = e['style']
                m = re.search('background-image:url\((?P<thumb>.*?)\)', sty)
                if(m is not None):
                    x.thumb = m.group('thumb')

            vid = e.find('video')
            if vid is not None:
                x.vid = vid['src']
    
        desc = c.find('div' , {'class' : 'homethreec'} )
        x.text = desc.text
        
        x.text = x.text.replace('|','\n')
        
        itemlist.append(x)    
    
    return itemlist
    
def getMoreData(user, pw, page):

    # page 1 display page without big highlights
    
    itemlist = []

    # init browser
    br = mechanize.Browser()
    br.set_handle_robots(False)

    br.open("http://www.onlinetvrecorder.com/v2/?go=home")

    # login
    br.select_form('fhomelogin')

    br['email'] = user
    br['password'] = pw
    br.submit().read()
    
    select = 0 # -2 returns also the highlights
    
    if(page == 2):
        select = 14
    if(page > 2):
        select = (15 * (page-1)) - 1
        
    params = {u'language': 'de', u'start': str(select)}
    data = urllib.urlencode(params)

    response = br.open("http://www.onlinetvrecorder.com/v2/ajax/get_homethree.php",  data)
    result = response.read() 

    # logged in

    result = result.replace('\'','\"')
    soup = BeautifulSoup(result)

    # search for actual movies

    content = soup.findAll ('div' , {'class' : 'homethree'} )

    for c in content:
        
        x = ItemClass()
    
        link = c.find('a', {'class' : 'homethreehredbig'} )
        if link is None:
            break
        
        x.url = link['href']
        
        # we just want the id   
        s = x.url.index('id=')
        x.url = x.url[s+3:]

        title = c.find('div' , {'class' : 'toolbardiv'} )
        x.title = title.text
    
        data = c.findAll('div', {'class' : 'homethreee'} )

        x.thumb = 'DefaultVideo.png' 

        for e in data:
            img = e.find('img')
            if img is not None:
                x.thumb = img['src']
            else:
                sty = e['style']
                m = re.search('background-image:url\((?P<thumb>.*?)\)', sty)
                if(m is not None):
                    x.thumb = m.group('thumb')
               
            vid = e.find('video')
            if vid is not None:
                x.vid = vid['src']
    
        desc = c.find('div' , {'class' : 'homethreec'} )
        x.text = desc.text
        
        itemlist.append(x)    
    
    return itemlist
    
def getMovies(user, pw, epg_id):

    itemlist = []

    # get HTML
    link = 'http://www.onlinetvrecorder.com/v2/?go=download&epg_id=' + epg_id 
    data = functions.getHTML(user, pw, link)    
    
    result = data.replace('\'','\"')
    
    # search the title & text
    title = '?'
    match = re.search('<div.style="color:#FFF;.*?font-size:20px;([^>]*)>(?P<txt>[^>]*)<', result, re.DOTALL)
    if(match is not None):
        title = match.group('txt').strip()

    desc = '...'
    #match = re.search('<div.style="height:215px;.overflow:auto([^>]*)>(?P<txt>[^>]*)<', result, re.DOTALL)
    match = re.search('currentepgtext[^>]*>(?P<txt>.*?)<.span>', result, re.DOTALL)
    if(match is not None):
        desc = match.group('txt').strip().replace('<br>','\n')
    
    #get stars
    stars = 0   
    regex = 'font-size:21px; color:#FFCA00;'
    for m in re.finditer(regex, result, re.DOTALL):
        stars += 1   

    # search picture   
    thumb = 'DefaultVideo.png' 

    match = re.search('<div.id="quickbigimage.*?src="(?P<thumb>[^"]*)"', result)
    if(match != None):
        thumb = match.group('thumb')
    
    match = re.search('<div.id="quickbigimage.*?background-image:url.(?P<thumb>[^)]*)', result)
    if(match != None):
        thumb = match.group('thumb')

    # search preview video
    
    match = re.search('<video.id="previewvideo[^>]*>.*?<source.src="(?P<url>[^"]*)"', result, re.DOTALL)
    if(match != None):
        x = ItemClass()
        x.url = match.group('url')
        x.title = "Preview"
        x.price = "0,00 Cent"
        x.thumb = thumb
        x.desc = desc
        x.stars = stars
        
        itemlist.append(x)
    
    # search video page  
                   
    regex = '<input.type=button.class=epgscreengreenbutton[^>]*startEpgScreenStream\((?P<url>[^)]*)\);".value="(?P<q>.*?)">.*?<td.style=[^>]*>(?P<price>[^<]*)<'
    
    for m in re.finditer(regex, result, re.DOTALL): 
        
        test = m.group('q')
        test = test.replace('&raquo;','')
                        
        x = ItemClass()
            
        x.url = m.group('url')
        x.title = test
        x.price = m.group('price')
        x.thumb = thumb
        x.desc = desc
        x.stars = stars
            
        itemlist.append(x)  
            
    return itemlist    
        
def search(user, pw, keyword, page):
           
    link = functions.getSearchString(keyword, page)
    data = functions.getHTML(user, pw, link)
    
    # now parse
    return functions.scanList(data)

def searchStation(user, pw, keyword, station, date, page):
           
    link = functions.getSearchStationString(keyword, station, date, page)
    data = functions.getHTML(user, pw, link)
          
    # now parse
    return functions.scanList(data)

def searchGroup(user, pw, group, page):
    
    link = functions.getGroupString(group, page)
    data = functions.getPostHTML(user, pw, link)
    
    # now parse
    return functions.scanList(data)

def getRecords(user, pw, page):
    
    # get HTML
    link = functions.getRecordsString(page)
    data = functions.getHTML(user, pw, link)
    
    # now parse
    return functions.scanList(data)




