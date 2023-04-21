from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from model.login import Login
from model.user import User
from model.note import Note
from model.note_list import NoteList

APP = Flask(__name__)
API = Api(APP)
CORS(APP)

@APP.route("/")
def index():
    return {
        'success' : True,
        'message' : 'You are currently accessing the API for RS2 Notes App v0.1'
    }

API.add_resource(Login, '/api/login')
API.add_resource(User, '/api/user')
API.add_resource(Note, '/api/note')
API.add_resource(NoteList, '/api/notes')

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000, debug=True)