# coding=utf-8
#
#    copyright (C) 2017 Steffen Rolapp (github@rolapp.de)
#
#    based on ZattooBoxExtended by Daniel Griner (griner.ch@gmail.com) license under GPL
#    
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

import xbmc, xbmcgui, xbmcaddon, os, xbmcplugin, datetime, time
import json, sys

import functions
import urllib2, re

__addon__ = xbmcaddon.Addon()
_listMode_ = __addon__.getSetting('channellist')
_channelList_=[]
localString = __addon__.getLocalizedString
local = xbmc.getLocalizedString

_umlaut_ = {ord(u'ä'): u'ae', ord(u'ö'): u'oe', ord(u'ü'): u'ue', ord(u'ß'): u'ss'}

class ItemClass(object):
    pass

REMOTE_DBG = False

# append pydev remote debugger
if REMOTE_DBG:
  # Make pydev debugger works for auto reload.
  # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
  try:
    import pysrc.pydevd as pydevd  # with the addon script.module.pydevd, only use `import pydevd`
  # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
    #pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True, suspend=False)
    pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)
  except ImportError:
    sys.stderr.write("Error: You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
    sys.exit(1)

class otrDB(object):
  def __init__(self):
    self.conn = None
    profilePath = xbmc.translatePath(__addon__.getAddonInfo('profile'))
    if not os.path.exists(profilePath): os.makedirs(profilePath)
    self.databasePath = os.path.join(profilePath, "otr.db")
    self.connectSQL()
    
  @staticmethod
  def adapt_datetime(ts):
    # http://docs.python.org/2/library/sqlite3.html#registering-an-adapter-callable
    return time.mktime(ts.timetuple())

  @staticmethod
  def convert_datetime(ts):
    try:
        return datetime.datetime.fromtimestamp(float(ts))
    except ValueError:
        return None
         
  def connectSQL(self):
    import sqlite3

    sqlite3.register_adapter(datetime.datetime, self.adapt_datetime)
    sqlite3.register_converter('timestamp', self.convert_datetime)

    self.conn = sqlite3.connect(self.databasePath, detect_types=sqlite3.PARSE_DECLTYPES)
    self.conn.execute('PRAGMA foreign_keys = ON')
    self.conn.row_factory = sqlite3.Row

    # check if DB exists
    c = self.conn.cursor()
    try: c.execute('SELECT * FROM showinfos')
    except: self._createTables()


  def _createTables(self):
    import sqlite3
    c = self.conn.cursor()

    try: c.execute('DROP TABLE channels')
    except: pass
    try: c.execute('DROP TABLE programs')
    except: pass
    try: c.execute('DROP TABLE updates')
    except: pass
    try: c.execute('DROP TABLE playing')
    except: pass
    try: c.execute('DROP TABLE showinfos')
    except: pass
    self.conn.commit()

    try:
      c.execute('CREATE TABLE channels(id TEXT, title TEXT, logo TEXT, weight INTEGER, favourite BOOLEAN, PRIMARY KEY (id) )')
      c.execute('CREATE TABLE programs(showID TEXT, title TEXT, channel TEXT, start_date TIMESTAMP, end_date TIMESTAMP, series BOOLEAN, description TEXT, description_long TEXT, year TEXT, country TEXT, genre TEXT, category TEXT, image_small TEXT, image_large TEXT, updates_id INTEGER, FOREIGN KEY(channel) REFERENCES channels(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED, FOREIGN KEY(updates_id) REFERENCES updates(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)')
      c.execute('CREATE TABLE updates(id INTEGER, date TIMESTAMP, type TEXT, PRIMARY KEY (id) )')
      #c.execute('CREATE TABLE playing(channel TEXT, start_date TIMESTAMP, action_time TIMESTAMP, current_stream INTEGER, streams TEXT, PRIMARY KEY (channel))')
      c.execute('CREATE TABLE showinfos(showID INTEGER, info TEXT, PRIMARY KEY (showID))')
      c.execute('CREATE TABLE playing(channel TEXT, current_stream INTEGER, streams TEXT, PRIMARY KEY (channel))')

      c.execute('CREATE INDEX program_list_idx ON programs(channel, start_date, end_date)')
      c.execute('CREATE INDEX start_date_idx ON programs(start_date)')
      c.execute('CREATE INDEX end_date_idx ON programs(end_date)')

      self.conn.commit()
      c.close()

    except sqlite3.OperationalError, ex:
      pass

  def updateChannels(self, rebuild=False):
    c = self.conn.cursor()

    if rebuild == False:
        date = datetime.date.today().strftime('%Y-%m-%d')
        c.execute('SELECT * FROM updates WHERE type=? ', ['channels']) # we dont update, only on request, if one exist OK
        if len(c.fetchall())>0:
            c.close()
            return

    date = datetime.date.today()
    xbmcgui.Dialog().notification('Update channels', self.formatDate(date), __addon__.getAddonInfo('path') + '/icon.png', 5000, False)

    # always clear db on update
    c.execute('DELETE FROM channels')

    channelsData = []
        
    user = __addon__.getSetting('email')
    pw = __addon__.getSetting('pass')
    
    programData = functions.getHTML(user, pw, 'https://www.onlinetvrecorder.com/v2/?go=epg_export')

    match = re.search('<b>Sender.*?(?P<data><div.*?)<.div>', programData, re.DOTALL)
    if(match != None):
        data = match.group('data')
        for m in re.finditer('<input.type=checkbox.name=\'cb(?P<id>.*?)\'.>(?P<channel>.*?)<br>', data, re.DOTALL):
            #print m.group('id') + " - " + m.group('channel')
            
            item = ItemClass()
            item.id = m.group('id')
            item.title =  m.group('channel').strip()
            item.logo =  'https://static.onlinetvrecorder.com/images/easy/stationlogos/black/' + item.title.lower().replace(' ','%20') + ".gif"
            channelsData.append(item)

    # TODO make this adjust able
    favoritesData = ['ARD', 'ZDF', 'NDR', 'PRO7', 'RTL', 'SAT1', 'VOX', 'KABEL 1', 'RTL2', '3SAT',
                     'ZDF NEO', 'SIXX', 'TLC', 'SRTL', 'DISNEY', 'KIKA', 'NTV', 'N24', 'DMAX',
                     'KABEL1DOKU', 'EUROSPORT', 'SPORT1', 'SKYSPORTNEWS', 'DELUXEMUSIC']

    nr = 0
    
    for channel in channelsData:

        weight = 1000 + nr
        favourite = False

        for idx, ch in enumerate(favoritesData):
            if(ch.lower() == channel.title.lower()):
                weight = idx + 1
                favourite = True

        c.execute('INSERT OR IGNORE INTO channels(id, title, logo, weight, favourite) VALUES(?, ?, ?, ?, ?)', [channel.id, channel.title, channel.logo, weight, favourite])
        if not c.rowcount:
            c.execute('UPDATE channels SET title=?, logo=?, weight=?, favourite=? WHERE id=?', [channel.title, channel.logo, weight, favourite, channel.id])

        if(not favourite): 
            nr += 1

    if nr>0: c.execute('INSERT INTO updates(date, type) VALUES(?, ?)', [datetime.date.today(), 'channels'])
    self.conn.commit()
    c.close()
    return
    
  def updateProgram(self, date=None, rebuild=False):
  
    import sqlite3
    
    if date is None: date = datetime.date.today()
    else: date = date.date()

    c = self.conn.cursor()

    if rebuild:
      c.execute('DELETE FROM programs')
      c.execute('DELETE FROM updates WHERE type=program')
      self.conn.commit()

    nowExit = True

    # we need the data for actual day and next day  
    actdate = date.strftime('%Y-%m-%d')
    c.execute('SELECT * FROM updates WHERE date=? AND type=? ', [actdate, 'program'])
 
    count=c.fetchall()
    if len(count)==0:
        nowExit = False
      
    # we need the data for actual day and next day 
    nextDate = date + datetime.timedelta(days = 1)
    actdate = nextDate.strftime('%Y-%m-%d')
    c.execute('SELECT * FROM updates WHERE date=? AND type=? ', [actdate, 'program'])
 
    count=c.fetchall()
    if len(count)==0:
        nowExit = False
      
    if (nowExit == True):
        c.close()
        return

    #xbmc.executebuiltin("ActivateWindow(busydialog)")
    programData = []

    for i in xrange(0, 2):

        getDate =  date + datetime.timedelta(days = i)

        y = getDate.year
        m = getDate.month
        d = getDate.day
        strDate = '%02i.%02i.%04i' % (d, m ,y)

        xbmcgui.Dialog().notification(__addon__.getLocalizedString(31917), strDate , __addon__.getAddonInfo('path') + '/icon.png', 3000, False)

        file = '%04i_%02i_%02i' % (y, m ,d)
        print file
        csv = urllib2.urlopen('https://www.onlinetvrecorder.com/epg/csv/epg_' + file +'.csv', timeout = 30)

        first = True

        for line in csv:
    
            if(not first):
                line = line.strip()

                values =line.split(';')
                if(len(values) == 18):

                    try:
                        item = ItemClass()

                        item.id = values[0]

                        item.start = long(time.mktime(datetime.datetime.strptime(values[1], "%d.%m.%Y %H:%M:%S").timetuple()))
                        item.end = long(time.mktime(datetime.datetime.strptime(values[2], "%d.%m.%Y %H:%M:%S").timetuple()))

                        item.channel = values[4].upper()
                        
                        item.title = self.myConvert(values[5])
                        item.desc = self.myConvert(values[7]) #values[7].decode('cp1252','replace')

                        item.genre = values[6].decode('cp1252','replace')

                        programData.append(item)
                    except:
                        print "Unexpected error:", sys.exc_info()[0]
                        raise

            first = False

    cnt = 0
    unknown = 0

    for program in programData:

        cid = 'n.a.'

        c.execute('SELECT * FROM channels WHERE title==?', [program.channel])
        countt=c.fetchall()
        if len(countt)==0:
            unknown += 1
            #print "unkown channel : " + program.channel
        else:
            cid = countt[0]['id']

            cnt += 1

            try:
                #print ('INSERT OR IGNORE INTO programs(channel, title, start_date, end_date, description, genre, showID) VALUES(%, %, %, %, %, %, %)', [cid , program.title, program.start, program.end, program.desc, program.genre, program.id])
                i = 3
            except:
                pass
            c.execute('INSERT OR IGNORE INTO programs(channel, title, start_date, end_date, description, genre, showID) VALUES(?, ?, ?, ?, ?, ?, ?)', [cid, program.title, program.start, program.end, program.desc, program.genre, program.id])          
            if not c.rowcount:
                c.execute('UPDATE programs SET channel=?, title=?, start_date=?, end_date=?, description=?, genre=? WHERE showID=?', [cid, program.title, str(program.start), str(program.end), program.desc, program.genre, program.id])                       

    if(unknown > 0):
        print "unkown channel : " + str(unknown)

    try:
        self.conn.commit()
        
        if cnt > 0: 
            c.execute('INSERT into updates(date, type) VALUES(?, ?)', [date, 'program'])
            c.execute('INSERT into updates(date, type) VALUES(?, ?)', [nextDate, 'program'])
            self.conn.commit()
    except sqlite3.Error as e:
        print("A SQL error occurred:", e.args[0])

    #xbmc.executebuiltin("Dialog.Close(busydialog)")
    c.close()
    return

  def myConvert(self, text):

    try:
        text = text.decode('utf-8')
    except:
        text = text.decode('cp1252','replace')

    return text

  def getChannelList(self, favourites=True):
    #self.updateChannels()
    c = self.conn.cursor()
    if favourites: c.execute('SELECT * FROM channels WHERE favourite=1 ORDER BY weight')
    else: c.execute('SELECT * FROM channels ORDER BY weight')
    channelList = {'index':[]}
    nr=0
    for row in c:
      channelList[row['id']]={
        'id': str(row['id']),
        'title': row['title'],
        'logo': row['logo'],
        'weight': row['weight'],
        'favourite': row['favourite'],
        'nr':nr
      }
      channelList['index'].append(str(row['id']))
      nr+=1
    c.close()
    return channelList

  def get_channelInfo(self, channel_id):
    c = self.conn.cursor()
    c.execute('SELECT * FROM channels WHERE id=?', [channel_id])
    row = c.fetchone()
    channel = {
         'id':row['id'],
         'title':row['title'],
         'logo':row['logo'],
         'weight':row['weight'],
         'favourite':row['favourite']
    }
    c.close()
    return channel


  def getPrograms(self, channels, get_long_description=False, startTime=datetime.datetime.now(), endTime=datetime.datetime.now()):
    import urllib
    c = self.conn.cursor()
    programList = []
 
    for chan in channels['index']:
      c.execute('SELECT * FROM programs WHERE channel = ? AND start_date < ? AND end_date > ?', [chan, endTime, startTime])
      r = c.fetchall()
    
      for row in r:
        description_long = row['description_long']
        year = row['year']
        country = row['country']
        category =row['category']

        programList.append({
            'channel': row['channel'],
            'showID' : row['showID'],
            'title' : row['title'],
            'description' : row['description'],
            'description_long' : row['description'],
            'year': year, #row['year'],
            'genre': row['genre'],
            'country': country, #row['country'],
            'category': category, #row['category'],
            'start_date' : row['start_date'],
            'end_date' : row['end_date'],
            'image_small' : row['image_small'],
            'image_large': row['image_large']
            })

    c.close()
    return programList

  def getShowLongDescription(self, showID):
        info = self.conn.cursor()
        try:
            info.execute('SELECT * FROM programs WHERE showID= ? ', [showID])
        except:
            info.close()
            return None
        
        show = info.fetchone()
        longDesc = show['description']
        year = show['year']
        country = show['country']
        category = show ['category']
        series = show['series']
        
        info.close()
        return {'description':longDesc, 'year':year, 'country':country, 'category':category}
        
  def getShowInfo(self, showID, field='all'):
        if field!='all':
            showInfo = self.getShowLongDescription(showID)
            return showInfo[field]
            
        return showInfo

  def set_playing(self, channel=None, streams=None, streamNr=0):
    c = self.conn.cursor()
    c.execute('DELETE FROM playing')
    #c.execute('INSERT INTO playing(channel, start_date, action_time, current_stream,  streams) VALUES(?, ?, ?, ?, ?)', [channel, start, datetime.datetime.now(), streamNr, streams])
    c.execute('INSERT INTO playing(channel, current_stream,  streams) VALUES(?, ?, ?)', [channel, streamNr, streams])

    self.conn.commit()
    c.close()

  def get_playing(self):
    c = self.conn.cursor()
    c.execute('SELECT * FROM playing')
    row = c.fetchone()
    if row is not None:
      playing = {'channel':row['channel'], 'current_stream':row['current_stream'], 'streams':row['streams']}
    else:
      c.execute('SELECT * FROM channels ORDER BY weight ASC LIMIT 1')
      row = c.fetchone() 
      playing = {'channel':row['id'], 'start':datetime.datetime.now(), 'action_time':datetime.datetime.now()}
    c.close()
    return playing

  def set_currentStream(self, nr):
    c = self.conn.cursor()
    c.execute('UPDATE playing SET current_stream=?', [nr])
    self.conn.commit()
    c.close()

  def reloadDB(self):
    '''
    c = self.conn.cursor()
    c.execute('DELETE FROM updates')
    self.conn.commit()
    c.close()
    '''
    self._createTables()

    self.updateChannels(True)
    self.updateProgram(datetime.datetime.now(), True)
  
  
  def get_channeltitle(self, channelid):
    c = self.conn.cursor()
    c.execute('SELECT * FROM channels WHERE id= ? ', [channelid])
    row = c.fetchone()
    if row:
      channeltitle=row['title']
    self.conn.commit()
    c.close()
    return channeltitle 

  def get_channelid(self, channeltitle):
    c = self.conn.cursor()
    c.execute('SELECT * FROM channels WHERE title= ? ', [channeltitle])
    row = c.fetchone()
    print 'Title ' +str(channeltitle)
    if row:
      channelid=row['id']
    self.conn.commit()
    c.close()
    return channelid
  
  def get_channelweight(self, weight):
    c = self.conn.cursor()
    c.execute('SELECT * FROM channels WHERE weight= ? ', [weight])
    row = c.fetchone()
    if row:
      channelid=row['id']
    self.conn.commit()
    c.close()
    return channelid

  def getProgInfo(self, notify=False, startTime=datetime.datetime.now(), endTime=datetime.datetime.now()):
        fav = False
        if __addon__.getSetting('onlyfav') == 'true': fav = 'favorites'
        channels = self.getChannelList(fav)

        c = self.conn.cursor()
        print 'START Programm'
        # for startup-notify
        if notify:
            PopUp = xbmcgui.DialogProgressBG()
            #counter = len(channels)
            counter = 0
            for chan in channels['index']:
                c.execute('SELECT * FROM programs WHERE channel = ? AND start_date < ? AND end_date > ?', [chan, endTime, startTime])
                r=c.fetchall()
                for row in r:
                    counter += 1
            bar = 0         # Progressbar (Null Prozent)
            PopUp.create('ZattooBoxExt lade Programm Informationen ...', '')
            PopUp.update(bar)
        
        for chan in channels['index']:
            print str(chan) + ' - ' + str(startTime) 

            c.execute('SELECT * FROM programs WHERE channel = ? AND start_date < ? AND end_date > ?', [chan, endTime, startTime])
            r=c.fetchall()
        
            for row in r: 
                print str(row['channel']) + ' - ' + str(row['showID'])
                if notify:
                    bar += 1
                    percent = int(bar * 100 / counter) 
                description_long = row["description_long"]
                
                if description_long is None: 
                    print 'Lang ' + str(row['channel'])
                    if notify:
                        PopUp.update(percent,localString(31922), localString(31923) + str(row['channel']))
                    description_long = self.getShowLongDescription(row["showID"])
        c.close()
        if notify:
            PopUp.close()
        return 

  def cleanProg(self):
        d = (datetime.date.today() - datetime.timedelta(days=8))
        midnight = datetime.time(0)
        datelow = datetime.datetime.combine(d, midnight)
        print 'CleanUp  ' + str(datelow)
        c = self.conn.cursor()
        c.execute('SELECT * FROM programs WHERE start_date < ?', [datelow])
        r=c.fetchall()
        
        if len(r)>0:
            print 'Anzahl Records  ' + str(len(r))
            dialog = xbmcgui.Dialog()
            if dialog.yesno(localString(31918), str(len(r)) + ' ' + localString(31920), '', '',local(106),local(107)):
                nr=len(r)
                PopUp = xbmcgui.DialogProgress()
                counter=len(r)
                bar = 0         # Progressbar (Null Prozent)
                PopUp.create(localSring(31913), '')
                PopUp.update(bar)
                for row in r:
                    c.execute('DELETE FROM programs WHERE showID = ?', (row['showID'],))
                    bar += 1
                    percent = int(bar * 100 / counter)
                    PopUp.update(percent,  str(nr) + localString(31914))
                    if (PopUp.iscanceled()): 
                        c.close
                        return
                    nr -= 1
            PopUp.close() 

        self.conn.commit()
        c.close()
        return

  def formatDate(self, timestamp):
		if timestamp:
 			format = xbmc.getRegion('datelong')
 			date = timestamp.strftime(format)
 			date = date.replace('Monday', local(11))
 			date = date.replace('Tuesday', local(12))
 			date = date.replace('Wednesday', local(13))
 			date = date.replace('Thursday', local(14))
 			date = date.replace('Friday', local(15))
 			date = date.replace('Saturday', local(16))
 			date = date.replace('Sunday', local(17))
 			date = date.replace('January', local(21))
 			date = date.replace('February', local(22))
 			date = date.replace('March', local(23))
 			date = date.replace('April', local(24))
 			date = date.replace('May', local(25))
 			date = date.replace('June', local(26))
 			date = date.replace('July', local(27))
 			date = date.replace('August', local(28))
 			date = date.replace('September', local(29))
 			date = date.replace('October', local(30))
 			date = date.replace('November', local(31))
 			date = date.replace('December', local(32))
			return date
		else:
			return ''

  def getSeries(self, showID):
        c = self.conn.cursor()
        c.execute('SELECT series FROM programs WHERE showID = ?', [showID])
        series = c.fetchone()
        print str(showID)+'  '+str(series['series'])
        c.close()
        return series['series']
