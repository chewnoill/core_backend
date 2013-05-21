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
        #local GAE won't get https connection
        self.CM = ConnectionManager.ConnectionManager("https://trax.meditech.com")
        
        #builds initial set of cookies
        self.CM.get("/core-coreWeb.trax.mthr")
        #post credentials        
        creds = {'sourl':'/core-coreWeb.trax.mthr',
                 'userid':username,
                 'password':password}
        try:
            response = self.CM.post("/signon.mthz",creds)
            self.state = response
            #get redirection
            
            if 'redirect' in response:
                response = self.CM.get(response['redirect'])
            #print(response)
            
            #parse links from message
            #default page has "in" links and top nav bar [in, out, notes]
            #self.state = response
            self.state = TraxParser.parseInfo(response['content'])
            #depth first search of link tree
        except DeadlineExceededError:
            self.state = {'error':'timed out',
                          'detail':'timed out trying to connect to https://trax.meditech.com/signon.mthz'}
        
    def getNotes(self):
        r = self.CM.get(self.state['links']['Note'])
        self.state = TraxParser.parseInfo(r['content'])
        
        return {'notes':self.state['notes']}
        
    def getStatus(self):
        #if I already have the status, don't get it again
        if ('info' in self.state and 
            'status' in self.state['info'] and 
            'full_name' in self.state['info']):
            return self.state['info']
        r = self.CM.get(self.state['links']['In'])
        self.state = TraxParser.parseInfo(r['content'])
        
        return self.state['info']
    
    def postPathSave(self,path,extra={}):
        self.buildState(path)
        data = {}
        #get post name from state
        if 'extra' in self.state:
            for t in extra:
                if t in self.state['extra']:
                    data[self.state['extra'][t]['name']]=extra[t]
                
        ret = self.CM.post(self.state['extra'][t]['link'],data)
        #after extra data is saved, the data form names may be updated
        #update data with new form names
        newState = TraxParser.parseInfo(ret['content'])
        newdat = {}
        if 'extra' in newState:
            for t in extra:
                if t in newState['extra']:
                    newdat[newState['extra'][t]['name']]=extra[t]
        if len(newdat)>0:
            data = newdat
        #update self.state also?    
        #probably not, links are not reset
        if 'Save' in self.state['links']:
            data['img-saveButton']='{78|44}'
            #return urllib.urlencode(data)
            ret = self.CM.post(self.state['links']['Save'],data)
            return ret
        return {'error':'invalid path',
                'code':404}

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
        

    
class StateError(Exception):  
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)  
    
globalMenus = ['In','Out','Note']
leaf = ['Save']

if __name__ == "__main__":
    uname = ''
    password = ''
    sh = sessionHandler(uname,password)
    sh.buildMenu()
    
                


