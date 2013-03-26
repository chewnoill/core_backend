'''
Created on Feb 10, 2013
    Google App Engine connection manager
@author: will
'''
import unittest
#gae package
import google.appengine.api.urlfetch as urlfetch

try:
    import urllib.parse as urle #@UnusedImport@UnresolvedImport
except:
    #for python pre 2.7
    import urllib as urle
version_number = 1
user_agent = "Will-s-Core-Trax-version-"+str(version_number)

class ConnectionManager:
    def __init__(self,link):
        self.cookies = cookie_manager()
        self.url = link
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": user_agent}
        
    def post(self,target,data):
        #print('post target',target)
        params = urle.urlencode(data)
        self.headers['cookie']=self.cookies.getCookies()
        self.redirect = None
        
        r1 = urlfetch.Fetch(url = self.url+target,
                            payload = params,
                            method="POST",
                            headers = self.headers,
                            allow_truncated = False,
                            follow_redirects = False,
                            validate_certificate = True)
        headers = r1.header_msg
        self.process_headders(headers)
        return self.gather_response(r1)
    def get(self,target):
        self.headers['cookie']=self.cookies.getCookies()
        #print('get target',target)
        self.redirect = None
        r1 = urlfetch.Fetch(url = self.url+target,
                            payload = {},
                            method="GET",
                            headers = self.headers,
                            allow_truncated = False,
                            follow_redirects = False,
                            validate_certificate = True)
        headers = r1.header_msg
        self.process_headders(headers)

        return self.gather_response(r1)
    def gather_response(self,response):
        ret = {}
        ret['content']=response.content
        ret['status']=response.status_code
        if self.redirect:
            ret['redirect']=self.redirect
        return ret
    def process_headders(self,header_msg):
        if 'location' in header_msg:
            redirect = header_msg['location']
            if redirect[0]==".":
                redirect = redirect[1:]
            self.redirect = redirect
        
        cookies = header_msg.getheaders('set-cookie')
        for cookie in cookies:
            self.cookies.add_cookie(cookie)
class cookie_manager:
    def __init__(self):
        self.cookies={}
    def add_cookie(self,image):
        t = image.split(',')
        for c in t:
            u = c.split(';')
            primary = u[0].split('=')
            rest = {}
            for x in range(1,len(u)):
                secondary = u[x].split("=")
                a = secondary[0]
                b = u[x][len(a):]
                rest[a.strip()] = b.strip()
            a = primary[0].strip()
            b = primary[1].strip()
            self.cookies[a]=cookie(a,b,rest)
            
    
    def getCookies(self):
        '''get current cookie state'''
        ret = ''
        for key in self.cookies.keys():
            ret += self.cookies[key].__str__()+', '
        return ret[:len(ret)-2]
    def __str__(self):
        return self.getCookies()
                
class cookie:
    def __init__(self,key,value,extra={}):
        #print('new cookie: '+key+":"+value)
        self.key = key
        self.value = value
        self.image = extra
        
        
    def __str__(self):
        ret = self.key+'='+self.value
        for key in self.image.keys():
            ret += "; "+key+"="+self.image[key]
        return ret

class Test(unittest.TestCase):
    def test1(self):
        
        
        CM = cookie_manager()
        CM.add_cookie('abc=123; just=talkn; bout=u+me, 123=abc')
        CM.add_cookie('123=456')
        print(CM)
    
        pass
    def test2(self):
        CM = cookie_manager()
        CM.add_cookie('abc=123; just=talkn; bout=me')
        CM.add_cookie('123=456')
        print(CM)
        
        pass
if __name__ == "__main__":
    unittest.main()
    
    