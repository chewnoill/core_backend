'''
Created on Mar 23, 2013

@author: will
'''
from google.appengine.ext import db

class Menu(db.Model):
    name = db.StringProperty(required=True)
    JSONmenu = db.TextProperty()

class PathLookup(db.Model):
    arg1 = db.StringProperty(required=True)
    arg2 = db.StringProperty()
    path = db.StringProperty(required=True)
    
class stats(db.Model):
    type = db.StringProperty(required=True)
    user_agent = db.StringProperty(required=True)
    date = db.DateProperty(auto_now=True)
    time = db.DateTimeProperty(auto_now=True)
    username = db.StringProperty()
    what = db.StringProperty()    

def saveStat(user_agent,options):
    if 'type' in options:
        stat = stats(type=options['type'],
                     user_agent=user_agent)       
        if 'path' in options:
            stat.what = str(options['path'])
        if 'username' in options:
            stat.username = options['username']
            
        stat.put()
def saveError(user_agent,options):
    if 'error' in options:
        stat = stats(type='error',
                     what=options['error'],
                     user_agent=user_agent)
        stat.put()
    
def getStats():
    'not implemented'

def insertMenu(name,JSON):
    #check if exists already
    found = db.GqlQuery("select * from Menu where name='%s'" % name)
    db.delete(found)
    m = Menu(name=name)
    if(JSON):
        m.JSONmenu=JSON
    m.put()
    

def getMenu(name):
    found = db.GqlQuery("select * from Menu where name='%s'" % name)
    ret = found.get()
    if not ret==None:
        return ret.JSONmenu
    return ret

    
def insertPath(arg1,arg2,path):
    found = None
    if arg2:
        found = db.GqlQuery("select * from PathLookup where arg1='%s' and arg2='%s'" % (arg1,arg2))
    else:
        found = db.GqlQuery("select * from PathLookup where arg1='%s'" % arg1)
    
    for p in found.run(limit=50):
        p.delete()
    m = PathLookup(arg1=arg1,
                   path=path)
    if arg2:
        m.arg2=arg2
    m.put()
def getPath(arg1,arg2=None):
    found = None
    if arg2:
        found = db.GqlQuery("select * from PathLookup where arg1='%s' and arg2='%s'" % (arg1,arg2))
    else:
        found = db.GqlQuery("select * from PathLookup where arg1='%s'" % arg1)
    if found and found.get():
        return found.get().path