'''
Created on Feb 10, 2013

@author: will
'''
from HTMLParser import HTMLParser #@UnresolvedImport@UnusedImport
import re
import pprint
import unittest


info_id = {'z0-00_inBody-0-4-0-0s':'status',
        'z0-00_outBody-0-4-0-0s':'status',
        'z0-00_noteBody-0-4-0-1s':'status',
        'z0-00_inBody-0-1-0-1s':'full_name',
        'z0-00_outBody-0-1-0-1s':'full_name',
        'z0-00_noteBody-0-1-0-2s':'full_name'}

select_id = {'z0-00_dateBody-0-6-0-0s':'date_select_name',
             'z0-00_summaryBody-0-6-0-2_0i':'phone_ext_name'}
select = {'date':'z0-00_dateBody-0-6-0-0s',
          'phone':'z0-00_summaryBody-0-6-0-2_0i'}
def parseInfo(page,debug=False):
    #returns a dictionary of all links found
    tp = TraxInfoParser(debug=debug)
    tp.feed(page)
    ret =  {"links":tp.gather_links(),
            "info":tp.gather_info(),
            "extra":tp.getExtra(),
            "notes":tp.notes,
            "error":tp.gather_error()}
    
    if debug:
        ret['tags']=tp.tags

    return ret

class TraxInfoParser(HTMLParser):
    def __init__(self,debug=False):
        self.debug = debug
        HTMLParser.__init__(self)
        self.links = {}
        self.info = {}
        self.tags = {}
        self.gather_notes = False
        self.notes = ''
        self.error = ''
        self.obj={}
        self.parent=''
        self.dateSelect = False
        self.phoneExtInput = False
        self.note_form = False
    def getExtra(self):
        ret = {}
        for s in select_id:
            if s in self.tags:
                ret[select_id[s]]={'name':self.tags[s]['name'],
                                   'link':self.tags[s]['link']}
        return ret

    def gather_links(self):
        links = {}
        for tag in self.tags:
            if 'alt' in self.tags[tag]:
                if 'link' in self.tags[tag]:
                    links[self.tags[tag]['alt']]=self.tags[tag]['link']
                elif 'link' in self.tags[self.tags[tag]['parent']]:
                    links[self.tags[tag]['alt']]=self.tags[self.tags[tag]['parent']]['link']
        return links
    def gather_error(self):
        if 'message' in self.tags:
            return self.tags['message']['data']
        
    def gather_info(self):
        info = {}
        for i in info_id:
            if i in self.tags:
                t = self.tags[i]['data']
                t = filter(lambda x: not x in '\r\n\t', t)
                info[info_id[i]]=t
        return info
    def gather_error(self):
        if 'message' in self.tags:
            return self.tags['message']['data']
        return ''
    def convert_attrs(self,attrs):
        ret = {}
        for a in attrs:
            ret[a[0]]=a[1]
        return ret
    def handle_starttag(self, tag, attrs):
        if self.debug:
            print('start tag %s' % tag)
        if self.gather_notes:
            note = '<'+tag
            for a in attrs:
                note += ' '+a[0]+'="'+a[1]+'"'
            note += '>'
            self.notes+=note
            return
        self.obj = {}
        self.obj['tag']=tag
        self.obj['parent']=self.parent
        
        attr = self.convert_attrs(attrs)
        
        if self.debug:
            print('start tag attrs %s' % str(attr))
        if 'alt' in attr:
            self.obj['alt']=attr['alt']
        if 'id' in attr:
            self.obj['id']=attr['id']
        if 'name' in attr:
            self.obj['name']=attr['name']
        if 'id' in self.obj:
            if not tag == 'img':
                self.parent = self.obj['id']
            self.tags[self.obj['id']]=self.obj
        
    def handle_endtag(self, tag):
        if self.debug:
            print('end tag: %s' % tag)
        
        if self.gather_notes:
            note = '</'+tag+'>'
            self.notes+=note
            return
        if (not tag == 'img' and
            'parent' in self.obj):
            self.parent = self.obj['parent']

        self.obj = {}
        

    def handle_data(self, data):
        if self.debug:
            print 'handling data: %s' %data
            print(self.obj)
        if (('tag' in self.obj and 
             self.obj['tag']=='script') or
            len(self.obj)==0):
            self.handle_script_data(data)
        elif 'id' in self.obj:
            if 'data' in self.tags[self.obj['id']]:
                self.tags[self.obj['id']]['data']+=data
            else:
                self.tags[self.obj['id']]['data']=data

        if self.gather_notes:
            self.notes += data
        start_note_body = not data.find('newrichtext') == -1
        if start_note_body:
            s = data.split('|')
            self.note_form_name = s[1]
            self.note_form = True
            self.gather_notes = True
        
    def handle_script_data(self,data):
        if self.debug:
            print('handle_script_data')
        u = data.split('updeventhooks')
        if len(u)>1:
            self.gather_notes = False
        if self.debug:
            for v in u:
                print(v)
        reg_ex = ('(?P<before>.*?)'+
                  '((%7F)|\x7f)(?P<item_id>.*?)((%7F)|\x7f)'+
                  '(?P<garbage>.*?)'+
                  '\.(?P<link>/.*?\.mthd)'+
                  '(?P<after>.*?)')
        for v in u:
            result = re.search(reg_ex,v)
            if result:
                id = result.group('item_id')
                link = result.group('link')
                if id in self.tags:
                    self.tags[id]['link']=link
                elif id and link:
                    self.tags[id]={}
                    self.tags[id]['link']=link
            

    def __str__(self):
        return str(self.ret)

class Test(unittest.TestCase):
    def test_landing(self):
            
        t = '<!DOCTYPE html>\r\n<html lang=\"en\">\r\n<head>\r\n<title>Mobile Trax</title>\r\n<script type=\"text/javascript\" src=\"./system/jquery/jquery.js\"></script>\r\n<script type=\"text/javascript\" src=\"./system/scripts/main.js\"></script>\r\n<script type=\"text/javascript\">\r\n<!--\r\n  window.onbeforeunload = confirmExit;\r\n//-->\r\n</script>\r\n<style type=\"text/css\">\r\n.row {width:100%;\r\n      overflow:auto;\r\n      clear:both;}\r\n.component {position:relative;}\r\n.clickable {cursor:pointer;}\r\n.popupcalendarlink {cursor:default;\r\n                    border-color:#000;\r\n                    text-align:center; font-weight: 700;\r\n                    color: blue;}\r\n.popupcalendarheader { background: #ddf; }\r\n.popupcalendarhover { background: #ddf; }\r\nbody { margin:0; padding:0; font-family:Verdana,Helvetica,Arial,sans-serif;}\r\n@media screen {\r\n .regioncontainer {\r\n    width:100%; height:100%;\r\n    top:0; left:0;\r\n    position:absolute;\r\n    padding:0; margin:0;\r\n }\r\n}\r\n@media print {\r\n .regioncontainer {\r\n\r\n    padding:0; margin:0;\r\n }\r\n}\r\n.sysnormaltext {color:black; font-style:normal;}\r\n.sysoverridegraytext {color:gray; font-style:italic;}\r\n.sysoverridegraytextselect {color:gray;}\r\n.link {cursor:pointer;}\r\ndiv.popupshield {width:100%; height:100%;\r\n                 background:#000;\r\n                 position:absolute; margin:0; border:none; padding:0; top:0; left:0;\r\n                 opacity:0.2; filter:alpha(opacity=20);}\r\ndiv.popupshield2 {width:100%; height:100%;\r\n                  background:#000;\r\n                  position:absolute; margin:0; border:none; padding:0; top:0; left:0;\r\n                  opacity:0.0; filter:alpha(opacity=0);}\r\ndiv.popupouter {position:absolute; height:auto;\r\n                border:1px solid black;\r\n                background:#fff;}\r\ndiv.popupheader {background:#4040e0; color:white;\r\n                 margin:0; padding:2px;}\r\ndiv.popupbody {margin:0; padding:5px;}\r\ntable {word-wrap:break-word;}\r\n.style0 {font-size:medium; overflow-x:hidden; overflow-y:hidden;}\r\n.style1 {bottom:0; font-size:medium; left:0; margin:0; overflow-x:hidden; overflow-y:hidden; padding:0; position:absolute; right:0; top:0; width:100%;}\r\n.style2 {-webkit-overflow-scrolling:touch; bottom:0; font-size:medium; left:0; margin:0; overflow-y:auto; padding:0; position:absolute; right:0; top:0; width:100%;}\r\n.style3 {float:left; width:100%;}\r\n.style4 {text-align:center; vertical-align:middle;}\r\n.style5 {width:auto;}\r\n.style6 {margin-left:auto; margin-right:auto; display:block;}\r\n.style7 {text-align:center; vertical-align:middle; font-size:x-small;}\r\n.style8 {margin-left:auto; margin-right:auto;}\r\n.style9 {border-left:none; border-right:none; border-top:none;}\r\n.style10 {border-bottom:none; border-left:none; border-right:none; border-top:none;}\r\n</style>\r\n</head>\r\n<body id=\'body\'onload=\'BodyOnLoad();\'>\r\n<div id=\"regioncontainer-0\" class=\"regioncontainer style0\">\r\n<div id=\"arrangement-0-0\" class=\"style1\">\r\n<div id=\"z0-00_inBody\" class=\"style2\">\r\n<div class=\"style3\">\r\n<div id=\"z0-00_inBody-0-1\" class=\"row\">\r\n<div id=\"z0-00_inBody-0-1-0\" style=\"float:left;width:99.000%;\">\r\n<div id=\"z0-00_inBody-0-1-0-0\" class=\"component\">\r\n<style type=\"text/css\">@media screen and (min-width: 1px) {img.clickable {width:60px;height:60px;}img.style6 {width:60px;height:30px;}}@media screen and (min-width: 320px) {img.clickable {width:90px;height:81px;}img.style6 {width:90px;height:45px;}}@media screen and (min-width: 360px) {img.clickable {width:110px;height:99px;}img.style6 {width:108px;height:54px;}}@media screen and (min-width: 640px) {img.clickable {width:130px;height:117px;}img.style6 {width:130px;height:65px;}}@media screen and (min-width: 800px) {img.clickable {width:150px;height:135px;}img.style6 {width:150px;height:75px;}}@media screen and (min-width: 960px) {img.clickable {width:170px;height:153px;}img.style6 {width:170px;height:85px;}}@media screen and (min-width: 1120px) {img.clickable {width:190px;height:171px;}img.style6 {width:190px;height:95px;}}</style></div>\r\n <div id=\"z0-00_inBody-0-1-0-1\" class=\"component style4\">\r\n  <span id=\"z0-00_inBody-0-1-0-1s\" class=\"style4\">William Cohen</span>\r\n </div>\r\n</div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-2\" class=\"row\">\r\n<div id=\"z0-00_inBody-0-2-0\" style=\"float:left;width:99.000%;\">\r\n<div id=\"z0-00_inBody-0-2-0-0\" class=\"component\">\r\n<div style=\"height:0.5em;\" class=\"component\"></div></div>\r\n</div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-3\" class=\"row\">\r\n<div id=\"z0-00_inBody-0-3-0\" style=\"float:left;width:4.950%;\">\r\n <div id=\"z0-00_inBody-0-3-0-0\" style=\"height: 1.5em;\" class=\"component\"></div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-3-1\" style=\"float:left;width:29.700%;\">\r\n <div id=\"z0-00_inBody-0-3-1-0\" class=\"component style4 link clickable\">\r\n  <div id=\"z0-00_inBody-0-3-1-0-img\" tabindex=\"0\"\r\n class=\"style5\"\r\n>\r\n<img src=\"/pub/traxImages/inblue.png\"\r\n             class=\"style6 \"\r\n             name=\"img-inButton\"\r\n             id=\"z0-00_inBody-0-3-1-0-imgI\"\r\n             alt=\"In\"\r\n             title=\"In\">\r\n</div>\r\n </div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-3-2\" style=\"float:left;width:29.700%;\">\r\n <div id=\"z0-00_inBody-0-3-2-0\" class=\"component style4 link clickable\">\r\n  <div id=\"z0-00_inBody-0-3-2-0-img\" tabindex=\"0\"\r\n class=\"style5\"\r\n>\r\n<img src=\"/pub/traxImages/outblack.png\"\r\n             class=\"style6 \"\r\n             name=\"img-outButton\"\r\n             id=\"z0-00_inBody-0-3-2-0-imgI\"\r\n             alt=\"Out\"\r\n             title=\"Out\">\r\n</div>\r\n </div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-3-3\" style=\"float:left;width:29.700%;\">\r\n <div id=\"z0-00_inBody-0-3-3-0\" class=\"component style4 link clickable\">\r\n  <div id=\"z0-00_inBody-0-3-3-0-img\" tabindex=\"0\"\r\n class=\"style5\"\r\n>\r\n<img src=\"/pub/traxImages/notesblack.png\"\r\n             class=\"style6 \"\r\n             name=\"img-noteButton\"\r\n             id=\"z0-00_inBody-0-3-3-0-imgI\"\r\n             alt=\"Note\"\r\n             title=\"Note\">\r\n</div>\r\n </div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-3-4\" style=\"float:left;width:4.950%;\">\r\n <div id=\"z0-00_inBody-0-3-4-0\" style=\"height: 1.5em;\" class=\"component\"></div>\r\n</div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-4\" class=\"row\">\r\n<div id=\"z0-00_inBody-0-4-0\" style=\"float:left;width:99.000%;\">\r\n <div id=\"z0-00_inBody-0-4-0-0\" class=\"component style4\">\r\n  <span id=\"z0-00_inBody-0-4-0-0s\" class=\"style7\">Out for the day, returning Tue Jul 02 2013</span>\r\n </div>\r\n</div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-5\" class=\"row\">\r\n<div id=\"z0-00_inBody-0-5-0\" style=\"float:left;width:99.000%;\">\r\n<div id=\"z0-00_inBody-0-5-0-0\" class=\"component\">\r\n<div style=\"height:0.5em;\" class=\"component\"></div></div>\r\n</div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-6\" class=\"row\">\r\n<div id=\"z0-00_inBody-0-6-0\" style=\"float:left;width:99.000%;\">\r\n<div id=\"z0-00_inBody-0-6-0-0\" class=\"component\">\r\n<table cellspacing=\'0\' class=\"style8\">\r\n <tr>\r\n  <td id=\"z0-00_inBody-0-6-0-0-1-0\" class=\"style9\"><span ><img src=\"/pub/traxImages/atmydesk.PNG\" alt=\"At my desk\" id=\"z0-00_inBody-0-6-0-0-1-0-i0\" class=\"clickable\">\r\n<img src=\"/pub/traxImages/canbephoned.PNG\" alt=\"Can be phoned\" id=\"z0-00_inBody-0-6-0-0-1-0-i1\" class=\"clickable\">\r\n<img src=\"/pub/traxImages/canbepaged.PNG\" alt=\"Can be paged\" id=\"z0-00_inBody-0-6-0-0-1-0-i2\" class=\"clickable\">\r\n</span></td>\r\n </tr>\r\n <tr>\r\n  <td id=\"z0-00_inBody-0-6-0-0-2-0\" class=\"style10\"><span ><img src=\"/pub/traxImages/Enroute.png\" alt=\"En route\" id=\"z0-00_inBody-0-6-0-0-2-0-i0\" class=\"clickable\">\r\n<img src=\"/pub/traxImages/Inameeting.png\" alt=\"In a meeting\" id=\"z0-00_inBody-0-6-0-0-2-0-i1\" class=\"clickable\">\r\n<img src=\"/pub/traxImages/Inthecafe.png\" alt=\"In the cafe\" id=\"z0-00_inBody-0-6-0-0-2-0-i2\" class=\"clickable\">\r\n</span></td>\r\n </tr>\r\n</table></div>\r\n</div>\r\n</div>\r\n<div id=\"z0-00_inBody-0-7\" class=\"row\">\r\n<div id=\"z0-00_inBody-0-7-0\" style=\"float:left;width:99.000%;\">\r\n<div id=\"z0-00_inBody-0-7-0-0\" class=\"component\">\r\n<table cellspacing=\'0\' class=\"style8\">\r\n <tr>\r\n  <td id=\"z0-00_inBody-0-7-0-0-1-0\" class=\"style10\"><span ><img src=\"/pub/traxImages/outside.PNG\" alt=\"Outside\" id=\"z0-00_inBody-0-7-0-0-1-0-i0\" class=\"clickable\">\r\n<img src=\"/pub/traxImages/Unavailable.png\" alt=\"Unavailable\" id=\"z0-00_inBody-0-7-0-0-1-0-i1\" class=\"clickable\">\r\n</span></td>\r\n </tr>\r\n</table></div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n</div>\r\n<iframe name=\"HiddenIFrame\" id=\"HiddenIFrame\" title=\"empty\" style=\"display:none;height:0;width:0;border:none;\"></iframe>\r\n<script type=\'text/javascript\'>\n\r// <!--\n\rProcessAjaxResponse(unescape(\"%7Fclearchildregionslist%7F%7F%7Fclearremainderlist%7F%7F%7Fclearrowlist%7F%7F%7Fnewpage%7F%7F%7Fnewpage%7F%7F%7Fupdeventhooks%7Fbody%7F%1B%7B%1B%7Bkeypress%1B%7CKeyEvent%1B%7C%1B%7Bthis%1B%7Cevent%1B%7C0%1B%7D%1B%7D%1B%7D%7Fsetsetfocusbynameurl%7F00002wpl3y%7F%7Fupdeventhooks%7Fz0-00_inBody-0-3-1-0-img%7F%1B%7B%1B%7Bclick%1B%7CImageClicked%1B%7C%5Bevent%2Cthis%2C%27img-inButton%27%2C%27%25link%27%2C1%2Cnull%5D%1B%7C0%1B%7C./1shva5yg00003e9hjb.mthd%1B%7C%1B%7D%1B%7C%1B%7Bkeypress%1B%7CLinkOnKeyPress%1B%7C%5Bthis%2Cevent%5D%1B%7C0%1B%7C%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-3-2-0-img%7F%1B%7B%1B%7Bclick%1B%7CImageClicked%1B%7C%5Bevent%2Cthis%2C%27img-outButton%27%2C%27%25link%27%2C1%2Cnull%5D%1B%7C0%1B%7C./1shva5yg00004bgvdj.mthd%1B%7C%1B%7D%1B%7C%1B%7Bkeypress%1B%7CLinkOnKeyPress%1B%7C%5Bthis%2Cevent%5D%1B%7C0%1B%7C%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-3-3-0-img%7F%1B%7B%1B%7Bclick%1B%7CImageClicked%1B%7C%5Bevent%2Cthis%2C%27img-noteButton%27%2C%27%25link%27%2C1%2Cnull%5D%1B%7C0%1B%7C./1shva5yg00005gioxt.mthd%1B%7C%1B%7D%1B%7C%1B%7Bkeypress%1B%7CLinkOnKeyPress%1B%7C%5Bthis%2Cevent%5D%1B%7C0%1B%7C%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-6-0-0-1-0-i0%7F%1B%7B%1B%7Bclick%1B%7C%1B%7C%1B%7C%1B%7C./1shva5yg000069xzkl.mthd%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-6-0-0-1-0-i1%7F%1B%7B%1B%7Bclick%1B%7C%1B%7C%1B%7C%1B%7C./1shva5yg000072whsw.mthd%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-6-0-0-1-0-i2%7F%1B%7B%1B%7Bclick%1B%7C%1B%7C%1B%7C%1B%7C./1shva5yg000088msyu.mthd%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-6-0-0-2-0-i0%7F%1B%7B%1B%7Bclick%1B%7C%1B%7C%1B%7C%1B%7C./1shva5yg00009gg71o.mthd%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-6-0-0-2-0-i1%7F%1B%7B%1B%7Bclick%1B%7C%1B%7C%1B%7C%1B%7C./1shva5yg0000a14v6y.mthd%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-6-0-0-2-0-i2%7F%1B%7B%1B%7Bclick%1B%7C%1B%7C%1B%7C%1B%7C./1shva5yg0000b061iq.mthd%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-7-0-0-1-0-i0%7F%1B%7B%1B%7Bclick%1B%7C%1B%7C%1B%7C%1B%7C./1shva5yg0000clbd1q.mthd%1B%7C%1B%7D%1B%7D%7Fupdeventhooks%7Fz0-00_inBody-0-7-0-0-1-0-i1%7F%1B%7B%1B%7Bclick%1B%7C%1B%7C%1B%7C%1B%7C./1shva5yg0000d731hb.mthd%1B%7C%1B%7D%1B%7D%7Fconstrainimages%7F%7F%7Fsetvalidationglobals%7F%7F%1B%7E%7Fsetvalidationexceptions%7F%7F%1B%7E%7Fsetvalidatordefs%7F%7F%1B%7E%7Faddtoremainderlist%7Fregioncontainer-0%7FV%7C0%7Faddtoremainderlist%7Farrangement-0-0%7FV%7C0%7Fsettimeout%7F1800%7F%7Fsetinitialurl%7F/core-coreWeb.trax.mthr%7F\"));\n\r// -->\n\r</script>\n\r</body>\r\n</html>'
        info = parseInfo(t,debug=False)
        pprint.pprint(info)
        pass
    def test_unautherized(self):
        t = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\r\n<html>\r\n<head>\r\n\r\n<title>Meditech #Web Signon</title>\r\n<style type="text/css">\r\n   BODY         { background-color: #aaf;\r\n                              font: 9pt arial;}\r\n   .container   { background-color: #eee;\r\n                            border: 2px solid #000;\r\n                             width: 200px;\r\n                            height: 300px;\r\n                       margin-left: 30px;\r\n                      margin-right: 30px;\r\n                        margin-top: 20px;\r\n                     margin-bottom: auto;\r\n                           display:block;\r\n                          position: relative;}\r\n   .headline    {       text-align: center;\r\n                              font: 16pt arial;\r\n                             color: #000;\r\n                        margin-top: 15px; }\r\n   .box         {           margin: 10px;\r\n                           padding: 10px;\r\n                  background-color: #dde;\r\n                            border: 1px solid #bbc; }\r\n   .message     {          padding: 10px;\r\n                       margin-left: 15px;\r\n                      margin-right: 15px;\r\n                             color: #f00; }\r\n   .centeredDiv { margin-right: auto; margin-left: auto; width: 260px;}\r\n</style>\r\n<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>\r\n<META HTTP-EQUIV="Pragma" CONTENT="no-cache">\r\n<script type="text/javascript">\r\n\r\n  var _gaq = _gaq || [];\r\n  _gaq.push([\'_setAccount\', \'UA-22228657-1\']);\r\n  _gaq.push([\'_setDomainName\', \'meditech.com\']);\r\n  _gaq.push([\'_trackPageview\']);\r\n\r\n  (function() {\r\n    var ga = document.createElement(\'script\'); ga.type = \'text/javascript\'; ga.async = true;\r\n    ga.src = (\'https:\' == document.location.protocol ? \'https://ssl\' : \'http://www\') + \'.google-analytics.com/ga.js\';\r\n    var s = document.getElementsByTagName(\'script\')[0]; s.parentNode.insertBefore(ga, s);\r\n  })();\r\n\r\n</script>\r\n\r\n\r\n\r\n\r\n</head>\r\n\r\n<body onload="document.getElementById(\'userid\').focus()">\r\n<div class="centeredDiv">\r\n<div class="container">\r\n  <div class="headline">Trax Mobile</div>\r\n  <div class="box">\r\n    <form action="./signon.mthz" method="post" autocomplete="on" name="signinForm">\r\n      <input type="hidden" name="sourl" value="&#47;core-coreWeb.trax.mthr">\r\n      <input type="hidden" name="application" value="">\r\n      <div  style="text-align:center;">\r\n        <label>User Name:</label>\r\n        <div><input id="userid" autocapitalize="off" type="text" name="userid" size=15><br></div>\r\n        <br>\r\n        <label>Password:</label>\r\n        <div><input type="password" id="password" name="password" size=15><br></div>\r\n        \r\n        <br>\r\n        <div><input value="Sign In" type="submit"></div>\r\n      </div>\r\n    </form>\r\n<div class="message" id="message">Invalid username/password, try again.</div>\r\n\r\n  </div>\r\n\r\n\r\n</div>\r\n</div>\r\n<script type="text/javascript">\r\n$(document).ready(function (){document.getElementById(\'userid\').focus();\r\n                              setTimeout(function(){autoSub()},1000);});\r\n\r\nfunction autoSub()\r\n{\r\n\tvar t= $("#message").html();\r\n\tvar d = document.getElementById("userid");\r\n    \tvar p = document.getElementById("password");\r\n\tif (t!=="Invalid username/password, try again." && t!=="Missing field(s), try again." && d.value!== "" && p.value !== "") \r\n\t  {setTimeout("document.signinForm.submit();",100);}\r\n}\r\n</script>\r\n\r\n</body>\r\n</html>'
        info = parseInfo(t,debug=True)
        pprint.pprint(info)
        pass
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    full_suite = unittest.TestSuite()
    full_suite.addTests([Test('test_landing'),
                         Test('test_unautherized')])
    #unittest.TextTestRunner().run(full_suite)
    #
    
    sub_suite = unittest.TestSuite()
    sub_suite.addTest(Test('test_unautherized'))
    unittest.TextTestRunner().run(sub_suite)
    import trax
    try:
        raise trax.UnautherizedError('poop','adoop')
    except trax.UnautherizedError, e:
        
        print e.message