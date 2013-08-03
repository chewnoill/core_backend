'''
Created on Jul 18, 2013

@author: will
'''
import ConnectionManager
import urllib
import CoreParser
version_number = 1
user_agent = "Will-s-Core-Trax-version-"+str(version_number)

class sessionHandler:
    def __init__(self,username,password,debug=False):
        self.debug = debug
        self.CPI = CoreParser.CoreParserInitial()
        
        #setup connection manager
        LINK="https://core.meditech.com"
        self.CM = ConnectionManager.ConnectionManager(LINK)
        
        #builds initial set of cookies
        self.CM.get("/core-coreWebHH.desktop.mthh")
        #post credentials        
        creds = {'sourl':'/core-coreWebHH.desktop.mthh',
                 'userid':username,
                 'password':password}
        response = self.CM.post("/signon.mthz",creds)
        self.state = response
        if 'redirect' in response:
            response = self.CM.get(response['redirect'])
            self.state = response
        self.CPI.feed(self.state['content'])
        self.initial_state = self.CPI.gather_response()
        if self.initial_state['error']:
            raise UnautherizedError(self.initial_state['error'])
    def lookup_person(self,lookup_key):
        response = self.CM.get(self.initial_state['links']['People'])
        CPP = CoreParser.CoreParserPerson()
        CPP.feed(response['content'])
        self.people_state = CPP.gather_response()
        
        data = {self.people_state['lookup']['name']:lookup_key}
        response = self.CM.post(self.people_state['lookup']['link'],data)
        
        CPP = CoreParser.CoreParserPerson()
        CPP.feed(response['content'])
        self.people_state = CPP.gather_response()
        if len(self.people_state['results'])==0:
            return {'type':'info',
                    'info':self.people_state['info']}
        else:
            return {'type':'results',
                    'results':self.people_state['results']}
        
    def get_events(self):
        
        self.event_states = {}
        if 'events' in self.initial_state:
            for link_name in self.initial_state['events']:
                event = self.CM.get(self.initial_state['events'][link_name])
                if self.debug:
                    self.event_states[link_name] = event['content']
                    continue
                
                CPE = CoreParser.CoreParserEvent(debug=self.debug)
                CPE.feed(event['content'])
                self.event_states[link_name] = CPE.gather_response()
        return self.event_states

class UnautherizedError(Exception):
    def __init__(self, message='', Errors=None):
        Exception.__init__(self, message)
        self.Errors = Errors
        
        