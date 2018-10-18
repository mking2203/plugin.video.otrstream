import mechanize, re
from BeautifulSoup import BeautifulSoup
from datetime import date

class ItemClass(object):
    pass

def getHTML(user, pw, link):

    # init browser
    br = mechanize.Browser()
    br.set_handle_robots(False)

    br.open("https://www.onlinetvrecorder.com/v2/?go=home")

    # login
    br.select_form('fhomelogin')

    br['email'] = user
    br['password'] = pw
    br.submit().read()

    response = br.open(link)
    result = response.read()

    return result

def getPostHTML(user, pw, link):

    # init browser
    br = mechanize.Browser()
    br.set_handle_robots(False)

    br.open("https://www.onlinetvrecorder.com/v2/?go=home")

    # login
    br.select_form('fhomelogin')

    br['email'] = user
    br['password'] = pw
    br.submit().read()

    response = br.open(link)
    result = response.read()

    return result

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

        desc = c.find('span' , id=lambda x: x and x.startswith('spanlongtext'))
        x.desc = desc.text

        x.thumb = 'DefaultVideo.png'

        pict = c.find('td' , id=lambda x: x and x.startswith('listimagetd'))
        pic = pict.find('img')
        if not (pic is None):
            x.thumb = pic['src']

        genre = c.find('p' , style=lambda x: x and x.startswith('text-transform:capitalize'))
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

def getSearchString(keyword, page):

    keyword = keyword.replace(' ','+')

    iPage = int(page)
    x = (iPage-1) * 20

    s = 'https://www.onlinetvrecorder.com/v2/?go=list'
   #s += '&tab=search'
    s += '&station='
    s += '&date=all'
    #s += '&min_start_date=0'

    'not a nice solution, during changeover of a year'
    s += '&year=' + str(date.today().year)

    s += '&fd=1'
    s += '&fm=1'
    s += '&td=31'
    s += '&tm=12'
    s += '&actor='
    s += '&season='
    s += '&episode='
    s += '&director='
    s += '&minutes='
    s += '&title=' + keyword
    s += '&genre='
    s += '&order=beginn%20DESC' # neueste zuerst
    s += '&format=mp4,mcut,avi,hq,hcut' # stream format
    s += '&times='
    s += '&intext=0'
    s += '&exact=0'
    s += '&cbde=0'
    s += '&cbsing=0'
    s += '&cben=0'
    s += '&cbxy=0'
    s += '&cbfav=0'
    s += '&rating='
    s += '&weekday='
    s += '&searchmethod=match'
    s += '&indatefrom=0'
    s += '&indateto=0'
    s += '&intimefrom=0'
    s += '&intimeto=23'
    s += '&source=otr' # suche nur in otr
    s += '&wdh='
    s += '&fsk='
    s += '&productionyear='
    s += '&filestate='
    #s += '&_view=table'
    s += '&start=' + str(x)

    return s

def getGroupString(group, page):

    iPage = int(page)
    x = (iPage-1) * 20

    s = 'https://www.onlinetvrecorder.com/v2/?go=list&tab=search'
    s += '&station='
    s += '&date=all'
    s += '&min_start_date=0'

    'not a nice solution, during changeover of a year'
    s += '&year=' + str(date.today().year)

    s += '&fd=1'
    s += '&fm=1'
    s += '&td=31'
    s += '&tm=12'
    s += '&actor='
    s += '&season='
    s += '&episode='
    s += '&director='
    s += '&minutes='
    s += '&title='
    s += '&genre=' + group
    s += '&order=beginn%20DESC' # neueste zuerst
    s += '&format=mp4,mcut,avi,hq,hcut,' # stream format
    s += '&times='
    s += '&intext=0'
    s += '&exact=0'
    s += '&cbde=0'
    s += '&cbsing=0'
    s += '&cben=0'
    s += '&cbxy=0'
    s += '&cbfav=0'
    s += '&rating='
    s += '&weekday='
    s += '&searchmethod=match'
    s += '&indatefrom=0'
    s += '&indateto=0'
    s += '&intimefrom=0'
    s += '&intimeto=23'
    s += '&source=otr' # suche nur in otr
    s += '&wdh='
    s += '&fsk='
    s += '&productionyear='
    s += '&filestate='
    s += '&_view=table'
    s += '&start=' + str(x)

    return s

def getSearchStationString(keyword, station, date, page):

    iPage = int(page)
    x = (iPage-1) * 20

    s = 'https://www.onlinetvrecorder.com/v2/?go=list&tab=search'
    s += '&order=beginn%20DESC' # neueste zuerst
    s += '&preset='
    s += '&epg_id='
    s += '&start=' + str(x)
    s += '&view='
    s += '&state='
    s += '&title=' + keyword
    s += '&date=all'
    s += '&cbsing=1'
    if(station <> ''):
        s += '&selectedstation_' + station + '=on'
    s += '&source=otr'
    s += '&intimefrom=0'
    s += '&intimeto=23'
    if(date == ''):
        s += '&fd=1'
        s += '&fm=1'
        s += '&td=31'
        s += '&tm=12'
    else:
        dd =date.split('.')
        if(len(dd)==2):
            day= "%02d" % int(dd[0])
            month = "%02d" % int(dd[1])
            s += '&fd=' + day
            s += '&fm=' + month
            s += '&td=' + day
            s += '&tm=' + month
        else:
            s += '&fd=1'
            s += '&fm=1'
            s += '&td=31'
            s += '&tm=12'
    s += '&genre='
    s += '&weekday='
    s += '&selected_filter_weekday='
    s += '&times='
    s += '&selected_filter_times='

    'not a nice solution, during changeover of a year'
    s += '&year=' + str(date.today().year)

    s += '&productionyear='
    s += '&selected_filter_productionyear='
    s += '&format=mp4,mcut,avi,hq,hcut,' # stream format
    s += '&selected_filter_format='
    s += '&filestate='
    s += '&selected_filter_filestate='
    s += '&minutes='
    s += '&selected_filter_duration='
    s += '&wdh='
    s += '&season='
    s += '&selected_filter_season='
    s += '&episode='
    s += '&selected_filter_episode='
    s += '&rating='
    s += '&selected_filter_rating='
    s += '&fsk='
    s += '&selected_filter_fsk='
    s += '&actor='
    s += '&director='
    s += '&btn_ok=+Suchen+'
    s += '&programm=0'
    s += '&multioption='

    return s