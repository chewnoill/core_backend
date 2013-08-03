'''
Created on Mar 21, 2013

@author: will
'''
import webapp2
import json
import trax
import core
import DataStore
from google.appengine import runtime
#from google.appengine.runtime import DeadlineExceededError as runDeadlineExceededError
#import DeadlineExceededError as apiDeadlineExceededError
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, webapp2 World!')
    def post(self):
        callback = self.request.GET.get('callback')
        
        input_fields = {}
        error = False
        ret = error_msg = {'error':'an error has occurred!',
                           'code':400,
                           'detail':'unknown error'}#default error message
        userAgent = 'unknown user agent'
        if 'User-Agent' in self.request.headers:
            userAgent = self.request.headers['User-Agent']
        elif 'user-agent' in self.request.headers:
            userAgent = self.request.headers['user-agent']
        try:
            input_fields = json.loads(self.request.body)
        except ValueError:
            error_msg['code']=400
            error_msg['detail']='invalid input'
            error_msg['error']='bad input'
            error = True
       
        
        if error:
            'do nothing'
        elif (has_required(['type'],input_fields)['has_required'] and
              input_fields['type'] in types):
                
            #check for missing fields
            check = has_required(types[input_fields['type']]['required_fields'],
                                 input_fields)
            if check['has_required']:
                #go go go
                
                try:
                    ret = types[input_fields['type']]['function'](input_fields)
                    
                except runtime.DeadlineExceededError:
                    error_msg={'code':404,
                               'detail':'trax.meditech.com took to long to respond',
                               'error':'DeadlineExceededError'}
                    error = True
                except runtime.apiproxy_errors.DeadlineExceededError:
                    error_msg={'code':404,
                               'detail':'trax.meditech.com took to long to respond',
                               'error':'DeadlineExceededError'}
                    error = True
                except Exception,e:
                    error_msg={'code':404,
                               'detail':str(e),
                               'error':'UnknownError'}
                    error = True
                
            else:
                error_msg = {'code':404,
                             'detail':'missing required field(s): '+str(check['missing_fields']),
                             'error':'missing required'}
                error = True
        else:
            
            error_msg['code']=404
            error_msg['detail']='missing required field: type'
            error_msg['error']='missing required'
            error = True
        
        try:
            if callback:
                self.response.out.write(callback+'(')
            
            if error:
                #DataStore.saveError(userAgent,error_msg)
                msg = json.dumps(error_msg)
            else:
                #msg = str(ret)
                #DataStore.saveStat(userAgent,input_fields)
                msg = json.dumps(ret,encoding='ISO-8859-1')
            self.response.out.write(msg)
            if callback:
                self.response.out.write(')')
        except UnicodeDecodeError:
            raise Exception("UnicodeDecodeError: "+str(ret))


def get_status(data):
    #-----------------------------
    #required fields
    username = data['username']
    password = data['password']
    traxSession = None
    try:
        traxSession = trax.sessionHandler(username,password)
    except trax.UnautherizedError, e:
        return {'error':'UnautherizedError',
                'detail':e.message}
    except KeyError:
        return {'code':404,
                'detail':'trax.meditech.com returned an unexpected result',
                'error':'parsing error'}
    #-----------------------------
    ret = traxSession.state
    return traxSession.getStatus()
def get_notes(data):
    #-----------------------------
    #required fields
    username = data['username']
    password = data['password']
    traxSession = None
    try:
        traxSession = trax.sessionHandler(username,password)
    except trax.UnautherizedError, e:
        return {'error':'trax.UnautherizedError',
                'detail':e.message}
    except KeyError:
        return {'code':404,
                'detail':'trax.meditech.com returned an unexpected result',
                'error':'parsing error'}
    #-----------------------------
    
    return traxSession.getNotes()
def set_status(data):
    #-----------------------------
    #required fields
    username = data['username']
    password = data['password']
    path = data['path']
    #-----------------------------
    traxSession = None
    try:
        traxSession = trax.sessionHandler(username,password)
    except trax.UnautherizedError, e:
        return {'error':'trax.UnautherizedError',
                'detail':e.message}
    except KeyError:
        return {'code':404,
                'detail':'trax.meditech.com returned an unexpected result',
                'error':'parsing error'}
    ret = traxSession.state
    
    extra = {}
    if 'extra' in data:
        extra = data['extra']
    
    ret = traxSession.postPathSave(path,extra)
    return ret 

def set_notes(traxSession,data):
    #-----------------------------
    #required fields
    username = data['username']
    password = data['password']
    traxSession = None
    try:
        traxSession = trax.sessionHandler(username,password)
    except trax.UnautherizedError, e:
        return {'error':'trax.UnautherizedError',
                'detail':e.message}
    except KeyError:
        return {'code':404,
                'detail':'trax.meditech.com returned an unexpected result',
                'error':'parsing error'}
    #-----------------------------
    
    notes = None
    if 'notes' in data:
        ret = traxSession.postNotes(notes)
        return ret 
    else:
        return {'error':'incomplete message'}

def lookup_person(data):
    #-----------------------------
    #required fields
    username = data['username']
    password = data['password']
    lookup_key = data['lookup_key']
    coreSession = None
    try:
        coreSession = core.sessionHandler(username,password)
    except core.UnautherizedError, e:
        return {'error':'core.UnautherizedError',
                'detail':e.message}
    #-----------------------------
    return coreSession.lookup_person(lookup_key)

def list_events(data):
    #-----------------------------
    #required fields
    username = data['username']
    password = data['password']
    coreSession = None
    try:
        coreSession = core.sessionHandler(username,password)
    except core.UnautherizedError, e:
        return {'error':'core.UnautherizedError',
                'detail':e.message}
    #-----------------------------
    return coreSession.get_events()

def build_menu(data):
    #-----------------------------
    #required fields
    username = data['username']
    password = data['password']
    traxSession = None
    try:
        traxSession = trax.sessionHandler(username,password)
    except trax.UnautherizedError, e:
        return {'error':'UnautherizedError',
                'detail':e.message}
    except KeyError:
        return {'code':404,
                'detail':'trax.meditech.com returned an unexpected result',
                'error':'parsing error'}
    #-----------------------------
    
    #This takes a long time, probably shouldn't do it very often
    MenuObj = traxSession.buildMenu()
    
    #save results to GAE Datastore
    ret = json.dumps(MenuObj)
    DataStore.insertMenu('menu', ret)
    
    return ret
    

def get_menu_no_id(data = None):
    ret = DataStore.getMenu('menu')
    
    if not ret:
        ret = {'error':'no menu',
               'code':404,
               'detail': 'no menu found, must be rebuilt'}
        return ret
    else:
        return json.loads(ret)
def buildReversePathLookup():
    menu = get_menu_no_id()
    if 'error' in menu:
        return menu
    
    else:
        dontcare=['Save']
        
        for o in menu:
            for p in menu[o]:
                if p not in dontcare:
                    DataStore.insertPath(arg1 = p,
                                         arg2 = None,
                                         path = json.dumps([o,p]))
                    #print('itm: %s %s' % (p,[o,p]))
                    for q in menu[o][p]:
                        if q not in dontcare:
                            tq = ''
                            if q == 'extra':
                                tq = menu[o][p][q].keys()[0]
                            else:
                                tq = q
                            print (p,tq,json.dumps([o,p,tq]))
                            DataStore.insertPath(arg1 = p,
                                                 arg2 = tq,
                                                 path = json.dumps([o,p,tq]))
                            #print('\titm: %s %s' % (q,[o,p,q]))

def has_required(required_fields,input_fields):
    missing_fields = []
    
    for field in required_fields:
        if not field in input_fields:
            missing_fields += [field]
            
    if len(missing_fields)==0:
        return {'has_required':True}
    else:
        return {'has_required':False,
                'missing_fields':missing_fields}

def not_implemented(data):
    ret = {'error': 'not found',
           'detail': 'not implemented, try again later',
           'code': 404}
    return ret

#dispatch dictionary
types = {'get_status': {'required_fields':['username','password'],
                        'function':get_status},
         'get_notes': {'required_fields':['username','password'],
                       'function':get_notes},
         'set_status': {'required_fields':['username','password','path'],
                        'function':set_status},
         'set_notes': {'required_fields':['username','password'],
                       'function':not_implemented},
         'list_events': {'required_fields':['username','password'],
                         'function':list_events},
         'lookup_person': {'required_fields':['username','password','lookup_key'],
                           'function':lookup_person},
         'build_menu':{'required_fields':['username','password'],
                       'function':not_implemented},
         'get_menu':{'required_fields':[],
                     'function':get_menu_no_id}}
         
app = webapp2.WSGIApplication([('/handler.html', MainPage)],
                              debug=True)
