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
import datetime

import urllib, urllib2
import requests

import re

import buggalo
import json

import mechanize
import HTMLParser
from BeautifulSoup import BeautifulSoup

import inputstreamhelper
from random import randint

PROTOCOL = 'mpd'
DRM = 'com.widevine.alpha'

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

_filePath = os.path.join(__profilePath, "user.txt")
_chanList = os.path.join(__profilePath, "channel.txt")

__resource  = xbmc.translatePath(os.path.join(__addonpath, 'resources', 'lib' )).decode("utf-8")
sys.path.append(__resource)

USE_ALL = __addon.getSetting('live') == "true"

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

    # check for premium
    login = xbmcplugin.getSetting(_handle, 'email')
    password = xbmcplugin.getSetting(_handle, 'pass')

    data = website.login(login, password, __cookiePath)
    xbmc.log('OTR ' + data.state , xbmc.LOGNOTICE)

    xbmcplugin.setContent(_handle, 'files')


    if(data.state == 'Premium'):
        addPictureItem('LIVE TV', _url + '?live=all', 'DefaultFolder.png') # Live TV

    addPictureItem(__addon.getLocalizedString(30030), _url + '?actual=1', 'DefaultFolder.png')    # highlights

    if(data.state == 'Premium'):
        #start URL
        link = 'https://www.onlinetvrecorder.com/v2/watchlist/choose.php?genre=Comedy'
        link = urllib.quote_plus(link)
        addPictureItem(__addon.getLocalizedString(30045), _url + '?online=nav&url=' + link, 'DefaultFolder.png')  # online

    addPictureItem(__addon.getLocalizedString(30034), _url + '?records=all', 'DefaultFolder.png') # meine aufnahmen
    addPictureItem(__addon.getLocalizedString(30039), _url + '?decode=all', 'DefaultFolder.png')  # meine dekodings
    addPictureItem(__addon.getLocalizedString(30035), _url + '?toplist=all', 'DefaultFolder.png') # top listen

    addPictureItem(__addon.getLocalizedString(30032), _url + '?genres=all', 'DefaultFolder.png')  # genres

    addPictureItem(__addon.getLocalizedString(30031), _url + '?search=select', 'DefaultFolder.png')  # suche
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
        hList = website.getMoreData(login, password, __cookiePath, 1)
    else:
        hList = website.getMoreData(login, password, __cookiePath, iPage)

    for aItem in hList:
        title= HTMLParser.HTMLParser().unescape(aItem.title)
        desc = HTMLParser.HTMLParser().unescape(aItem.text)
        url = aItem.url
        thumb = aItem.thumb
        addPictureItem2(title, _url + '?categories=%s' % url + '&title=%s' % title , thumb, desc)

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?actual=2', 'DefaultFolder.png') # next page
    else:
        no = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?actual=' + str(no), 'DefaultFolder.png') # next page

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

            rid = aItem.rid
            cs = aItem.cs
            mode = 'play'

            url = _url + '?movie=%s' %  mode + '&rid=%s' %  rid + '&cs=%s' %  cs  + '&epg_id=%s' % epg_id

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

def showMovie(cs, rid, epg_id):

    add = xbmcaddon.Addon('plugin.video.otrstream')

    user = add.getSetting('email')
    pw = add.getSetting('pass')
    warn = add.getSetting('warning')== "true"

    # continue ok
    ok = True

    if(warn):
        ok = False
        ok = xbmcgui.Dialog().yesno('otrstream', __addon.getLocalizedString(30014), __addon.getLocalizedString(30015) )

    if(ok):
        link = website.getPlayLink(user,pw,__cookiePath,cs,rid)

        if link is not None:
            if not (link.startswith('ERROR')):
                xbmc.log('- movie - ' + link)

                title = ''
                desc = ''
                thumb = ''

                mList = website.getMovieInfo(user, pw, __cookiePath, epg_id)
                if  len(mList) == 1:
                    title = mList[0].title
                    desc = mList[0].desc
                    thumb = mList[0].thumb


                txt = title + '\n' + desc
                playitem = xbmcgui.ListItem(path=link, thumbnailImage=thumb)
                playitem.setInfo('video', { 'plot': txt })
                xbmc.Player().play(item=link, listitem=playitem)
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

    listitem = xbmcgui.ListItem (title)
    listitem.setInfo('video', {'Title': title })

    xbmc.Player().play(url, listitem)

def searchOverview():

    xbmcplugin.setContent(_handle, 'files')

    addPictureItem(__addon.getLocalizedString(30086), _url + '?search=new', 'DefaultFolder.png')    # new search

    s1 = xbmcplugin.getSetting(_handle, 's1')
    if(len(s1) > 0):
        addPictureItem(s1, _url + '?search=' + s1 + '&page=1', 'DefaultFolder.png')    # search 01
    s2 = xbmcplugin.getSetting(_handle, 's2')
    if(len(s2) > 0):
        addPictureItem(s2, _url + '?search=' + s2 + '&page=1', 'DefaultFolder.png')    # search 02
    s3 = xbmcplugin.getSetting(_handle, 's3')
    if(len(s3) > 0):
        addPictureItem(s3, _url + '?search=' + s3 + '&page=1', 'DefaultFolder.png')    # search 03
    s4 = xbmcplugin.getSetting(_handle, 's4')
    if(len(s4) > 0):
        addPictureItem(s4, _url + '?search=' + s4 + '&page=1', 'DefaultFolder.png')    # search 04
    s5 = xbmcplugin.getSetting(_handle, 's5')
    if(len(s5) > 0):
        addPictureItem(s5, _url + '?search=' + s5 + '&page=1', 'DefaultFolder.png')    # search 05
    s6 = xbmcplugin.getSetting(_handle, 's6')
    if(len(s6) > 0):
        addPictureItem(s6, _url + '?search=' + s6 + '&page=1', 'DefaultFolder.png')    # search 06

    xbmcplugin.endOfDirectory(_handle, cacheToDisc=False)

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

            s1 = xbmcplugin.getSetting(_handle, 's1')
            s2 = xbmcplugin.getSetting(_handle, 's2')
            s3 = xbmcplugin.getSetting(_handle, 's3')
            s4 = xbmcplugin.getSetting(_handle, 's4')
            s5 = xbmcplugin.getSetting(_handle, 's5')
            s6 = xbmcplugin.getSetting(_handle, 's6')

            __addon.setSetting(id='s6', value=s5)
            __addon.setSetting(id='s5', value=s4)
            __addon.setSetting(id='s4', value=s3)
            __addon.setSetting(id='s3', value=s2)
            __addon.setSetting(id='s2', value=s1)
            __addon.setSetting(id='s1', value=keyword)

            searchPage(keyword, 1)

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

        now = datetime.datetime.strftime(datetime.datetime.now(),'%d.%m')  # %y')

        keyboard = xbmc.Keyboard(now, __addon.getLocalizedString(30038))
        keyboard.doModal()

        if (keyboard.isConfirmed()):
            date = keyboard.getText()

        if len(keyword) > 0:

            xbmcplugin.setContent(_handle, 'movies')

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

            #addPictureItem(__addon.getLocalizedString(30020), _url + '?station=' + station + '&page=2&keyword=' + keyword, 'DefaultFolder.png')

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

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + keyword + '&page=2', 'DefaultFolder.png') # next page
    else:
        x = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + keyword + '&page=' + str(x), 'DefaultFolder.png') # next page

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

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + group + '&page=2', 'DefaultFolder.png')
    else:
        x = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?search=' + group + '&page=' + str(x), 'DefaultFolder.png')

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

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?records=2', 'DefaultFolder.png') # next page
    else:
        x = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?records=' + str(x), 'DefaultFolder.png') # next page

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

    if(iPage < 2):
        addPictureItem(__addon.getLocalizedString(30020), _url + '?toplist=' + no + '&page=2', 'DefaultFolder.png')
    else:
        x = iPage + 1
        addPictureItem(__addon.getLocalizedString(30020), _url + '?toplist=' + no + '&page=' + str(x), 'DefaultFolder.png')

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


#### LIVE TV ####


def play(tv):

    is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    if is_helper.check_inputstream():

        url = 'https://www.schoener-fernsehen.com/ajax/get_live.php'
        resp = requests.post(url)

        if (resp.status_code == 200):
            obj = json.loads(resp.text)

            root = obj['channelname']

            for item in root:
                channel = root[item]['station']

                if channel == tv:
                    mpd = root[item]['mdp']
                    sec = root[item]['sec']

                    title = root[item]['title']
                    member = root[item]['membership_status']
                    desc = root[item]['description']
                    start = root[item]['starttime']
                    stop = root[item]['nextstarttime']
                    lower = root[item]['lowerstation']

                    ref = 'https://h5p2p.peer-stream.com/s0/index-video.html?mpd=//'
                    ref = ref + mpd
                    ref = ref + '&sec=' + sec

                    url = 'https://' + mpd + '?cp=' + str(randint(20000,50000))
                    url = url + '|Origin=' + urllib.quote_plus('https://h5p2p.peer-stream.com')
                    url = url + '&Referer=' + urllib.quote_plus(ref)

                    if member == 'free':
                        thumb = 'https://static.onlinetvrecorder.com/images/easy/stationlogos/white/' + lower.replace(' ','%20') + '.gif'
                    else:
                        thumb = 'https://static.onlinetvrecorder.com/images/easy/stationlogos/black/' + lower.replace(' ','%20') + '.gif'

                    playitem = xbmcgui.ListItem(path=url, thumbnailImage=thumb)
                    txt =  urllib.unquote(title) + ' ' + start + '-' + stop + '\n' + urllib.unquote(desc)
                    playitem.setInfo('video', { 'plot': txt })
                    playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
                    playitem.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                    playitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
                    xbmc.Player().play(item=url, listitem=playitem)

def showChannels(userState, chanList):

    is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    if is_helper.check_inputstream():

        url = 'https://www.schoener-fernsehen.com/ajax/get_live.php'
        resp = requests.post(url)

        if (resp.status_code == 200):
            obj = json.loads(resp.text)

            root = obj['channelname']

            if not USE_ALL:

                f= file(chanList,'r')
                lines = f.readlines()
                f.close()

                for line in lines:
                    for item in root:
                        member = root[item]['membership_status']
                        channel = root[item]['station']

                        if (member == 'free') | (userState == 'plus'):
                            if line.replace('\n','') == channel:
                                 addItem(root[item])
            else:
                for item in root:
                    member = root[item]['membership_status']
                    if (member == 'free') | (userState == 'plus'):
                        addItem(root[item])


        if USE_ALL:
            xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

        xbmcplugin.endOfDirectory(_handle, cacheToDisc=False)

def addItem(item1):

    member = item1['membership_status']
    title = item1['title']
    nxt = item1['nexttitle']
    channel = item1['station']

    lower = item1['lowerstation']
    desc = item1['description']

    start = item1['starttime']
    stop = item1['nextstarttime']
    perc = item1['passed_relative']

    strInfo = start + ' - ' + stop + ' (' + str(perc) + "%)"
    if(nxt != ''):
        strInfo = strInfo + "\nDanach: " + nxt

    desc = urllib.unquote(desc)

    if(len(desc) > 150):
        desc = desc[:147] + '...'

    desc = desc + '\n' + strInfo
    url = '{0}?tv={1}'.format(_url, channel)

    if member == 'free':
        thumb = 'https://static.onlinetvrecorder.com/images/easy/stationlogos/white/' + lower.replace(' ','%20') + '.gif'
    else:
        thumb = 'https://static.onlinetvrecorder.com/images/easy/stationlogos/black/' + lower.replace(' ','%20') + '.gif'

    list_item = xbmcgui.ListItem(label=channel + ': ' + title, thumbnailImage=thumb)
    list_item.setInfo('video', { 'plot': desc })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

def getUserState():

    userState = 'free'

    # user data
    login = xbmcplugin.getSetting(_handle, 'email')
    pw = xbmcplugin.getSetting(_handle, 'pass')

    if(len(login) != 0):

        loginURL = 'https://www.schoener-fernsehen.com/ajax/login.php'

        params = dict()
        params["email"] = login
        params["password"] = pw

        r = requests.post(loginURL, data=params)
        result = r.text

        obj = json.loads(result)
        state = obj['success']
        if(state):
            userState = obj['membership']
            xbmc.log('SF: userstate ' + userState)
        else:
            userState = 'error'
            xbmc.log('SF: login failed')

    return userState

def saveFile(filePath, userState):

    try:
        f = file(filePath,'w')
        f.write(userState)
        f.close()
    except Exception as e:
        pass

def deleteFile(filePath):

    try:
        if os.path.isfile(filePath):
            os.unlink(filePath)
    except Exception as e:
        pass

def checkFile(filePath, userState):

    date = datetime.datetime.now() - datetime.timedelta(hours = 24)
    ts = time.mktime(date.timetuple())

    # invalid login
    if(userState == 'error'):
        if(os.path.exists(filePath)):
            deleteFile(filePath)

    if(os.path.exists(filePath)):
        fileDate = os.path.getmtime(filePath)
        if(ts>fileDate):
            deleteFile(filePath)
            return False
        else:
            f= file(filePath,'r')
            txt = f.read()
            f.close()

            if(txt == userState):
                return True
            else:
                deleteFile(filePath)
                return False

    return False

def createDefault(chanList):

    if(True):

        try:
            f = file(chanList,'w')
            f.write('ARD\n')
            f.write('ZDF\n')
            f.write('NDR\n')
            f.write('VOX\n')
            f.write('SAT 1\n')
            f.write('KABEL 1\n')
            f.write('PRO SIEBEN\n')
            f.write('RTL2\n')
            f.write('KABEL1DOKU\n')
            f.write('DMAX\n')
            f.write('TLC\n')
            f.write('N24\n')
            f.write('EUROSPORT\n')
            f.write('SPORT1\n')
            f.close()

        except Exception as e:
            pass


#### main entry point ####

if __name__ == '__main__':

    PARAMS = urlparse.parse_qs(sys.argv[2][1:])
    createDefault(_chanList)

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
        showMovie(PARAMS['cs'][0], PARAMS['rid'][0], PARAMS['epg_id'][0])
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
        if (PARAMS['search'][0] == 'select'):
            searchOverview()
        elif (PARAMS['search'][0] == 'new'):
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

        while xbmcgui.Window(10000).getProperty('otrstream_runningView')=="epg":
            xbmc.sleep(10)
        xbmc.log('- close window -')
        del epg
    elif PARAMS.has_key('live'):
        userState = getUserState()

        check = checkFile(_filePath, userState)
        if(not check):
            if(userState == 'free'):
                # keine Daten ?
                xbmcgui.Dialog().notification(ADDON_NAME, 'Sie benutzen SF im FREE Modus.\nBitte melden Sie sich an.', time=5000)
            elif(userState == 'error'):
                # falsche Daten ?
                xbmcgui.Dialog().notification(ADDON_NAME, 'Der LOGIN war nicht erfolgreich.\nBitte überprüfen Sie die Daten.', time=5000)
            elif(userState == 'member'):
                # wir sind angemeldet
                xbmcgui.Dialog().notification(ADDON_NAME, 'Sie haben keinen PLUS Status\nAktivieren Sie bitte PLUS.', time=5000)
            elif(userState == 'plus'):
                # wir sind plus mitglied
                pass
            else:
                xbmcgui.Dialog().notification(ADDON_NAME, 'StateState= ' + userState, time=5000)
            saveFile(_filePath, userState)

        showChannels(userState, _chanList)
    elif PARAMS.has_key('tv'):
        play(PARAMS['tv'][0])

    else:
        mainSelector()

except Exception:
    buggalo.onExceptionRaised()
