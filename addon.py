#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#    copyright (C) 2017 Mark Koenig
#
#    GUI EPG:
#    based on ZattooBoxExtended by Daniel Griner (griner.ch@gmail.com) License under GPL
#    based on ZattooBox by Pascal Nançoz (nancpasc@gmail.com) Licence under BSD 2 clause

#    This file is part of otrstream
#
#    otrstream is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    otrstream is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with otrstream.  If not, see <http://www.gnu.org/licenses/>.
#

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import xbmcvfs
import sys, urlparse, os
import time

import urllib, urllib2

import re

import buggalo

import mechanize
import HTMLParser
from datetime import datetime
from BeautifulSoup import BeautifulSoup


CommonRootView = 50
FullWidthList = 51
Shift = 53
ThumbnailView = 500
PictureWrapView = 510
PictureThumbView = 514
MediaListView2 = 503
MediaListView3 = 504

_listMode_ = ''

_url = sys.argv[0]
_handle = int(sys.argv[1])

__addon = xbmcaddon.Addon()
__addonId =__addon.getAddonInfo('id')
__addonname = __addon.getAddonInfo('name')

__icon = __addon.getAddonInfo('icon')

__addonpath = __addon.getAddonInfo('path').decode("utf-8")
__debug = __addon.getSetting('debug') == "true"
__view = __addon.getSetting('view') == "true"

__profilePath = xbmc.translatePath(__addon.getAddonInfo('profile')).decode("utf-8")
if not xbmcvfs.exists(__profilePath): xbmcvfs.mkdirs(__profilePath)
__cookiePath = os.path.join(__profilePath, "cookie.db")

__resource  = xbmc.translatePath(os.path.join(__addonpath, 'resources', 'lib' )).decode("utf-8")
sys.path.append(__resource)

import website

from resources.otrDB import otrDB
from resources.epg.epg import EPG

__otrDB = otrDB()

def showCredit():

    if __debug:
        xbmc.log('- credit -')

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    data = website.login(login, password, __cookiePath)

    # to do checks
    if(data.state == 'Premium'):
        xbmcgui.Dialog().ok('otrstream', __addon.getLocalizedString(30040) + ' ' + xbmcplugin.getSetting(_handle, 'email') ,
                                        __addon.getLocalizedString(30041) +  ' ' + data.state + ' - ' + data.decode,
                                        __addon.getLocalizedString(30042) + ' ' + data.value)
    else:
        xbmcgui.Dialog().ok('otrstream', __addon.getLocalizedString(30040) + ' ' + xbmcplugin.getSetting(_handle, 'email') ,
                                        __addon.getLocalizedString(30041) +  ' ' + data.state + ' - ' + data.decode,
                                        __addon.getLocalizedString(30042) + ' ' + data.value)

def mainSelector():

    if __debug:
        xbmc.log('- main selector -')

    xbmcplugin.setContent(_handle, 'files')

    addPictureItem(__addon.getLocalizedString(30030), _url + '?actual=0', 'DefaultFolder.png')    # highlights

    # check for premium
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    data = website.login(login, password, __cookiePath)
    xbmc.log('OTR ' + data.state , xbmc.LOGNOTICE)

    if(data.state == 'Premium'):

        #start URL
        link = 'https://www.onlinetvrecorder.com/v2/watchlist/choose.php?genre=Comedy'
        link = urllib.quote_plus(link)
        addPictureItem(__addon.getLocalizedString(30045), _url + '?online=nav&url=' + link, 'DefaultFolder.png')  # online

    addPictureItem(__addon.getLocalizedString(30034), _url + '?records=all', 'DefaultFolder.png') # meine aufnahmen
    addPictureItem(__addon.getLocalizedString(30039), _url + '?decode=all', 'DefaultFolder.png')  # meine dekodings
    addPictureItem(__addon.getLocalizedString(30035), _url + '?toplist=all', 'DefaultFolder.png') # top listen

    addPictureItem(__addon.getLocalizedString(30032), _url + '?genres=all', 'DefaultFolder.png')  # genres

    addPictureItem(__addon.getLocalizedString(30031), _url + '?search=now', 'DefaultFolder.png')  # suche
    addPictureItem(__addon.getLocalizedString(30037), _url + '?station=now', 'DefaultFolder.png')  # suche station

    str1 = __addon.getSetting('search1').decode("utf-8")
    str2 = __addon.getSetting('search2').decode("utf-8")
    str3 = __addon.getSetting('search3').decode("utf-8")

    if(str1 <>''):
        addPictureItem(__addon.getLocalizedString(30031) + ' : ' + str1, _url + '?search=' + str1 + '&page=1', 'DefaultFolder.png')
    if(str2 <>''):
        addPictureItem(__addon.getLocalizedString(30031) + ' : ' + str2, _url + '?search=' + str2 + '&page=1', 'DefaultFolder.png')
    if(str3 <>''):
        addPictureItem(__addon.getLocalizedString(30031) + ' : ' + str3, _url + '?search=' + str3 + '&page=1', 'DefaultFolder.png')

    addPictureItem(__addon.getLocalizedString(30033), _url + '?credit=now', 'DefaultFolder.png')  # benutzer info
    addPictureItem('EPG', _url + '?epg=today', 'DefaultFolder.png')  #epg

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % ThumbnailView)
    xbmcplugin.endOfDirectory(_handle)

def genresSelector():

    if __debug:
        xbmc.log('- genres selector -')

    xbmcplugin.setContent(_handle, 'files')

    addPictureItem(__addon.getLocalizedString(30060), _url + '?search=group11&page=1', 'DefaultFolder.png') # Filme
    addPictureItem(__addon.getLocalizedString(30068), _url + '?search=group1&page=1', 'DefaultFolder.png')  # Sport
    addPictureItem(__addon.getLocalizedString(30062), _url + '?search=group2&page=1', 'DefaultFolder.png')  # Nachrichten
    addPictureItem(__addon.getLocalizedString(30070), _url + '?search=group12&page=1', 'DefaultFolder.png') # Kinder
    addPictureItem(__addon.getLocalizedString(30064), _url + '?search=group3&page=1', 'DefaultFolder.png')  # Doku
    addPictureItem(__addon.getLocalizedString(30065), _url + '?search=group4&page=1', 'DefaultFolder.png')  # Magazine
    addPictureItem(__addon.getLocalizedString(30066), _url + '?search=group5&page=1', 'DefaultFolder.png')  # Wissen
    addPictureItem(__addon.getLocalizedString(30069), _url + '?search=group6&page=1', 'DefaultFolder.png')  # Musik
    addPictureItem(__addon.getLocalizedString(30063), _url + '?search=group7&page=1', 'DefaultFolder.png')  # Comedy
    addPictureItem(__addon.getLocalizedString(30061), _url + '?search=group8&page=1', 'DefaultFolder.png')  # Serien
    addPictureItem(__addon.getLocalizedString(30067), _url + '?search=group9&page=1', 'DefaultFolder.png')  # Show

    addPictureItem(__addon.getLocalizedString(30071), _url + '?search=group10&page=1', 'DefaultFolder.png') # Erotic

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % ThumbnailView)
    xbmcplugin.endOfDirectory(_handle)

def toplistSelector():

    if __debug:
        xbmc.log('- toplist selector -')

    xbmcplugin.setContent(_handle, 'files')

    addPictureItem(__addon.getLocalizedString(30055), _url + '?toplist=202&page=1', 'DefaultFolder.png') # blockbuster
    addPictureItem(__addon.getLocalizedString(30050), _url + '?toplist=105&page=1', 'DefaultFolder.png') # gestern
    addPictureItem(__addon.getLocalizedString(30051), _url + '?toplist=106&page=1', 'DefaultFolder.png') # wochenende
    addPictureItem(__addon.getLocalizedString(30052), _url + '?toplist=104&page=1', 'DefaultFolder.png') # 7 Tage
    addPictureItem(__addon.getLocalizedString(30053), _url + '?toplist=103&page=1', 'DefaultFolder.png') # 30 Tage
    addPictureItem(__addon.getLocalizedString(30054), _url + '?toplist=101&page=1', 'DefaultFolder.png') # des jahres

    addPictureItem(__addon.getLocalizedString(30090), _url + '?toplist=1&page=1', 'DefaultFolder.png') # meine Liste 1
    addPictureItem(__addon.getLocalizedString(30091), _url + '?toplist=2&page=1', 'DefaultFolder.png') # meine Liste 2
    addPictureItem(__addon.getLocalizedString(30092), _url + '?toplist=3&page=1', 'DefaultFolder.png') # meine Liste 3
    addPictureItem(__addon.getLocalizedString(30093), _url + '?toplist=4&page=1', 'DefaultFolder.png') # meine Liste 4

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % ThumbnailView)
    xbmcplugin.endOfDirectory(_handle)

def showSelector(page):

    if __debug:
        xbmc.log('- selector - page ' + page)

    xbmcplugin.setContent(_handle, 'movies')

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    iPage = int(page)

    if(iPage < 2):
        hList = website.getMoreData(login, password, __cookiePath, 0)

        addPictureItem(__addon.getLocalizedString(30020), _url + '?actual=2', 'DefaultFolder.png')

    if(iPage > 1):
        hList = website.getMoreData(login, password, __cookiePath, iPage)

        no = iPage - 1
        addPictureItem(__addon.getLocalizedString(30021), _url + '?actual=' + str(no), 'DefaultFolder.png')
        no = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?actual=' + str(no), 'DefaultFolder.png')

    for aItem in hList:
        title= HTMLParser.HTMLParser().unescape(aItem.title)
        desc = HTMLParser.HTMLParser().unescape(aItem.text)
        url = aItem.url
        thumb = aItem.thumb
        addPictureItem2(title, _url + '?categories=%s' % url + '&title=%s' % title , thumb, desc)

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView2)
    xbmcplugin.endOfDirectory(_handle)

def showCategory(epg_id, iTitle):

    if __debug:
        xbmc.log('- category - ' + epg_id + " / " + iTitle)

    xbmcplugin.setContent(_handle, 'movies')

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    mList = website.getMovies(login, password, __cookiePath, epg_id)

    addPictureItem('Screenshots', _url + '?screenshot=' + epg_id, 'DefaultFolder.png')

    for aItem in mList:
        title = aItem.title
        url = aItem.url
        price = aItem.price
        thumb = aItem.thumb

        if(title == 'Preview'):
            addPictureItem2s(title, _url + '?preview=%s' % url + '&title=%s' % iTitle, thumb, aItem.desc, aItem.stars)
        elif(title == 'prev'):
            addPictureItem2s(__addon.getLocalizedString(30025), _url + '?categories=%s' % url + '&title=%s' % title, thumb, '', 0)
        elif(title == 'next'):
            addPictureItem2s(__addon.getLocalizedString(30026), _url + '?categories=%s' % url + '&title=%s' % title, thumb, '', 0)
        else:
            para = url
            para = para.replace('"','')
            data = para.split(',')

            eid = data[0]
            rid = data[1]
            mode = data[2]

            url = _url + '?movie=%s' %  mode + '&eid=%s' %  eid + '&rid=%s' %  rid

            addPictureItem2s(aItem.title + " / " + price, url, thumb, aItem.desc, aItem.stars)

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView2)
    xbmcplugin.endOfDirectory(_handle)

def showScreenshot(epg_id):

    if __debug:
        xbmc.log('- screenshot - ' + epg_id)

    xbmcplugin.setContent(_handle, 'movies')

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    mList = website.getScreenshots(login, password, __cookiePath, epg_id)

    if mList is not None:
        for aItem in mList:
            addPictureItem(aItem.title, '', aItem.url)

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % Shift)
    xbmcplugin.endOfDirectory(_handle)

def showMovie(eid, rid, mode):

    add = xbmcaddon.Addon('plugin.video.otrstream')

    user = add.getSetting('email')
    pw = add.getSetting('pass')
    warn = add.getSetting('warning')== "true"

    # continue ok
    ok = True

    if(warn):
        ok = False
        ok = xbmcgui.Dialog().yesno('otrstream', __addon.getLocalizedString(30014), __addon.getLocalizedString(30015) )

    if(ok or (not warn)):
        link = website.getPlayLink(user, pw, __cookiePath, eid, rid, mode)
        if(not link.startswith('http')):
            link = 'https:' + link
    else:
        link = None

    if link is not None:
        if not (link.startswith('ERROR')):
            xbmc.log('- movie - ' + link)
            xbmc.Player().play(link)
        else:
            xbmc.executebuiltin('Notification(Free-Stream,' + link + ', 3000)')
    else:
        xbmc.log('- movie - not found')

def showPreview(url, title):

    if __debug:
        xbmc.log('- preview - ' + title + " / " + url)

    url = urllib.unquote(url).decode('utf8')

    if __debug:
        xbmc.log('Play preview ' + url)

    listitem =xbmcgui.ListItem (title)
    listitem.setInfo('video', {'Title': title })

    xbmc.Player().play(url, listitem)

def search():

    if __debug:
        xbmc.log('- search -')

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    keyboard = xbmc.Keyboard('', __addon.getLocalizedString(30031))
    keyboard.doModal()

    if (keyboard.isConfirmed()):
        keyword = keyboard.getText()

        if len(keyword) > 0:

            xbmcplugin.setContent(_handle, 'movies')

            addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + keyword + '&page=2', 'DefaultFolder.png')

            de = xbmcplugin.getSetting(_handle, 'searchDE')== "true"
            hList = website.search(login, password, __cookiePath, keyword, '1', de)

            for aItem in hList:
                id = aItem.id
                title = aItem.title
                if len(aItem.serie) > 0:
                    desc = aItem.date + " " + aItem.time + " " + aItem.serie +  "-" + aItem.episode +  " " + aItem.desc
                else:
                    desc = aItem.date + " " + aItem.time + " " + aItem.desc
                thumb = aItem.thumb

                addPictureItem3(title, _url + '?categories=%s' % id + '&title=%s' % title, thumb, desc, aItem.genre)

            if(__view):
                xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)

            xbmcplugin.endOfDirectory(_handle)

def searchStation():

    if __debug:
        xbmc.log('- search station -')

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    keyboard = xbmc.Keyboard('', __addon.getLocalizedString(30031))
    keyboard.doModal()

    if (keyboard.isConfirmed()):
        keyword = keyboard.getText()

        station = ''
        date = ''

        keyboard = xbmc.Keyboard('', __addon.getLocalizedString(30036))
        keyboard.doModal()

        if (keyboard.isConfirmed()):
            station = keyboard.getText()

        now = datetime.strftime(datetime.now(),'%d.%m')  # %y')

        keyboard = xbmc.Keyboard(now, __addon.getLocalizedString(30038))
        keyboard.doModal()

        if (keyboard.isConfirmed()):
            date = keyboard.getText()

        if len(keyword) > 0:

            xbmcplugin.setContent(_handle, 'movies')

            #addPictureItem(__addon.getLocalizedString(30020), _url + '?station=' + station + '&page=2&keyword=' + keyword, 'DefaultFolder.png')

            de = xbmcplugin.getSetting(_handle, 'searchDE')== "true"
            hList = website.searchStation(login,password, __cookiePath, keyword, station, date, '1')

            for aItem in hList:
                id = aItem.id
                title = aItem.title
                if len(aItem.serie) > 0:
                    desc = aItem.date + " " + aItem.time + " " + aItem.serie +  "-" + aItem.episode +  " " + aItem.desc
                else:
                    desc = aItem.date + " " + aItem.time + " " + aItem.desc
                thumb = aItem.thumb

                addPictureItem3(title, _url + '?categories=%s' % id + '&title=%s' % title, thumb, desc, aItem.genre)

            if(__view):
                xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)

            xbmcplugin.endOfDirectory(_handle)

def searchPage(keyword, page, station=None):

    if __debug:
        xbmc.log('- search ' + keyword +' page ' + page + ' -')

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    xbmcplugin.setContent(_handle, 'movies')

    iPage = int(page)

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + keyword + '&page=2', 'DefaultFolder.png')

    if(iPage > 1):
        x = iPage - 1
        addPictureItem(__addon.getLocalizedString(30021), _url + '?search=' + keyword + '&page=' + str(x), 'DefaultFolder.png')
        x = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + keyword + '&page=' + str(x), 'DefaultFolder.png')

    de = xbmcplugin.getSetting(_handle, 'searchDE')== "true"
    hList = website.search(login,password, __cookiePath, keyword, page, de)

    for aItem in hList:
        id = aItem.id
        title = aItem.title
        if len(aItem.serie) > 0:
            desc = aItem.date + ' ' + aItem.time + ' S' + aItem.serie +  '-E' + aItem.episode +  ' ' + aItem.desc
        else:
            desc = aItem.date + ' ' + aItem.time + ' ' + aItem.desc
        thumb = aItem.thumb

        addPictureItem3(title, _url + '?categories=%s' % id + '&title=%s' % title, thumb, desc, aItem.genre)

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)
    xbmcplugin.endOfDirectory(_handle)

def searchGroup(group , page):

    if __debug:
        xbmc.log('- searchgroup ' + group + ' - ' + page )

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    xbmcplugin.setContent(_handle, 'movies')

    iPage = int(page)

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + group + '&page=2', 'DefaultFolder.png')

    if(iPage > 1):
        x = iPage - 1
        addPictureItem(__addon.getLocalizedString(30021), _url + '?search=' + group + '&page=' + str(x), 'DefaultFolder.png')
        x = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + group + '&page=' + str(x), 'DefaultFolder.png')

    de = xbmcplugin.getSetting(_handle, 'searchDE')== "true"
    hList = website.searchGroup(login, password, __cookiePath, group, page)

    for aItem in hList:
        id = aItem.id
        title = aItem.title
        if len(aItem.serie) > 0:
            desc = aItem.date + ' ' + aItem.time + ' S' + aItem.serie +  '-E' + aItem.episode +  ' ' + aItem.desc
        else:
            desc = aItem.date + ' ' + aItem.time + ' ' + aItem.desc
        thumb = aItem.thumb

        addPictureItem3(title, _url + '?categories=%s' % id + '&title=%s' % title, thumb, desc, aItem.genre)

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)
    xbmcplugin.endOfDirectory(_handle)

def showRecords(page):

    if __debug:
        xbmc.log('- records - ' + page)

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    xbmcplugin.setContent(_handle, 'movies')

    iPage = int(page)

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?records=2', 'DefaultFolder.png')

    if(iPage > 1):
        x = iPage - 1
        addPictureItem(__addon.getLocalizedString(30021), _url + '?records=' + str(x), 'DefaultFolder.png')
        x = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?records=' + str(x), 'DefaultFolder.png')

    hList = website.getRecords(login, password, __cookiePath, page)
    for aItem in hList:
        id = aItem.id
        title = aItem.title
        if len(aItem.serie) > 0:
            desc = aItem.date + ' ' + aItem.time + ' S' + aItem.serie +  '-E' + aItem.episode +  ' ' + aItem.desc
        else:
            desc = aItem.date + ' ' + aItem.time + ' ' + aItem.desc
        thumb = aItem.thumb

        addPictureItem3(title, _url + '?categories=%s' % id + '&title=%s' % title, thumb, desc, aItem.genre)

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)
    xbmcplugin.endOfDirectory(_handle)

def showToplist(no, page):

    if __debug:
        xbmc.log('- toplist ' + str(no) + "/ p." + str(page))

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    xbmcplugin.setContent(_handle, 'movies')

    iPage = int(page)

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?toplist=' + no + '&page=2', 'DefaultFolder.png')

    if(iPage > 1):
        x = iPage - 1
        addPictureItem(__addon.getLocalizedString(30021), _url + '?toplist=' + no + '&page=' + str(x), 'DefaultFolder.png')
        x = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?toplist=' + no + '&page=' + str(x), 'DefaultFolder.png')

    hList = website.getList(login, password, __cookiePath, no, page)
    for aItem in hList:
        id = aItem.id
        title = aItem.title
        if len(aItem.serie) > 0:
            desc = aItem.date + ' ' + aItem.time + ' S' + aItem.serie +  '-E' + aItem.episode +  ' ' + aItem.desc
        else:
            desc = aItem.date + ' ' + aItem.time + ' ' + aItem.desc
        thumb = aItem.thumb

        addPictureItem3(title, _url + '?categories=%s' % id + '&title=%s' % title, thumb, desc, aItem.genre)

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)
    xbmcplugin.endOfDirectory(_handle)

def showDecode():

    xbmcplugin.setContent(_handle, 'files')

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    decList = website.getDecode(login, password, __cookiePath)
    for aItem in decList:

        title = aItem.title
        thumb = aItem.thumb

        addPictureItem(title, _url + '?search=%s' % aItem.search + '&page=1' , thumb)

    if(__view):
        xbmc.executebuiltin('Container.SetViewMode(%d)' % ThumbnailView)
    xbmcplugin.endOfDirectory(_handle)

 # --------------  helper -------------------

def showOnline(mode, url):

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    if((mode == 'nav') | (mode == 'season')):

        xbmcplugin.setContent(_handle, 'files')

        page = website.getPage(login, password, __cookiePath, url)
        soup = BeautifulSoup(page)

        table = soup.find('td' , {'class' : 'nav'} )
        strHtml = str(table)

        regex = '<a.href=\"(.*?)\".*?>(.*?)<'
        for m in re.finditer(regex, strHtml, re.DOTALL):
            link =  m.group(1).strip()
            name =  m.group(2).strip()

            if(mode == 'nav'):
                link = urllib.quote_plus('https://www.onlinetvrecorder.com/v2/watchlist/choose.php' + link)
                addPictureItem(name, _url + '?online=group&url=' + link, 'DefaultFolder.png') # group
            else:
                link = urllib.quote_plus('https://www.onlinetvrecorder.com/v2/watchlist/watch.php' + link)
                addPictureItem(name, _url + '?online=episode&url=' + link, 'DefaultFolder.png') # group

            if(__view):
                xbmc.executebuiltin('Container.SetViewMode(%d)' % ThumbnailView)
        xbmcplugin.endOfDirectory(_handle)

    elif (mode == 'group'):

        xbmcplugin.setContent(_handle, 'movies')

        page = website.getPage(login, password, __cookiePath, url)
        soup = BeautifulSoup(page)

        tables = soup.findAll('td' , {'class' : 'wsite-multicol-col'} )

        for table in tables:

            strHtml = str(table)

            regex = '<a.href=\"(.*?)\"'
            m = re.search(regex, strHtml)
            link = 'https://www.onlinetvrecorder.com/v2/watchlist/' + m.group(1)
            link = urllib.quote_plus(link)

            regex = '<h2.*?<font.*?>(.*?)<'
            m = re.search(regex, strHtml, re.DOTALL)
            title = m.group(1).strip()

            regex = 'background-image:url\((.*?)\)'
            m = re.search(regex, strHtml, re.DOTALL)
            img = m.group(1)

            addPictureItem(title, _url + '?online=season&url=' + link, img) # episode

            if(__view):
                xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)
        xbmcplugin.endOfDirectory(_handle)

    elif (mode == 'episode'):

        xbmcplugin.setContent(_handle, 'movies')

        page = website.getPage(login, password, __cookiePath, url)
        soup = BeautifulSoup(page)

        tables = soup.findAll('td' , {'class' : 'wsite-multicol-col'} )

        for table in tables:

            strHtml = str(table)

            regex = '<a.href=\"(.*?)\"'
            m = re.search(regex, strHtml)
            link = 'https://www.onlinetvrecorder.com/v2/watchlist/watch.php' + m.group(1)
            link = urllib.quote_plus(link)

            regex = '<h2.*?<font.*?>(.*?)<'
            m = re.search(regex, strHtml, re.DOTALL)
            title = m.group(1).strip()

            regex = 'background-image:url\((.*?)\)'
            m = re.search(regex, strHtml, re.DOTALL)
            img = m.group(1)

            addPictureItem(title, _url + '?online=detail&url=' + link, img) # movie

            if(__view):
                xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)
        xbmcplugin.endOfDirectory(_handle)

    elif (mode == 'detail'):

        xbmcplugin.setContent(_handle, 'movies')

        page = website.getPage(login, password, __cookiePath, url)
        soup = BeautifulSoup(page.decode('utf-8', 'ignore'))

        # image
        img = 'DefaultVideo.png'
        regex = 'background:.url\((.*?)\)'
        m = re.search(regex, page, re.DOTALL)
        if m is not None:
            img = m.group(1)

        table = soup.find('div' , {'id' : 'bannerright'} )
        banner = str(table)

        soup = BeautifulSoup(banner.decode('utf-8', 'ignore'))
        table = soup.find('div' , {'class' : 'wsite-text wsite-headline-paragraph'} )
        strHtml = str(table)

        # desc / cost
        cost = ''
        desc = ''

        regex = '<div.style.*?>(.*?)<.*?<\/div>(.*?)<\/div>'
        m = re.search(regex, strHtml, re.DOTALL)
        if m is not None:
            cost = m.group(1).strip()
            desc = m.group(2).strip()

        # title
        regex = '<span.class=\"wsite-text.wsite-headline\">(.*?)<'
        m = re.search(regex, banner, re.DOTALL)
        title = m.group(1).strip()

        # url (same)
        url = urllib.quote_plus(url)

        addMovieItemExt(title, _url + '?online=movie&url=' + url, img, cost + '\n' + desc) # movie

        if(__view):
            xbmc.executebuiltin('Container.SetViewMode(%d)' % MediaListView3)
        xbmcplugin.endOfDirectory(_handle)

    elif (mode == 'movie'):
        # play movie
        xbmcplugin.setContent(_handle, 'movies')

        add = xbmcaddon.Addon('plugin.video.otrstream')
        warn = add.getSetting('warning')== "true"

        # continue ok
        ok = True

        if(warn):
            ok = False
            ok = xbmcgui.Dialog().yesno('otrstream', __addon.getLocalizedString(30014), __addon.getLocalizedString(30015) )

        if(ok or (not warn)):

            page = website.getPage(login, password, __cookiePath, url)

            # get parameters
            regex = 'getSeriesWatchlistPlayer\(\'(.*?)\',\'(.*?)\''
            m = re.search(regex, page)

            if m is not None:
                # query values
                link = 'https://www.onlinetvrecorder.com/v2/ajax/get_series_watchlist_player.php'
                page = website.getOnlineMovie( __cookiePath, link, m.group(1), m.group(2))

                # now find source
                regex = '<source.src=\"(.*?)\"'
                m = re.search(regex, page)

                if m is not None:
                    listitem =xbmcgui.ListItem ('Movie')
                    listitem.setInfo('video', {'Title': 'Movie' })
                    xbmc.Player().play(m.group(1), listitem)

def addPictureItem(title, url, thumb):

    list_item = xbmcgui.ListItem(label=title, thumbnailImage=thumb)

    list_item.setArt({'thumb': thumb,
                      'icon': thumb,
                      'poster': thumb})

    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

def addPictureItem2(title, url, thumb, desc):

    list_item = xbmcgui.ListItem(label=title, thumbnailImage=thumb)
    list_item.addContextMenuItems([(__addon.getLocalizedString(30022), 'Action(ParentDir)'),
                                   (__addon.getLocalizedString(30023), 'XBMC.Container.Update(plugin://plugin.video.otrstream/?main=go)'),
                                   (__addon.getLocalizedString(30024), 'ActivateWindow(10000)')])


    list_item.setArt({'thumb': thumb,
                      'icon': thumb,
                      'poster': thumb})

    list_item.setInfo('video', { 'plot': desc })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

def addPictureItem2s(title, url, thumb, desc, stars):

    list_item = xbmcgui.ListItem(label=title, thumbnailImage=thumb)
    list_item.addContextMenuItems([(__addon.getLocalizedString(30022), 'Action(ParentDir)'),
                                   (__addon.getLocalizedString(30023), 'XBMC.Container.Update(plugin://plugin.video.otrstream/?main=go)'),
                                   (__addon.getLocalizedString(30024), 'ActivateWindow(10000)')])


    list_item.setArt({'thumb': thumb,
                      'icon': thumb,
                      'poster': thumb})

    list_item.setInfo('video', { 'plot': desc , 'rating': float(stars * 2) })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

def addPictureItem3(title, url, thumb, desc, genre):

    list_item = xbmcgui.ListItem(label=title, thumbnailImage=thumb)
    list_item.addContextMenuItems([(__addon.getLocalizedString(30022), 'Action(ParentDir)'),
                                   (__addon.getLocalizedString(30023), 'XBMC.Container.Update(plugin://plugin.video.otrstream/?main=go)'),
                                   (__addon.getLocalizedString(30024), 'ActivateWindow(10000)')])

    list_item.setArt({'thumb': thumb,
                      'icon': thumb,
                      'poster': thumb})

    list_item.setInfo('video', { 'plot': desc, 'genre': genre })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

def addMovieItem(title, url, thumb):

    list_item = xbmcgui.ListItem(label=title, thumbnailImage=thumb)

    list_item.setArt({'thumb': thumb,
                      'icon': thumb,
                      'poster': thumb})

    xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

def addMovieItemExt(title, url, thumb, desc):

    list_item = xbmcgui.ListItem(label=title, thumbnailImage=thumb)

    list_item.setArt({'thumb': thumb,
                      'icon': thumb,
                      'poster': thumb})

    list_item.setInfo('video', { 'plot': desc })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

#### main entry point ####

if __name__ == '__main__':

    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

try:

    # check login
    check = website.checkCookie(__cookiePath)

    if(not check):
        xbmcgui.Dialog().notification(__addonname, __addon.getLocalizedString(30100), time=3000)

        user = xbmcplugin.getSetting(_handle, 'email')
        pw = xbmcplugin.getSetting(_handle, 'pass')
        login = website.login(user, pw, __cookiePath)
        if(login.state == 'not loged in'):
            xbmcgui.Dialog().notification(__addonname, __addon.getLocalizedString(30101), time=5000)

    if PARAMS.has_key('categories'):
        showCategory(PARAMS['categories'][0], PARAMS['title'][0])
    elif PARAMS.has_key('movie'):
        showMovie(PARAMS['eid'][0], PARAMS['rid'][0], PARAMS['movie'][0])
    elif PARAMS.has_key('online'):
        showOnline(PARAMS['online'][0], PARAMS['url'][0])
    elif PARAMS.has_key('screenshot'):
        showScreenshot(PARAMS['screenshot'][0])
    elif PARAMS.has_key('preview'):
        showPreview(PARAMS['preview'][0],PARAMS['title'][0])
    elif PARAMS.has_key('actual'):
        SHOW_CREDIT = False
        showSelector(PARAMS['actual'][0])
    elif PARAMS.has_key('search'):
        if (PARAMS['search'][0] == 'now'):
            search()
        elif (PARAMS['search'][0][:5] == 'group'):
            searchGroup(PARAMS['search'][0], PARAMS['page'][0])
        else:
            searchPage(PARAMS['search'][0], PARAMS['page'][0])
    elif PARAMS.has_key('station'):
        if (PARAMS['station'][0] == 'now'):
            searchStation()
    elif PARAMS.has_key('credit'):
        showCredit()
    elif PARAMS.has_key('genres'):
        genresSelector()
    elif PARAMS.has_key('records'):
        if (PARAMS['records'][0] == 'all'):
            showRecords('1')
        else:
            showRecords(PARAMS['records'][0])
    elif PARAMS.has_key('decode'):
        showDecode()
    elif PARAMS.has_key('toplist'):
        if (PARAMS['toplist'][0] == 'all'):
            toplistSelector()
        else:
            showToplist(PARAMS['toplist'][0], PARAMS['page'][0])
    elif PARAMS.has_key('main'):
        mainSelector()
    elif PARAMS.has_key('epg'):

        epg = EPG('1', 'True')
        epg.loadChannels(_listMode_ == 'favourites')
        xbmc.log('- show window -')
        epg.show() #doModal()
        xbmc.log('- now wait -')
	while xbmcgui.Window(10000).getProperty('otrstream_runningView')=="epg": xbmc.sleep(10)
	xbmc.log('- close window -')
	del epg

    else:
        mainSelector()

except Exception:
    buggalo.onExceptionRaised()
