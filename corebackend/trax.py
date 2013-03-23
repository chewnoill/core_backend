'''
Created on Jan 23, 2013

@author: will
'''

import unittest

import ConnectionManager
import TraxParser

class sessionHandler:
    def __init__(self,username,password):
        #setup connection manager
        self.CM = ConnectionManager.ConnectionManager("http://trax.meditech.com")
        
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
        self.state = TraxParser.parseInfo(response['content'])
        #depth first search of link tree

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


