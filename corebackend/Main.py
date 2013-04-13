'''
Created on Mar 21, 2013

@author: will
'''
import webapp2
import json
import trax as trax
import DataStore


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, webapp2 World!')
    def post(self):
        callback = self.request.GET.get('callback')
        
        input = ''
        error = False
        ret = error_msg = {'error':'an error has occurred!'}#default error message
        
        try:
            
            input = json.loads(self.request.body)
        except ValueError:
            error_msg['code']=400
            error_msg['message']='invalid input'
            error_msg['error']='bad input'
            error = True

        
        if error:
            'do nothing'
        elif 'username' in input and 'password' in input:
            username = input['username']
            password = input['password']
            if len(username)==0 or len(password)==0:
                error_msg['code']=401
                error_msg['detail']='username and password required'
                error_msg['error']='unauthorized'
                error = True
            elif 'type' in input:
                if input['type'] in types:
                    #go go go
                    traxSession = trax.sessionHandler(username,password)
                    ret = traxSession.state
                    
                    if ret['error']=='Invalid username/password, try again.':
                        #oops, one more error
                        error_msg['code']=401
                        error_msg['detail']='username/password rejected'
                        error_msg['error']='unauthorized'
                        error = True
                    else:
                        #dispatch to do stuff
                        ret = types[input['type']](traxSession,input)
                        #check for more errors
                else:
                    error_msg['code']=404
                    error_msg['detail']='unknown type: '+input['type']
                    error_msg['error']='bad input'
                    error = True
            else:
                error_msg['code']=400
                error_msg['detail']='missing type'
                error_msg['error']='bad input'
                error = True
        else:
            if 'type' in input and input['type']=='get_menu':
                ret = getMenu_no_id()
            else:
                #return error
                error_msg['code']=401
                error_msg['detail']='username and password required'
                error_msg['error']='unauthorized'
                error = True
        
        if callback:
            self.response.out.write(callback+'(')
        
        if error:
            msg = json.dumps(error_msg)
        else:
            #msg = str(ret)
            msg = json.dumps(ret)
        self.response.out.write(msg)
        if callback:
            self.response.out.write(')')


def getStatus(traxSession,data):
    return traxSession.getStatus()
def getNotes(traxSession,data):
    return traxSession.getNotes()
def setStatus(traxSession,data):
    extra = {}
    path = []
    if 'path' in data:
        path = data['path']
    else:
        #no path, return error
        ret = {'error':'no path',
               'code':404,
               'detail': 'no path recieved, malformed data'}
        return ret
    if 'extra' in data:
        extra = data['extra']
    
    ret = traxSession.postPathSave(path,extra)
    return ret 

def setNotes(traxSession,data):
    'TODO'
def buildMenu(traxSession,data):
    #This takes a long time, probably shouldn't do it very often
    MenuObj = traxSession.buildMenu()
    
    #save results to GAE Datastore
    ret = json.dumps(MenuObj)
    DataStore.insertMenu('menu', ret)
    
    return ret
    
def getMenu(traxSession,data):
    ret = DataStore.getMenu('menu')
    
    if not ret:
        ret = buildMenu(traxSession,data)
    return json.loads(ret)
def getMenu_no_id():
    ret = DataStore.getMenu('menu')
    
    if not ret:
        ret = {'error':'no menu',
               'code':404,
               'detail': 'no menu found, must be rebuilt'}
        return ret
    else:
        return json.loads(ret)
def buildReversePathLookup():
    menu = getMenu_no_id()
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



def notImplemented(traxSession,data):
    ret = {'error': 'not found',
           'detail': 'not implemented, try again later',
           'code': 404}
    return ret
    
#dispatch dictionary
types = {'get_status': getStatus,
         'get_notes': getNotes,
         'set_status': setStatus,
         'set_notes': notImplemented,
         'list_events': notImplemented,
         'find_person': notImplemented,
         'build_menu':notImplemented,
         'get_menu':getMenu}
         
app = webapp2.WSGIApplication([('/handler.html', MainPage)],
                              debug=True)
