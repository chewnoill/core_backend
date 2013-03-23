'''
Created on Mar 21, 2013

@author: will
'''
import webapp2
import json
import corebackend.trax as trax

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
            input = json.loads(self.request.POST.items()[0][0])
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
    'TODO'
def setNotes(traxSession,data):
    'TODO'
def notImplemented(traxSession,data):
    ret = {'detail': 'not implemented, try again later',
           'code': 404}
    return ret
    
#dispatch dictionary
types = {'get_status': getStatus,
         'get_notes': getNotes,
         'set_status': notImplemented,
         'set_notes': notImplemented,
         'list_events': notImplemented,
         'find_person': notImplemented}
         
app = webapp2.WSGIApplication([('/handler.html', MainPage)],
                              debug=True)