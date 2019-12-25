import re
import tele_util, lst, config
import time
import random
import requests
import json

REX_ZTT_ADD='\/zitat((.*)~\|~\s?(.*))?'
REX_ZTT='\/zitat\s(.*)?'

def zitat(msg):
    m = re.search(REX_ZTT_ADD, msg.txt)
    if m.group(1) != None:
        sql = '''
        INSERT INTO ztt (chat_id, autor, text, cts)
        value (%(chat_id)s, '%(at)s', '%(tx)s', '%(cts)s')
        '''
        data = {'chat_id': msg.getChatId(), 'at': m.group(3),'tx': m.group(2), 'cts': time.strftime('%Y-%m-%d %H:%M:%S')}
        tele_util.executeSQL(sql, data)
        msg.send(('%s ~|~ %s' % (m.group(2), m.group(3))))
        return "OK"
    m = re.search(REX_ZTT, msg.txt)
    if m != None:
        sql = """
        select concat(text, ' ~|~ ', autor) 
        from ztt 
        where chat_id=%(id)s 
        and lower(text) like '%%%(t)s%%' 
        or lower(autor) like '%%%s%%' 
        order by rand() limit 1" 
        """ % {'id': msg.getChatId(), 't': m.group(1).lower()}
        msg.send(tele_util.getOneSQL(sql))
    else:
        sql = """
        select 'm',concat(text, ' ~|~ ', autor) 
        from ztt 
        where chat_id=%s order by rand() limit 1""" % (msg.getChatId())
        msg.send(tele_util.getOneSQL(sql))

REX_LIST='\/list\s(del\s|rnd|)\s*(\S*)\s*(.*)?'
def list(msg):
    m = re.search(REX_LIST,msg.txt)
    if m == None:
        ls = lst.getAllLists(msg.getChatId())
    else:
        modus = m.group(1)
        name = m.group(2)
        entry = m.group(3)
        if len(modus) == 0 and len(entry) > 0:
            lst.addList(msg.getChatId(), name, entry)
        elif modus == 'del':
            lst.delList(msg.getChatId(), name, entry)
        elif modus == 'rnd':
            lst.rndList(msg.getChatId(), name)
        ls = lst.getList(msg.getChatId(), name)
    msg.send(('*%s:*\n[%s]' % (name, lst.prtList(ls))), parse_mode='Markdown')
   
rol_dec = {}
def roulette(msg):
    global rol_dec
    val = None
    if msg.getChatId() in rol_dec:
        t, val = rol_dec[msg.getChatId()]
        if time.strftime('%Y-%m-%d') != t:
            val = None
    if val == None:
        val = lst.rndList(msg.getChatId(), 'roulette')
        rol_dec[msg.getChatId()]=(time.strftime('%Y-%m-%d'), val)
    msg.send('*%s* hat /roulette am %s gewonnen!' % (val, time.strftime('%Y-%m-%d')), parse_mode='Markdown')
    url = getGiphy(val)
    if url:
        msg.send(url, typ='d')


def bit(msg):
    if random.randint(0,100) >= 40:
        msg.send('CgADBAADaAADDOAFUX2bfkqLEdVSFgQ', typ='d') # No
    else:
        msg.send('CgADBAADyJIAAhwXZAfKFg_xUcgLxRYE', typ='d') # Yes

def gif(msg):
    url = getGiphy(msg.txt)
    if url == None:
        url = getGiphy('otter')
    msg.send(url, typ='d', reply=True)
    
def tenor(msg):
    url = getTenor(msg.txt)
    if url == None:
        url = getTenor('sexy')
    msg.send(url, typ='d', reply=True)

def getGiphy(term):
    r = requests.get("http://api.giphy.com/v1/gifs/search?lang=de&api_key=%s&q=%s&rating=R&limit=1&offset=%s" \
                     % (config.apikeys['giphy'], term, random.randint(1,10)))
    if r.status_code == 200:
        jobj = json.loads(r.content)
        if 'data' in jobj and len(jobj['data'])>0:
            return jobj['data'][0]['images']["original"]["url"].replace('\/', '/')

def getTenor(term):
    r = requests.get("https://api.tenor.com/v1/random?key=%s&limit=1&q=%s&locale=de_GER" \
                     % (config.apikeys['tenor'], term))
    if r.status_code == 200:
        jobj = json.loads(r.content)
        if 'results' in jobj and len(jobj['results'])>0:
            return jobj['results'][0]["url"]


