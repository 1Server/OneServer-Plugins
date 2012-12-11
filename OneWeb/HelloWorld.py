import cherrypy
import os

class OnePage(object):
	def index(self):
		return "one page!"
	index.exposed = True

class LoginPage(object):
	def index(self):
		return "Login page!"
	index.exposed = True
	
class HelloWorld(object):
	def index(self):
		return "Hello world!"
	index.exposed = True
	#onepage = OnePage()
	#login = "/LoginPage.html"
	
WEB_ROOT = os.path.abspath(os.path.dirname(__file__))
	
cherrypy.server.socket_port = 80
cherrypy.server.socket_host = '127.0.0.1'
	
conf = { '/':
	{ 'tools.staticdir.on' : True,
	  'tools.staticdir.dir' : WEB_ROOT,
	  'tools.staticdir.index' : 'index.html' } }

cherrypy.quickstart(HelloWorld(), config = conf)