Core_Backend
====
To send information to the server and retrieve results,
JSON queries must be sent with a always required `type` 
field along with any other required fields as well.
Server will respond with the with a JSON object with an 
appropriate response.

Queries can be POSTed to my live instance which is here:
https://corebackend.appspot.com

##Currently supported functions

------------------------------------------------------------------
###Trax functions
####get status:
query
```JSON
{
 "type":"get_status",
 "username": username,
 "password": password
}
```
response
```JSON
{
  "status": current_status,
  "notes": current_notes,
  "full_name": full_name
}
```
####set status:
query
```JSON
{
 "type":"set_status",
 "username": username,
 "password": password
}
```
response
```JSON
{
  "saved":True
}
```

-----------------------------------------------------------------
###Error messages
####Unautherized:
```JSON
{
    "detail": "Invalid username/password, try again.",
    "error": "UnautherizedError"
}
```
####Missing required fields:
```JSON
{
	"detail":"missing required field(s): '+field list,
    'error':'missing required'
}
````
####Timeout:
Meditech took to long to respond and I gave up
```JSON
{
	'detail':'trax.meditech.com took to long to respond',
	'error':'DeadlineExceededError'
}
```
####Parsing Error:
If you see this, Meditech probably changed their interface and I haven't put out an update
```JSON
{
	'detail':'trax.meditech.com returned an unexpected result',
	'error':'parsing error'
}
```

types = {'get_status': {'required_fields':['username','password'],
                        'session':trax,
                        'function':getStatus},

         'set_status': {'required_fields':['username','password'],
                        'session':trax,
                        'function':setStatus},
         'set_notes': {'required_fields':['username','password'],
                       'session':trax,
                       'function':notImplemented},
         'list_events': {'required_fields':['username','password'],
                         'session':trax,
                         'function':notImplemented},
         'find_person': {'required_fields':['username','password'],
                         'session':trax,
                         'function':notImplemented},
         'build_menu':{'required_fields':['username','password'],
                       'session':trax,
                       'function':notImplemented},
         'get_menu':{'required_fields':[],
                     'session':trax,
                     'function':getMenu}}