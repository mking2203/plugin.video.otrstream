from datetime import date

def getSearchString(keyword, page, de):

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
    s += '&order=beginn+DESC' # neueste zuerst
    s += '&format=mp4,mcut,avi,hq,hcut' # stream format
    s += '&times='
    s += '&intext=0'
    s += '&exact=0'
    if(de):
        s += '&cbde=1'
    else:
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
    s += '&order=beginn+DESC' # neueste zuerst
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

def getRecordsString(page):

    iPage = int(page)
    x = (iPage-1) * 20

    s = 'https://www.onlinetvrecorder.com/v2/?go=list&tab=search&preset=5'

    s += '&order=beginn+DESC' # neueste zuerst
    s += '&epg_id='
    s += '&start=' + str(x)
    s += '&view='
    s += '&state='
    s += '&title='
    s += '&date=all'
    s += '&source=my' # suche nur records
    s += '&intimefrom=0'
    s += '&intimeto=23'
    s += '&fd=1'
    s += '&fm=1'
    s += '&td=31'
    s += '&tm=12'
    s += '&genre='
    s += '&weekday'
    s += '&selected_filter_weekday'
    s += '&times'
    s += '&selected_filter_times'
    s += '&year=' + str(date.today().year)
    s += '&productionyear'
    s += '&selected_filter_productionyear'
    s += '&format'
    s += '&selected_filter_format'
    s += '&format_mp4=on'
    s += '&format_mcut=on'
    s += '&format_avi=on'
    s += '&format_hq=on'
    s += '&format_hcut=on'
    s += '&format_hd=on'
    s += '&format_dcut=on'
    s += '&filestate='
    s += '&selected_filter_filestate='
    s += '&minutes='
    s += '&selected_filter_duration='
    s += '&wdh='
    s += '&season='
    s += '&selected_filter_season'
    s += '&episode='
    s += '&selected_filter_episode'
    s += '&rating'
    s += '&selected_filter_rating='
    s += '&fsk='
    s += '&selected_filter_fsk'
    s += '&actor'
    s += '&director'
    s += '&btn_ok=+Suchen+'
    s += '&programm=0'
    s += '&multioption'

    return s

def getSearchStationString(keyword, station, selDate, page):

    iPage = int(page)
    x = (iPage-1) * 20

    s = 'https://www.onlinetvrecorder.com/v2/?go=list&tab=search'
    s += '&order=beginn+DESC' # neueste zuerst
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
    if(selDate == ''):
        s += '&fd=1'
        s += '&fm=1'
        s += '&td=31'
        s += '&tm=12'
    else:
        dd =selDate.split('.')
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
