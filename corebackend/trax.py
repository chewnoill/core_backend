'''
Created on Jan 23, 2013

@author: will
'''

import unittest

import ConnectionManager
import TraxParser
import urllib

class sessionHandler:
    def __init__(self,username,password):
        #setup connection manager
        LINK="https://trax.meditech.com"
        self.CM = ConnectionManager.ConnectionManager(LINK)
        
        #builds initial set of cookies
        self.CM.get("/core-coreWeb.trax.mthr")
        #post credentials        
        creds = {'sourl':'/core-coreWeb.trax.mthr',
                 'userid':username,
                 'password':password}
        response = self.CM.post("/signon.mthz",creds)
        self.state = response
        #get redirection
        
        if 'redirect' in response:
            
            response = self.CM.get(response['redirect'])
        #print(response)
        
        #parse links from message
        #default page has "in" links and top nav bar [in, out, notes]
        #self.state = response
        self.content = response['content']
        self.state = TraxParser.parseInfo(response['content'])
        if len(self.state['error'])>0:
            raise UnautherizedError(self.state['error'])
        #depth first search of link tree
    def get(self,link):
        r = self.CM.get(self.state['links'][link])
        state = TraxParser.parseInfo(r['content'])
        if not (len(state['extra'])==0 and
                len(state['links'])==0):
            self.state=state
        return r['content']
    def post(self,link,data):
        r = self.CM.post(link,data)
        state = TraxParser.parseInfo(r['content'])
        return {'content':r['content'],
                'state':state}
    def getNotes(self):
        r = self.CM.get(self.state['links']['Note'])
        self.state = TraxParser.parseInfo(r['content'])
        
        return {'notes':self.state['notes'],
                'content':r['content']}
        
    def getStatus(self):
        #if I already have the status, don't get it again
        ret = {}
        
        if ('info' in self.state and 
            'status' in self.state['info'] and 
            'full_name' in self.state['info']):
            ret = self.state['info']
        else:
            r = self.CM.get(self.state['links']['In'])
            self.content = r['content']
            self.state = TraxParser.parseInfo(r['content'])
            ret = self.state['info']
        notes = self.getNotes()
        ret['notes'] = notes['notes']
        return ret
    
    def postPathSave(self,path,extra={}):
        self.buildState(path)
        data = None
        link = None
        ret = {}
        #get post name from state
        if 'extra' in self.state:
            for t in extra:
                if (t in self.state['extra'] and 
                    'name' in self.state['extra'][t]):
                    data = {}
                    data[self.state['extra'][t]['name']]=extra[t]
                if (t in self.state['extra'] and
                    'link' in self.state['extra'][t]):
                    link = self.state['extra'][t]['link']
                if (link and data):
                    ret = self.post(link,data)
                    link = None
                    data = None
        #click save... if you can
        if 'Save' in self.state['links']:
            #data['img-saveButton']='{78|44}'
            #return urllib.urlencode(data)
            ret = self.CM.get(self.state['links']['Save'])
            return {'saved':True}
        return {'error':'invalid path',
                'code':404}

    def postNotes(self,notes):
        path = ['Note']
        notes = (urllib.urlencode(notes) +
                 urllib.urlencode('<style type="text/css">\
                 body {\
                     background: #FFF;\
                     font-family: verdana;\
                     font-size: 75%;\
                     }\
                     </style>&img-saveButton={113|36}'))
        extra = {'note_form_name':notes}
        self.buildState(path)
        data = {}
        ret = {}
        #get post name from state
        if 'extra' in self.state:
            for t in extra:
                if (t in self.state['extra'] and 
                    'link' in self.state['extra'][t] and
                    'name' in self.state['extra'][t]):
                    data[self.state['extra'][t]['name']]=extra[t]
                    ret = self.CM.post(self.state['extra'][t]['link'],data)
        newState = {}
        if 'content' in ret:
            newState = TraxParser.parseInfo(ret['content'])
        newdat = {}
        if 'extra' in newState:
            for t in extra:
                if t in newState['extra']:
                    newdat[newState['extra'][t]['name']]=extra[t]
        if 'Save' in self.state['links']:
            #return urllib.urlencode(data)
            ret = self.CM.post(self.state['links']['Save'],data)
            if ret.status_code==200:
                return {'notes':notes}
            else:
                return {'error':'some error',
                        'code':404,
                        'detail': 'unknown'}
    def logOut(self):
        'ToDo'
    
    def buildMenu(self):
        ret = {}
        for item in globalMenus:
            if item in self.state['links']:
                #self.rebuildState([item])
                
                ret[item]=self.buildMenu_rec(item=item,
                                             path=[],
                                             depth=0)
            else:
                ret[item]='KeyError: link not found'
            
        return ret
    def buildMenu_rec(self,item,path,depth):
        if item in leaf or depth>2:
            return item
        
        #python will only pass links for lists which creates problems for 
        #recursive functions, must force a copy to be made leaving original 
        #as is
        path = list(path)+[item]
        try:
            self.buildState(path)
        except KeyError:
            return ['build state error',path]
        links = self.state['links']
        ret = {}
        if 'extra' in self.state:
            ret['extra']=self.state['extra'].copy()
        for link in links:
            if not link in globalMenus:
                ret[link] = self.buildMenu_rec(link,path,depth+1)

        return ret
        
        
                
    def buildState(self,path):
        for item in path:
            if item == 'Save':
                #dont save here
                return
            r = self.CM.get(self.state['links'][item])
            newState = TraxParser.parseInfo(r['content'])
            if len(newState['links'])>0:
                self.state = newState
    def load(self,link):
        if link in self.state['links']:
            r = self.CM.get(self.state['links'][link])
            newState = TraxParser.parseInfo(r['content'])
            if len(newState['links'])>0:
                self.state = newState
            return r
        else:
            return 'link not found'
        

class UnautherizedError(Exception):
    def __init__(self, message='', Errors=None):
        Exception.__init__(self, message)
        self.Errors = Errors
        
        
class StateError(Exception):  
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)  
    
globalMenus = ['In','Out','Note']
leaf = ['Save']


    
                


