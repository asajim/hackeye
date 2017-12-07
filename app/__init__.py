from flask import Flask
from flask_socketio import SocketIO, emit                                       
import time                            
# import flask_resize

app = Flask(__name__)
socketio = SocketIO(app)                                                        
thread = None 
# app.secret_key = 'monkey'
# images = Images(app)

# app.config['RESIZE_URL'] = 'https://mysite.com/'
# app.config['RESIZE_ROOT'] = '/home/user/myapp/images'

# resize = flask_resize.Resize(app)

# Setup the app with the config.py file
app.config.from_object('app.config')

# Setup the logger
from app.logger_setup import logger

# Setup the database
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Setup the mail server
from flask.ext.mail import Mail
mail = Mail(app)

# Setup the debug toolbar
from flask_debugtoolbar import DebugToolbarExtension
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
app.config['DEBUG_TB_PROFILER_ENABLED'] = True
toolbar = DebugToolbarExtension(app)

# Setup the password crypting
from flask.ext.bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# Import the views
from app.views import main, user, error
app.register_blueprint(user.userbp)

# Setup the user login process
from flask.ext.login import LoginManager
from app.models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'userbp.signin'


@login_manager.user_loader
def load_user(email):
    return User.query.filter(User.email == email).first()

from app import admin

from flask_socketio import SocketIO, emit                                       
import time                            

def background_thread():
	i = 0
	while True:                                                                 
		if i==0:
			socketio.emit('message', {'data':'I\'m connected!'});
			socketio.emit('count', {'data':1});
			i = 1;
		else:
			socketio.emit('message', {'data':'jembuuuuuts!'});
			socketio.emit('count', {'data':0});
			i = 0;
		time.sleep(5) 
        
        # socketio.emit('message', {'goodbye': "Goodbye"})   

@socketio.on('connect')                                                         
def connect():                                                                  
    global thread                                                               
    if thread is None:                                                          
        thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':                                                      
    socketio.run(app, debug=True)

# ef on_new_client(clientsocket,addr):
# 	i = 0
# 	while True:                                                                 
# 		if i==0:
# 			socketio.emit('message', {'data':'I\'m connected!'});
# 			socketio.emit('count', {'data':1});
# 			i = 1;
# 		else:
# 			socketio.emit('message', {'data':'jembuuuuuts!'});
# 			socketio.emit('count', {'data':0});
# 			i = 0;
# 		time.sleep(1) 

# s = socket.socket()         # Create a socket object
# host = socket.gethostname() # Get local machine name
# port = 5000                # Reserve a port for your service.

# print('Server started!')
# print('Waiting for clients...')

# s.bind((host, port))        # Bind to the port
# s.listen(5)                 # Now wait for client connection.

# while True:
#    c, addr = s.accept()     # Establish connection with client.
#    print('Got connection from', addr)
#    thread.start_new_thread(on_new_client,(c,addr))
#    #Note it's (addr,) not (addr) because second parameter is a tuple
#    #Edit: (c,addr)
#    #that's how you pass arguments to functions when creating new threads using thread module.
# s.close()