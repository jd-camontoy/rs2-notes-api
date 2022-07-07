from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from model.survey_settings import SurveySettings
from model.survey_response import SurveyResponse
from model.login import Login
from model.survey import Survey
from model.dashboard import Dashboard

APP = Flask(__name__)
API = Api(APP)
CORS(APP)

@APP.route("/")
def index():
    return {
        'success' : True,
        'message' : 'You are currently accessing the API for Motivation Meter Mini v0.1'
    }

API.add_resource(SurveySettings, '/api/survey_settings')
API.add_resource(SurveyResponse, '/api/survey_response')
API.add_resource(Survey, '/api/survey')
API.add_resource(Login, '/api/login')
API.add_resource(Dashboard, '/api/dashboard')

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000, debug=True)