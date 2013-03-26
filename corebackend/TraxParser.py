'''
Created on Feb 10, 2013

@author: will
'''
from HTMLParser import HTMLParser #@UnresolvedImport@UnusedImport

info = {'z0-00_inBody-0-4-0-0s':'status',
        'z0-00_outBody-0-4-0-0s':'status',
        'z0-00_inBody-0-1-0-1s':'full_name',
        'z0-00_outBody-0-1-0-1s':'full_name'}
dateSelect = 'z0-00_dateBody-0-6-0-0s'
def parseInfo(page,debug=False):
    #returns a dictionary of all links found
    tp = TraxInfoParser(debug=debug)
    tp.feed(page)
    ret =  {"links":tp.links,
            "info":tp.info,
            "notes":tp.notes,
            "error":tp.error}
    extra = tp.getExtra()
    if extra:
        ret['extra']=extra
    return ret

class TraxInfoParser(HTMLParser):
    def __init__(self,debug=False):
        self.debug = debug
        
        HTMLParser.__init__(self)
        self.onclick = ''
        self.alt = ''
        self.gather_info = False
        self.gather_info_tag = ''
        
        self.gather_notes = False
        self.gather_error = False
        self.error = ''
        self.notes = ''
        self.links = {}
        self.info = {}
        
        self.dateSelect = False
        self.dateSelectName = ''
        self.dateSelectLink = ''
        
        self.phoneExtInput = False
        self.phoneExtName = ''
        self.phoneExtLink = ''
        
        self.note_form = False
        self.note_form_name = ''

    def getExtra(self):
        ret = {}
        if self.dateSelect or self.phoneExtInput or self.note_form: 
            if self.dateSelect:
                ret['date_select_name']={'name':self.dateSelectName,
                                         'link':self.dateSelectLink}
            if self.phoneExtInput:
                ret['phone_ext_name']={'name':self.phoneExtName,
                                       'link':self.phoneExtLink}
            if self.note_form:
                ret['note_form_name']=self.note_form_name
            return ret
        else:
            return False
        
    def handle_starttag(self, tag, attrs):
        if self.debug:
            print('start tag %s' % tag)
        self.maybe_save_tag()
        
        if self.gather_notes:
            note = '<'+tag
            for attr in attrs:
                note += ' '+attr[0]+'="'+attr[1]+'"'
            note += '>'
            self.notes+=note
            return
        
        if tag == 'img' or tag == 'div':
            
            for attr in attrs:
                if attr[0] == 'alt':
                    #image tag, get alt
                    self.alt = attr[1]
                
                elif attr[0] == 'onclick':
                    #print("\ton click: %s" % attr[1])
                    try:
                        t = attr[1]
                        s1 = 'javascript'
                        s = t.index(s1)+len(s1)
                        s2 = 'Clicked'
                        s = t.index(s2,s)+len(s2)
                        s3 = '".'
                        s = t.index(s3,s)+len(s3)
                        e = t.index('"',s)
                        
                        #print("\ton click: %d:" % s, "%d" % e)
                        self.onclick = t[s:e]
                    except ValueError:
                        #?? no javascript here?
                        continue
                        
                elif attr[0]=='id': 
                    if attr[1] == 'message':
                        self.gather_error = True

                        
        elif tag == 'select':
            #date selection 
            for attr in attrs:
                if attr[0]=='id': 
                    if attr[1] == dateSelect:   
                        self.dateSelect = True
                elif attr[0]=='name':
                    #form name to be used when posting
                    self.dateSelectName = attr[1]
                elif attr[0]=='onchange':
                    self.dateSelectLink = self.parse_link(attr[1])
        elif tag == 'input':
            #phone ext input
            for attr in attrs:
                if attr[0]=='value': 
                    if attr[1] == 'Phone Number':   
                        self.phoneExtInput = True
                elif attr[0]=='name':
                    #form name to be used when posting
                    self.phoneExtName = attr[1]
                elif attr[0]=='onclick':
                    self.phoneExtLink = self.parse_link(attr[1])
                    
        elif tag == 'span':
            
            for attr in attrs:
                print('get info %s' % str(attr))
                if attr[0] == 'id' and (attr[1] in info):
                    
                    self.gather_info_tag  = info[attr[1]]
                    self.gather_info = True
                
        #print("Encountered the beginning of a %s tag" % tag)
        #print("\tattrs %s" % attrs)
    
    def parse_link(self,tag):
        try:
            t = tag
            s1 = 'javascript'
            s = t.index(s1)+len(s1)
            s2 = 'Clicked'
            s = t.index(s2,s)+len(s2)
            s3 = '".'
            s = t.index(s3,s)+len(s3)
            e = t.index('"',s)
            
            #print("\ton click: %d:" % s, "%d" % e)
            
            return t[s:e]
        except ValueError:
            #?? no javascript here?
            return None
    def handle_endtag(self, tag):
        if self.debug:
            print('end tag: %s' % tag)
        if self.gather_notes:
            note = '</'+tag+'>'
            self.notes+=note
            return
        

        self.maybe_save_tag()
        ##give up on tag
        self.name = self.onclick = ''
        self.gather_info = False
        if self.gather_error:
            self.gather_error = False
            
    def maybe_save_tag(self):
        if len(self.onclick)>0 and len(self.alt)>0:
            self.links[self.alt] = self.onclick
            self.alt = self.onclick = ''


    def handle_data(self, data):
        if self.debug:
            print 'handling data: %s' %data
        end_note_body = not data.find('resetkeymap') == -1
        if end_note_body:
            self.gather_notes = False
        if self.gather_info:
            if self.gather_info_tag in self.info:
                self.info[self.gather_info_tag] += data
            else:
                self.info[self.gather_info_tag] = data
            
        if self.gather_notes:
            self.notes += data
        if self.gather_error:
            self.error += data
            
        start_note_body = not data.find('newrichtext') == -1
        if start_note_body:
            s = data.split('|')
            self.note_form_name = s[1]
            self.note_form = True
            self.gather_notes = True
    def handle_entityref(self,data):
        if self.gather_info:
            if self.gather_info_tag in self.info:
                self.info[self.gather_info_tag] += '&'+data+';'
            else:
                self.info[self.gather_info_tag] = '&'+data+';'
            
        if self.gather_notes:
            self.notes += '&'+data+';'
    def handle_charref(self,data):
        if self.gather_info:
            if self.gather_info_tag in self.info:
                self.info[self.gather_info_tag] += chr(int(data))
            else:
                self.info[self.gather_info_tag] = chr(int(data))
            
        if self.gather_notes:
            self.notes += chr(int(data))
    def __str__(self):
        return str(self.ret)
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    '''
    
    t = '<html>\r\n<head>\r\n<title>Mobile Trax</title>\r\n<script type="text/javascript" src="./system/scripts/main.js"></script>\r\n<script type="text/javascript">\r\n<!--\r\n  window.onbeforeunload = confirmExit;\r\n//-->\r\n</script>\r\n<style type="text/css">\r\n.block {float:left;}\r\n.component {position:relative;\r\n            font-family:Verdana,Helvetica,Ariel,sans-serif;}\r\n.clickable {cursor:pointer;}\r\n.cell-component {font-family:Verdana,Helvetica,Ariel,sans-serif}\r\n.popupcalendarlink {cursor:default;\r\n                    border-color:#000;\r\n                    text-align:center; font-weight: 700;\r\n                    color: blue;}\r\n.popupcalendarheader { background: #ddf; }\r\n.popupcalendarhover { background: #ddf; }\r\nbody { margin:0; padding:0; }\r\n@media screen {\r\n .regioncontainer {\r\n    width:100%; height:100%;\r\n    top:0; left:0;\r\n    position:absolute;\r\n    padding:0; margin:0;\r\n    overflow:hidden;\r\n }\r\n}\r\n@media print {\r\n .regioncontainer {\r\n    top:0; left:0;\r\n    padding:0; margin:0;\r\n    overflow:hidden;\r\n }\r\n}\r\n.sysnormaltext {color:black; font-style:normal;}\r\n.sysoverridegraytext {color:gray; font-style:italic;}\r\n.sysoverridegraytextselect {color:gray;}\r\ndiv.link {cursor:pointer;}\r\ndiv.popupshield {width:100%; height:100%;\r\n                 background:#000;\r\n                 position:absolute; margin:0; border:none; padding:0; top:0; left:0;\r\n                 opacity:0.2; filter:alpha(opacity=20);}\r\ndiv.popupshield2 {width:100%; height:100%;\r\n                  background:#000;\r\n                  position:absolute; margin:0; border:none; padding:0; top:0; left:0;\r\n                  opacity:0.0; filter:alpha(opacity=0);}\r\ndiv.popupouter {position:absolute; height:auto;\r\n                border:1px solid black;\r\n                background:white;}\r\ndiv.popupheader {background:#4040e0; color:white;\r\n                 margin:0; padding:2px;}\r\ndiv.popupbody {margin:0; padding:5px;}\r\nimg.link {cursor:pointer;}\r\n.style0 {height:100%; left:0; margin:0; padding:0; position:absolute; top:0%; width:100%;}\r\n.style1 {border-top:1px solid #000000; border-right:1px solid #000000; border-bottom:1px solid #000000; height:100%; left:0; margin:0; overflow:auto; padding:0; position:absolute; top:0; width:100%;}\r\n.style2 {float:left; width:100%;}\r\n.style3 {text-align:center;}\r\n.style4 {width:auto;}\r\n.style5 {margin:auto; display:block;}\r\n.style6 {font-size:x-small; font-family:verdana;}\r\n.style7 {margin:auto;}\r\n.style8 {border-left:none; border-right:none; border-top:none;}\r\n.style9 {border-bottom:none; border-left:none; border-right:none; border-top:none;}\r\n</style>\r\n</head>\r\n<body onload=\'BodyOnLoad();\' onkeypress=\'KeyEvent(this,event);\'>\r\n<div><a tabindex="0" href=""></a></div>\r\n<div><a tabindex="0" href=""></a></div>\r\n<div id="regioncontainer-0" class="regioncontainer">\r\n<div id="body-0-wrapper" class="style0">\r\n<div id="body-0" class="style1">\r\n<div class="style2"><div>\r\n\r\n<div id="z0-b-0-1-0" class="block" style="width:96.0000%;clear:both;">\r\n<div id="z0-b-0-1-0-0" class="component">\r\n<style type="text/css">@media screen and (min-width: 320px) {img.clickable {width:90px;height:81px;}img.style5 {width:90px;height:45px;}}@media screen and (min-width: 360px) {img.clickable {width:110px;height:99px;}img.style5 {width:108px;height:54px;}}@media screen and (min-width: 640px) {img.clickable {width:130px;height:117px;}img.style5 {width:130px;height:65px;}}@media screen and (min-width: 800px) {img.clickable {width:150px;height:135px;}img.style5 {width:150px;height:75px;}}@media screen and (min-width: 960px) {img.clickable {width:170px;height:153px;}img.style5 {width:170px;height:85px;}}@media screen and (min-width: 1120px) {img.clickable {width:190px;height:171px;}img.style5 {width:190px;height:95px;}}</style></div>\r\n <div class="component style3">\r\n  <span id="z0-b-0-1-0-1s">William Cohen </span>\r\n</div>\r\n</div>\r\n\r\n</div>\r\n<div>\r\n\r\n<div id="z0-b-0-2-0" class="block" style="width:96.0000%;clear:both;">\r\n<div id="z0-b-0-2-0-0" class="component">\r\n<div style="height:0.5em;" class="component"></div></div>\r\n</div>\r\n\r\n</div>\r\n<div>\r\n\r\n<div id="z0-b-0-3-0" class="block" style="width:4.8000%;clear:both;">\r\n <div style="height: 1.5em;" class="component"></div>\r\n</div>\r\n\r\n<div id="z0-b-0-3-1" class="block" style="width:28.8000%;">\r\n <div id="z0-b-0-3-1-0" class="component link clickable">\r\n  <div id="z0-b-0-3-1-0-img" tabindex="0"\r\n class="style4"\r\n onclick=\'javascript:LinkClicked("./4rg00005zm6nq.mthd",1);\'\r\n onkeypress=\'LinkOnKeyPress(this,event);\'\r\n><img src="/pub/traxImages/inblue.png"\r\n             class="style5"\r\n             name="inButton"\r\n             id="z0-b-0-3-1-0-imgI"\r\n             alt="In"\r\n             width="60px"\r\n             height="30px"\r\n             title="In">\r\n</div>\r\n </div>\r\n</div>\r\n\r\n<div id="z0-b-0-3-2" class="block" style="width:28.8000%;">\r\n <div id="z0-b-0-3-2-0" class="component link clickable">\r\n  <div id="z0-b-0-3-2-0-img" tabindex="0"\r\n class="style4"\r\n onclick=\'javascript:LinkClicked("./4rg00006n9id1.mthd",1);\'\r\n onkeypress=\'LinkOnKeyPress(this,event);\'\r\n><img src="/pub/traxImages/outblack.png"\r\n             class="style5"\r\n             name="outButton"\r\n             id="z0-b-0-3-2-0-imgI"\r\n             alt="Out"\r\n             width="60px"\r\n             height="30px"\r\n             title="Out">\r\n</div>\r\n </div>\r\n</div>\r\n\r\n<div id="z0-b-0-3-3" class="block" style="width:28.8000%;">\r\n <div id="z0-b-0-3-3-0" class="component link clickable">\r\n  <div id="z0-b-0-3-3-0-img" tabindex="0"\r\n class="style4"\r\n onclick=\'javascript:LinkClicked("./4rg000072jseh.mthd",1);\'\r\n onkeypress=\'LinkOnKeyPress(this,event);\'\r\n><img src="/pub/traxImages/notesblack.png"\r\n             class="style5"\r\n             name="noteButton"\r\n             id="z0-b-0-3-3-0-imgI"\r\n             alt="Note"\r\n             width="60px"\r\n             height="30px"\r\n             title="Note">\r\n</div>\r\n </div>\r\n</div>\r\n\r\n<div id="z0-b-0-3-4" class="block" style="width:4.8000%;">\r\n <div style="height: 1.5em;" class="component"></div>\r\n</div>\r\n\r\n</div>\r\n<div>\r\n\r\n<div id="z0-b-0-4-0" class="block" style="width:96.0000%;clear:both;">\r\n <div class="component style3">\r\n  <span id="z0-b-0-4-0-0s" class="style6">Out for the day, returning Mon 02/11/13 </span>\r\n</div>\r\n</div>\r\n\r\n</div>\r\n<div>\r\n\r\n<div id="z0-b-0-5-0" class="block" style="width:96.0000%;clear:both;">\r\n<div id="z0-b-0-5-0-0" class="component">\r\n<div style="height:0.5em;" class="component"></div></div>\r\n</div>\r\n\r\n</div>\r\n<div>\r\n\r\n<div id="z0-b-0-6-0" class="block" style="width:96.0000%;clear:both;">\r\n<div id="z0-b-0-6-0-0" class="component">\r\n<table cellspacing=\'0\' class="style7">\r\n <tr>\r\n  <td id="z0-b-0-6-0-0-1-0" class="style8"><span><img src="/pub/traxImages/atmydesk.PNG" alt="At my desk" width="60" height="60" onclick=\'javascript:LinkClicked("./4rg00008zt73j.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/canbephoned.PNG" alt="Can be phoned" width="60" height="60" onclick=\'javascript:LinkClicked("./4rg00009c024j.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/canbepaged.PNG" alt="Can be paged" width="60" height="60" onclick=\'javascript:LinkClicked("./4rg0000ac7i77.mthd",1);\' class="clickable">\r\n</span></td>\r\n </tr>\r\n <tr>\r\n  <td id="z0-b-0-6-0-0-2-0" class="style9"><span><img src="/pub/traxImages/Enroute.png" alt="En route" width="60" height="60" onclick=\'javascript:LinkClicked("./4rg0000b2h7m2.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/Inameeting.png" alt="In a meeting" width="60" height="60" onclick=\'javascript:LinkClicked("./4rg0000cqpuum.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/Inthecafe.png" alt="In the cafe" width="60" height="60" onclick=\'javascript:LinkClicked("./4rg0000d97uhw.mthd",1);\' class="clickable">\r\n</span></td>\r\n </tr>\r\n</table></div>\r\n</div>\r\n\r\n</div>\r\n<div>\r\n\r\n<div id="z0-b-0-7-0" class="block" style="width:96.0000%;clear:both;">\r\n<div id="z0-b-0-7-0-0" class="component">\r\n<table cellspacing=\'0\' class="style7">\r\n <tr>\r\n  <td id="z0-b-0-7-0-0-1-0" class="style9"><span><img src="/pub/traxImages/outside.PNG" alt="Outside" width="60" height="60" onclick=\'javascript:LinkClicked("./4rg0000eiola4.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/Unavailable.png" alt="Unavailable" width="60" height="60" onclick=\'javascript:LinkClicked("./4rg0000fwr30r.mthd",1);\' class="clickable">\r\n</span></td>\r\n </tr>\r\n</table></div>\r\n</div>\r\n\r\n</div>\r\n</div></div>\r\n</div>\r\n</div>\r\n<iframe name="HiddenIFrame" id="HiddenIFrame" style="display:none;height:0;width:0;border:none;"></iframe>\r\n<script type=\'text/javascript\'>\n\r// <!--\n\rProcessAjaxResponse(unescape("%7fnewpage%7f%7f%7fnewpage%7f%7f%7fsetfocus%7fz0-b-0-3-1-0-img%7f%7fsendkeymap%7fshift+tab%7f./4rg00002ufs0f.mthd%7fsendkeymap%7ftab%7f./4rg00003dnu1q.mthd%7fsetsetfocusbynameurl%7f00004730c2%7f%7fsettimeout%7f600%7f%7fsetinitialurl%7f/core-coreWeb.trax.mthr%7f"));\n\r// -->\n\r</script>\n\r</body>\r\n</html>'
    info = parseInfo(t)
    print(info)
    t = '<div class="style2"><div>\\r\\n\\r\\n<div id="z0-b-0-1-0" class="block" style="width:96.0000%;clear:both;">\\r\\n<div id="z0-b-0-1-0-0" class="component">\\r\\n<style type="text/css"> table {width:100%;}</style></div>\\r\\n<div id="z0-b-0-1-0-1" class="component">\\r\\n<style type="text/css">@media screen and (min-width: 320px) {img.clickable {width:90px;height:81px;}img.style5 {width:90px;height:45px;}}@media screen and (min-width: 360px) {img.clickable {width:110px;height:99px;}img.style5 {width:108px;height:54px;}}@media screen and (min-width: 640px) {img.clickable {width:130px;height:117px;}img.style5 {width:130px;height:65px;}}@media screen and (min-width: 800px) {img.clickable {width:150px;height:135px;}img.style5 {width:150px;height:75px;}}@media screen and (min-width: 960px) {img.clickable {width:170px;height:153px;}img.style5 {width:170px;height:85px;}}@media screen and (min-width: 1120px) {img.clickable {width:190px;height:171px;}img.style5 {width:190px;height:95px;}}</style></div>\\r\\n <div class="component style3">\\r\\n  <span id="z0-b-0-1-0-2s">William Cohen </span>\\r\\n</div>\\r\\n</div>\\r\\n\\r\\n</div>\\r\\n<div>\\r\\n\\r\\n<div id="z0-b-0-2-0" class="block" style="width:96.0000%;clear:both;">\\r\\n<div id="z0-b-0-2-0-0" class="component">\\r\\n<div style="height:0.5em;" class="component"></div></div>\\r\\n</div>\\r\\n\\r\\n</div>\\r\\n<div>\\r\\n\\r\\n<div id="z0-b-0-3-0" class="block" style="width:4.8000%;clear:both;">\\r\\n <div style="height: 1.5em;" class="component"></div>\\r\\n</div>\\r\\n\\r\\n<div id="z0-b-0-3-1" class="block" style="width:28.8000%;">\\r\\n <div id="z0-b-0-3-1-0" class="component link clickable">\\r\\n  <div id="z0-b-0-3-1-0-img" tabindex="0"\\r\\n class="style4"\\r\\n onclick=\\\'javascript:LinkClicked("./50y0000iuume8.mthd",1);\\\'\\r\\n onkeypress=\\\'LinkOnKeyPress(this,event);\\\'\\r\\n><img src="/pub/traxImages/inblack.png"\\r\\n             class="style5"\\r\\n             name="inButton"\\r\\n             id="z0-b-0-3-1-0-imgI"\\r\\n             alt="In"\\r\\n             width="60px"\\r\\n             height="30px"\\r\\n             title="In">\\r\\n</div>\\r\\n </div>\\r\\n</div>\\r\\n\\r\\n<div id="z0-b-0-3-2" class="block" style="width:28.8000%;">\\r\\n <div id="z0-b-0-3-2-0" class="component link clickable">\\r\\n  <div id="z0-b-0-3-2-0-img" tabindex="0"\\r\\n class="style4"\\r\\n onclick=\\\'javascript:LinkClicked("./50y0000ju10r8.mthd",1);\\\'\\r\\n onkeypress=\\\'LinkOnKeyPress(this,event);\\\'\\r\\n><img src="/pub/traxImages/outblack.png"\\r\\n             class="style5"\\r\\n             name="outButton"\\r\\n             id="z0-b-0-3-2-0-imgI"\\r\\n             alt="Out"\\r\\n             width="60px"\\r\\n             height="30px"\\r\\n             title="Out">\\r\\n</div>\\r\\n </div>\\r\\n</div>\\r\\n\\r\\n<div id="z0-b-0-3-3" class="block" style="width:28.8000%;">\\r\\n <div id="z0-b-0-3-3-0" class="component link clickable">\\r\\n  <div id="z0-b-0-3-3-0-img" tabindex="0"\\r\\n class="style4"\\r\\n onclick=\\\'javascript:LinkClicked("./50y0000kxloln.mthd",1);\\\'\\r\\n onkeypress=\\\'LinkOnKeyPress(this,event);\\\'\\r\\n><img src="/pub/traxImages/notesblue.png"\\r\\n             class="style5"\\r\\n             name="noteButton"\\r\\n             id="z0-b-0-3-3-0-imgI"\\r\\n             alt="Note"\\r\\n             width="60px"\\r\\n             height="30px"\\r\\n             title="Note">\\r\\n</div>\\r\\n </div>\\r\\n</div>\\r\\n\\r\\n<div id="z0-b-0-3-4" class="block" style="width:4.8000%;">\\r\\n <div style="height: 1.5em;" class="component"></div>\\r\\n</div>\\r\\n\\r\\n</div>\\r\\n<div>\\r\\n\\r\\n<div id="z0-b-0-4-0" class="block" style="width:96.0000%;clear:both;">\\r\\n</div>\\r\\n\\r\\n</div>\\r\\n<div>\\r\\n\\r\\n<div id="z0-b-0-5-0" class="block" style="width:96.0000%;clear:both;">\\r\\n<div id="z0-b-0-5-0-0" class="component">\\r\\n<div style="height:0.5em;" class="component"></div></div>\\r\\n</div>\\r\\n\\r\\n</div>\\r\\n<div>\\r\\n\\r\\n<div id="z0-b-0-6-0" class="block" style="width:1.9200%;clear:both;">\\r\\n <div style="height: 1.5em;" class="component"></div>\\r\\n</div>\\r\\n\\r\\n<div id="z0-b-0-6-1" class="block" style="width:94.0800%;">\\r\\n<div id="z0-b-0-6-1-0" class="component style3">\\r\\n</div>\\r\\n</div>\\r\\n\\r\\n</div>\\r\\n<div>\\r\\n\\r\\n<div id="z0-b-0-7-0" class="block" style="width:96.0000%;clear:both;">\\r\\n<div id="z0-b-0-7-0-0" class="component">\\r\\n<div style="height:0.5em;" class="component"></div></div>\\r\\n</div>\\r\\n\\r\\n</div>\\r\\n<div>\\r\\n\\r\\n<div id="z0-b-0-8-0" class="block" style="width:31.6800%;clear:both;">\\r\\n <div style="height: 1.5em;" class="component"></div>\\r\\n</div>\\r\\n\\r\\n<div id="z0-b-0-8-1" class="block" style="width:31.6800%;">\\r\\n <div id="z0-b-0-8-1-0" class="component link clickable">\\r\\n  <div id="z0-b-0-8-1-0-img" tabindex="0"\\r\\n class="style4"\\r\\n onclick=\\\'javascript:LinkClicked("./50y0000ljhsz3.mthd",1);\\\'\\r\\n onkeypress=\\\'LinkOnKeyPress(this,event);\\\'\\r\\n><img src="/pub/traxImages/saveblack.png"\\r\\n             class="style5"\\r\\n             name="saveButton"\\r\\n             id="z0-b-0-8-1-0-imgI"\\r\\n             alt="Save"\\r\\n             width="60px"\\r\\n             height="30px"\\r\\n             title="Save">\\r\\n</div>\\r\\n </div>\\r\\n</div>\\r\\n\\r\\n<div id="z0-b-0-8-2" class="block" style="width:31.6800%;">\\r\\n <div style="height: 1.5em;" class="component"></div>\\r\\n</div>\\r\\n\\r\\n</div>\\r\\n</div>\\x7fupdclass\\x7fbody-0\\x7fstyle1\\x7fupdstyle\\x7fbody-0\\x7f\\x7fnewpage\\x7f\\x7f\\x7fnewrichtext\\x7fz0-b-0-6-1-0|in1|\\x7f\\r<font size="2"><span style="font-family:Verdana; color:rgb(0,0,0);"><br>cell - 617 538 9088<br><br>When unavailable urgent issues to:<br>Amy Bacon&nbsp; X3247<br>Travis BeebeX5090<br>Neil Vigliotta X5043<br>Dave NadeauX3248<br><br></span></font>\\x7fresetkeymap\\x7f\\x7f\\x7fsendkeymap\\x7fshift+tab\\x7f./50y0000gvk09d.mthd\\x7fsendkeymap\\x7ftab\\x7f./50y0000hbkxmg.mthd\\x7fsetfocus\\x7fz0-b-0-3-1-0-img\\x7f\''
    info = parseInfo(t)
    print(info)
    t = 'b\'\x7fupd\x7fz0-b-0-3-1\x7f\r\n <div id="z0-b-0-3-1-0" class="component link clickable">\r\n  <div id="z0-b-0-3-1-0-img" tabindex="0"\r\n class="style4"\r\n onclick=\'javascript:LinkClicked("./ce50000islnun.mthd",1);\'\r\n onkeypress=\'LinkOnKeyPress(this,event);\'\r\n><img src="/pub/traxImages/inblack.png"\r\n             class="style5"\r\n             name="inButton"\r\n             id="z0-b-0-3-1-0-imgI"\r\n             alt="In"\r\n             width="60px"\r\n             height="30px"\r\n             title="In">\r\n</div>\r\n </div>\r\n\x7fupdclass\x7fz0-b-0-3-1\x7fblock\x7fupdstyle\x7fz0-b-0-3-1\x7fwidth:28.8000%;\x7fupd\x7fz0-b-0-3-2\x7f\r\n <div id="z0-b-0-3-2-0" class="component link clickable">\r\n  <div id="z0-b-0-3-2-0-img" tabindex="0"\r\n class="style4"\r\n onclick=\'javascript:LinkClicked("./ce50000jwf5ml.mthd",1);\'\r\n onkeypress=\'LinkOnKeyPress(this,event);\'\r\n><img src="/pub/traxImages/outblue.png"\r\n             class="style5"\r\n             name="outButton"\r\n             id="z0-b-0-3-2-0-imgI"\r\n             alt="Out"\r\n             width="60px"\r\n             height="30px"\r\n             title="Out">\r\n</div>\r\n </div>\r\n\x7fupdclass\x7fz0-b-0-3-2\x7fblock\x7fupdstyle\x7fz0-b-0-3-2\x7fwidth:28.8000%;\x7fupd\x7fz0-b-0-6-0\x7f\r\n<div id="z0-b-0-6-0-0" class="component">\r\n<table cellspacing=\'0\' class="style7">\r\n <tr>\r\n  <td id="z0-b-0-6-0-0-1-0" class="style8"><span><img src="/pub/traxImages/Outfortheday.png" alt="Out for the day" width="60" height="60" onclick=\'javascript:LinkClicked("./ce50000kdgva9.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/Outsick.png" alt="Out sick" width="60" height="60" onclick=\'javascript:LinkClicked("./ce50000liidew.mthd",1);\' class="clickable">\r\n</span></td>\r\n </tr>\r\n <tr>\r\n  <td id="z0-b-0-6-0-0-2-0" class="style9"><span><img src="/pub/traxImages/Outonvacation.png" alt="Out on vacation" width="60" height="60" onclick=\'javascript:LinkClicked("./ce50000matbvj.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/Outonleave.png" alt="Out on leave" width="60" height="60" onclick=\'javascript:LinkClicked("./ce50000n5gwff.mthd",1);\' class="clickable">\r\n</span></td>\r\n </tr>\r\n</table></div>\r\n\x7fupdclass\x7fz0-b-0-6-0\x7fblock\x7fupdstyle\x7fz0-b-0-6-0\x7fwidth:96.0000%;clear:both;\x7fupd\x7fz0-b-0-7-0\x7f\r\n<div id="z0-b-0-7-0-0" class="component">\r\n<table cellspacing=\'0\' class="style7">\r\n <tr>\r\n  <td id="z0-b-0-7-0-0-1-0" class="style9"><span><img src="/pub/traxImages/Backin12hour.png" alt="Back in 1/2 hour" width="60" height="60" onclick=\'javascript:LinkClicked("./ce50000oamehm.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/Backin1hour.png" alt="Back in 1 hour" width="60" height="60" onclick=\'javascript:LinkClicked("./ce50000ph14bt.mthd",1);\' class="clickable">\r\n<img src="/pub/traxImages/Backinawhile.png" alt="Back in a while" width="60" height="60" onclick=\'javascript:LinkClicked("./ce50000q2y9yz.mthd",1);\' class="clickable">\r\n</span></td>\r\n </tr>\r\n</table></div>\r\n\x7fupdclass\x7fz0-b-0-7-0\x7fblock\x7fupdstyle\x7fz0-b-0-7-0\x7fwidth:96.0000%;clear:both;\x7fnewpage\x7f\x7f\x7fresetkeymap\x7f\x7f\x7fsendkeymap\x7fshift+tab\x7f./ce50000gxerw7.mthd\x7fsendkeymap\x7ftab\x7f./ce50000hv4f7g.mthd\x7fsetfocus\x7fz0-b-0-3-1-0-img\x7f'
    info = parseInfo(t)
    print(info)
    t = '<div id="z0-00_noteBody-0-8-2" style="float:left;width:33%;"> <div style="height: 1.5em;" class="component"></div></div></div></div></div></div>updclassregioncontainer-0regioncontainer style0newpagenewrichtextz0-00_noteBody-0-6-1-0|in1|cbrte|p<font size="2"><span style="font-family:Verdana; color:rgb(0,0,0);">Retrofitting all day<br><br>Urgent issues to Amy Bacon x3247<br><br><br>cell - 617 538 9088<br><br>When unavailable urgent issues to:<br>Amy Bacon X3247<br>Travis BeebeX5090<br>Neil Vigliotta X5043<br>Dave NadeauX3248<br></span></font>resetkeymapsendkeymapshift+tab./j1gjxhyv0000gawj9w.mthdsendkeymaptab./j1gjxhyv0000hgs03a.mthdaddtoremainderlistregioncontainer-0V|0addtoremainderlistarrangement-0-0V|0addtorowlistz0-00_noteBody-0-1addtorowlistz0-00_noteBody-0-2addtorowlistz0-00_noteBody-0-3addtorowlistz0-00_noteBody-0-4addtorowlistz0-00_noteBody-0-5addtorowlistz0-00_noteBody-0-6addtorowlistz0-00_noteBody-0-7addtorowlistz0-00_noteBody-0-8setfocusz0-00_noteBody-0-3-1-0-img'
    info = parseInfo(t)
    '''
    
    t='<div id="z0-00_outBody-0-4-0" style="float:left;width:99%;">\r\n <div class="component style4">\r\n  <span id="z0-00_outBody-0-4-0-0s" class="style7">Out on vacation, returning Tue 03&#47;26&#47;13</span>\r\n </div>\r\n</div>\r\n</div>\r\n<div class="row" id="z0-00_outBody-0-5">'
    info = parseInfo(t,debug=True)
    print(info)
