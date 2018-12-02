# coding=utf-8

'''
Created on 27.04.2017

@author: Mark König
'''

import mechanize, re
from BeautifulSoup import BeautifulSoup
import time, os, datetime
import urllib, cookielib
import searchStrings
import xbmc
import requests

class ItemClass(object):
    pass

def deleteCookie(cookiePath):

    try:
        if os.path.isfile(cookiePath):
            os.unlink(cookiePath)
    except Exception as e:
        print ("BROWSER " + str(e))

def checkCookie(cookiePath):

    date = datetime.datetime.now() - datetime.timedelta(minutes = 20)
    ts = time.mktime(date.timetuple())

    if(os.path.exists(cookiePath)):
        fileDate = os.path.getmtime(cookiePath)
        if(ts>fileDate):
            deleteCookie(cookiePath)
            return False
        else:
            return True

    return False

def login(user, pw, cookiePath):

    br = mechanize.Browser()

    cj = cookielib.LWPCookieJar()

    br.set_cookiejar(cj)
    br.set_handle_robots(False)

    br.open("https://www.onlinetvrecorder.com/v2/?go=home")

    # login form
    br.select_form('fhomelogin')

    br['email'] = user
    br['password'] = pw

    result = br.submit().read()

    em = ''
    pw = ''

    # get user and pw and set cookies
    m = re.search('otr_email=(.*?);', result)
    if(m != None):
        em = m.group(1)
    m = re.search('otr_password=(.*?);', result)
    if(m != None):
        pw = m.group(1)

    date = datetime.datetime.now()
    ts = time.mktime(date.timetuple())
    ts = ts + 86400

    c = cookielib.Cookie(version=0, name='otr_email', value=em, port=None, port_specified=False, domain='onlinetvrecorder.com',
                         domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
                         secure=False, expires=ts, discard=True, comment=None, comment_url=None,
                         rest={'HttpOnly': None}, rfc2109=False)
    cj.set_cookie(c)
    c = cookielib.Cookie(version=0, name='otr_email', value=em, port=None, port_specified=False, domain='www.onlinetvrecorder.com',
                         domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
                         secure=False, expires=ts, discard=True, comment=None, comment_url=None,
                         rest={'HttpOnly': None}, rfc2109=False)
    cj.set_cookie(c)

    c = cookielib.Cookie(version=0, name='otr_password', value=pw, port=None, port_specified=False, domain='onlinetvrecorder.com',
                         domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
                         secure=False, expires=ts, discard=True, comment=None, comment_url=None,
                         rest={'HttpOnly': None}, rfc2109=False)
    cj.set_cookie(c)
    c = cookielib.Cookie(version=0, name='otr_password', value=pw, port=None, port_specified=False, domain='www.onlinetvrecorder.com',
                         domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
                         secure=False, expires=ts, discard=True, comment=None, comment_url=None,
                         rest={'HttpOnly': None}, rfc2109=False)
    cj.set_cookie(c)


    #now reload
    response = br.reload();
    result = response.read()

    x = ItemClass()
    x.state = 'not loged in'
    x.id = '0'
    x.decode = '0'
    x.value = '0'

    # info fron website
    match = re.search('my_user_id="(?P<id>.*?)";.*?my_ut="(?P<state>.*?)"', result)
    if(match != None):
        if(match.group('state')!= ''):
            cj.save(cookiePath, ignore_discard=True, ignore_expires=True)

            x.id = match.group('id')
            x.state = match.group('state').title()

        match = re.search('<a.href=".?go=history&tab=decodings(.*?)<\/i>(?P<value>[^<]*)<', result)
        if(match != None):
            x.decode = match.group('value')

        match = re.search('<div.id="cssmenuright">.*?<a.href=".go=points.*?>(?P<value>[^<]*)<', result, re.DOTALL)
        if(match != None):
            x.value = match.group('value')

    return x

def getData(user, pw, cookiePath):

    itemlist = []

    link = 'https://www.onlinetvrecorder.com/v2/?go=home'
    result = getHTML(user, pw, cookiePath, link)

    data = result.replace('\'','\"')
    return scanData(data)

def getMoreData(user, pw, cookiePath, page):

    br = mechanize.Browser()

    cj = cookielib.LWPCookieJar()
    cj.load(cookiePath, ignore_discard=True, ignore_expires=True)

    br.set_cookiejar(cj)
    br.set_handle_robots(False)

    select = -1

    if(page == 2):
        select = 14
    if(page > 2):
        select = (15 * (page-1)) - 1

    params = {u'language': 'de', u'start': str(select)}
    data = urllib.urlencode(params)

    response = br.open("https://www.onlinetvrecorder.com/v2/ajax/get_homethree.php",  data)
    result = response.read()

    result = result.replace('\'','\"')
    return scanData(result)

def getDecoding(url, params, cookiePath):

    br = mechanize.Browser()

    cj = cookielib.LWPCookieJar()
    cj.load(cookiePath, ignore_discard=True, ignore_expires=True)

    br.set_cookiejar(cj)
    br.set_handle_robots(False)

    data = urllib.urlencode(params)

    response = br.open(url,  data)
    result = response.read()

    result = result.replace('\'','\"')
    return result

def getHTML(user, pw, cookiePath, link):

    br = mechanize.Browser()

    cj = cookielib.LWPCookieJar()
    cj.load(cookiePath, ignore_discard=True, ignore_expires=True)

    br.set_cookiejar(cj)
    br.set_handle_robots(False)

    response = br.open(link, timeout=30)
    result = response.read()

    return result

def getAlternateHTML(cookiePath, link):

    cj = cookielib.LWPCookieJar()
    cj.load(cookiePath, ignore_discard=True, ignore_expires=True)

    resp = requests.post(link, None, None, cookies=cj, timeout=30)

    return resp.text

def getPostHTML(user, pw, cookiePath, link):

    cj = cookielib.LWPCookieJar()
    cj.load(cookiePath, ignore_discard=True, ignore_expires=True)

    result = None

    try:
        request = mechanize.Request(link, None, None, cookies=cj, timeout=30)
        response = mechanize.urlopen(request)
        result = response.read()
    except:
        pass

    return result

def getOnlineMovie(cookiePath, link, wid , cs ):

    cj = cookielib.LWPCookieJar()
    cj.load(cookiePath, ignore_discard=True, ignore_expires=True)

    data = {'wid': wid, 'cs': cs,}

    resp = requests.post(link, data=data, cookies=cj, timeout=30)
    return resp.text

def scanData(html):

    soup = BeautifulSoup(html)
    itemlist = []

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
            x.text = x.text.replace('|',' ')
            x.vid = ''

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
        x.text = x.text.replace('|',' ')

        match = re.search('[^\d+\W+].*', x.text)
        if(match is not None):
            x.text = match.group(0)

        itemlist.append(x)

    return itemlist

def scanList(data):

    itemlist = []

    soup = BeautifulSoup(data.decode('utf-8', 'ignore'))
    content = soup.findAll ('tr', id=lambda x: x and x.startswith('serchrow'))

    for c in content:

        x = ItemClass()

        inp = c.find('input', { 'type' : 'hidden'})
        x.id = inp['value']

        title = c.find('p' , id=lambda x: x and x.startswith('ptitleandtext'))
        x.title = title.find(text=True).strip()
        #new 05.07.
        if (len(x.title) == 0):
            title = c.find('a')
            x.title = title.text

        x.desc = ''
        desc = c.find('span' , id=lambda x: x and x.startswith('spanlongtext'))
        if not (desc is None):
            x.desc = desc.text
            x.desc = x.desc.replace('|',' ')

        x.thumb = 'DefaultVideo.png'
        pict = c.find('td' , id=lambda x: x and x.startswith('listimagetd'))
        if not (pict is None):
            pic = pict.find('img')
            if not (pic is None):
                x.thumb = pic['src']

        x.genre = ''
        genre = c.find('p' , style=lambda x: x and x.startswith('text-transform:capitalize'))
        if not(genre is None):
            x.genre = genre.text

        data = c.findAll('td' , oncontextmenu=lambda x: x and x.startswith('showNewTabMenu'))
        start = ''
        stop = ''

        x.serie = ''
        x.episode = ''
        x.date = ''
        x.time = ''

        for d in data:
            tmp = d.text

            if len(tmp) == 3:
                if(tmp[0] == 'S'):
                    ser = tmp[1:]
                    if(ser.isdigit()):
                        x.serie = ser
                if(tmp[0] == 'E'):
                    ep = tmp[1:]
                    if(ep.isdigit()):
                        x.episode = ep
            if len(tmp) == 8:
                x.date = tmp
            if len(tmp) == 5:
                if(start == ''):
                    start = tmp
                    x.time = tmp
                else:
                    stop = tmp

        itemlist.append(x)

    return itemlist

def getMovies(user, pw, cookiePath, epg_id):

    itemlist = []

    # get HTML
    link = 'https://www.onlinetvrecorder.com/v2/?go=download&epg_id=' + epg_id
    data = getHTML(user, pw, cookiePath, link)

    result = data.replace('\'','\"')

    # search the title & text
    title = '?'
    #match = re.search('<div.style="color:#FFF;.*?font-size:20px;([^>]*)>(?P<txt>[^>]*)<', result, re.DOTALL)
    #if(match is not None):
    #    title = match.group('txt').strip()
    match = re.search('document.title="(.*?)"', result)
    title = match.group(1)

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
        x.desc = title + '\n' + desc
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
        x.desc = title + '\n' + desc
        x.stars = stars

        itemlist.append(x)

    # search prev / next video

    regex = 'nextRecordingScreen\((.*?)\)'

    matches = re.findall(regex, result)
    if (matches is not None):
        for match in matches:
            values = match.split(',')
            beginn = values[4].replace('"','')
            cs  = values[5].replace('"','')
            direction = values[6].replace('"','')
            sender = values[3].replace('"','').replace(' ','%20')

            url = 'https://www.onlinetvrecorder.com/v2/ajax/nextrecording.php'
            url = url + '?beginn=' + beginn
            url = url + '&cs=' + cs
            url = url + '&dir=' + direction
            url = url + '&sender=' + sender

            link = getPostHTML(user, pw, cookiePath, url)

            if(link is not None):
                x = ItemClass()

                x.url = link
                x.title = direction
                x.price = "0,00 Cent"
                x.thumb = ''
                x.desc = ''
                x.stars = 0

                itemlist.append(x)

    return itemlist

def getScreenshots(user, pw, cookiePath, epg_id):

    itemlist = []

    # get HTML
    link = 'https://www.onlinetvrecorder.com/v2/?go=download&epg_id=' + epg_id
    data = getHTML(user, pw, cookiePath, link)

    regex = '<center>Screenshot.*?img.src=(?P<url>.*?).width'

    cnt =1
    for m in re.finditer(regex, data, re.DOTALL):

        x = ItemClass()

        x.url = m.group('url')
        x.title = str(cnt)
        cnt = cnt + 1

        itemlist.append(x)

    return itemlist

def search(user, pw, cookiePath, keyword, page, de):

    link = searchStrings.getSearchString(keyword, page, de)
    data = getPostHTML(user, pw, cookiePath, link)

    # now parse
    return scanList(data)

def searchStation(user, pw, cookiePath, keyword, station, date, page):

    link = searchStrings.getSearchStationString(keyword, station, date, page)
    data = getPostHTML(user, pw, cookiePath, link)

    # now parse
    return scanList(data)

def searchGroup(user, pw, cookiePath, group, page):

    link = searchStrings.getGroupString(group, page)
    data = getPostHTML(user, pw, cookiePath, link)

    # now parse
    return scanList(data)

def getRecords(user, pw, cookiePath, page):

    # get HTML
    link = searchStrings.getRecordsString(page)
    data = getHTML(user, pw, cookiePath, link)

    # now parse
    return scanList(data)

def getList(user, pw, cookiePath, no, page):

    # calculate start
    iPage = int(page)
    x = (iPage - 1) * 20

    # get HTML
    link = "https://www.onlinetvrecorder.com/v2/?go=list&tab=toplist&listid=" +  no + "&start=" + str(x)
    data = getPostHTML(user, pw, cookiePath, link)

    # now parse
    return scanList(data)

def getPlayLink(user, pw, cookiePath, eid, rid, mode):

    br = mechanize.Browser()

    cj = cookielib.LWPCookieJar()
    cj.load(cookiePath, ignore_discard=True, ignore_expires=True)

    br.set_cookiejar(cj)
    br.set_handle_robots(False)

    params = {u'eid': eid, u'rid': rid, u'mode': mode}
    data = urllib.urlencode(params)

    try:
        response = br.open("https://www.onlinetvrecorder.com/v2/ajax/start_epg_screen_stream.php",  data)
        result = response.read()

        q = result[:2]
        if(q == 'OK'):
            # result is OK
            url = result[3:]

            if mode <> 'normal':
                t = url.replace('player.php?','')
                t = t.replace('www.onlinetvrecorder.com/v2/downloadserverredirect/?url=','')
                return t
            else:
                response = br.open(url)
                result = response.read()

                m = re.search('source.src="(?P<url>[^"]*)"', result)
                if m is not None:
                    t = m.group('url')
                    return t

                m = re.search('init_player."(?P<url>[^"]*)"', result)
                if m is not None:
                    t = m.group('url')
                    return t

                # new 04.03.2018 // redirect
                m = re.search('location.href="(?P<url>[^"]*)"', result)
                if m is not None:
                    url = m.group('url')
                    response = br.open(url)
                    result = response.read()

                    m = re.search('init_player."(?P<url>[^"]*)"', result)
                    if m is not None:
                        t = m.group('url')
                        return t

        else:
            return None

    except mechanize.HTTPError as e:
        print e.code
        return 'ERROR ' + str(e.code)
    except mechanize.URLError as e:
        return 'ERROR ' + str(e.reason.args)

def getDecode(user, pw, cookiePath):

    itemlist = []

    link = 'https://www.onlinetvrecorder.com/v2/?go=history&tab=decodings'
    result = getAlternateHTML(cookiePath, link)

    result = result.replace('\'','\"')
    regex = 'loadDecodingTable\("(?P<c>.*?)","(?P<t>.*?)","(?P<x>.*?)","(.*?)","(?P<cs>.*?)","(.*?)"\);'

    cnt = 0

    for m in re.finditer(regex, result, re.DOTALL):

        url = 'https://www.onlinetvrecorder.com/v2/ajax/get_decoding_history.php'
        params = {u'c': m.group('c').replace('=','') , u't': m.group('t') , u'x': m.group('x') , u'cs': m.group('cs')}

        table = getDecoding(url, params, cookiePath)
        regex = '<td.id="userhistorydecoding_decoding_tracking.*?>(?P<title>.*?)<'

        for m in re.finditer(regex, table, re.DOTALL):
            data = m.group('title')
            srch = time.strftime(' %y.')
            pos = data.find(srch)

            if(pos > 0):
                x = ItemClass()
                x.thumb = 'DefaultVideo.png'

                x.title = data
                x.search = data[:pos].strip()

                itemlist.append(x)

        cnt = cnt + 1
        if(cnt == 2):
            return itemlist

    return itemlist

def getPage(user, pw, cookiePath, URL):

    result = getHTML(user, pw, cookiePath, URL)
    return result
