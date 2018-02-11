import sys
 
#Expand Python classes path with your app's path
sys.path.insert(0, "/srv/http/uipsys/")

#sys.path.append('/srv/http')
#sys.path.append('/srv/http/uipsys')

from index import app
#app.secret_key = "super secret key" 
app.secret_key = "f25a2fc72690b780b2a14e140ef6a9e0"

#Put logging code (and imports) here ...
 
#Initialize WSGI app object
application = app
