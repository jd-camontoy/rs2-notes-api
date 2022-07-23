import json
import os
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from pymongo import MongoClient
from model.survey_settings import SurveySettings
import uuid
import re
import hashlib

class Survey(Resource):
    # Enhance hashing
    def hashPassword(self, password):
        hashString = hashlib.sha1(password.encode('utf-8'))
        hashedString = hashString.hexdigest()
        no_of_iterations = os.getenv('HASH_ITERATION')
        for i in range(int(no_of_iterations)):
            hashedString = hashedString + str(i)
            hashString = hashlib.sha1(hashedString.encode('utf-8'))
            hashedString = hashString.hexdigest()
        return hashedString

    def get(self):
        db = None
        try:
            token = request.args.get('token') if 'token' in request.args else None

            if (token == None):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            db = Database.connect()
            data = db.survey.find_one({ 'token': token })

            if (data == None):
                return {
                    'success' : False,
                    'message' : 'Survey does not exist'
                }, 404
            else:
                response_count = db.survey_response.count_documents({ 'survey_token': token })
                survey_response_limit = data['no_of_respondents']
                current_datetime = datetime.now()
                survey_expiry_datetime = data['expires_at']
                
                if (response_count >= survey_response_limit):
                    return {
                        'success' : False,
                        'message' : 'Survey responses already reached its limit',
                        'survey_data': {
                            '_id': str(data['_id']),
                            'created_at': str(data['created_at']),
                            'expires_at': str(data['expires_at'])
                        }
                    }, 401
                elif (current_datetime >= survey_expiry_datetime):
                    return {
                        'success' : False,
                        'message' : 'Survey already expired',
                        'survey_data': {
                            '_id': str(data['_id']),
                            'created_at': str(data['created_at']),
                            'expires_at': str(data['expires_at'])
                        }
                    }, 401
                else:
                    return {
                        'success': True,
                        'data': {
                            '_id': str(data['_id']),
                            'created_at': str(data['created_at']),
                            'expires_at': str(data['expires_at'])
                        }
                    }

        except Exception as exception:
            return {'error': str(exception)}, 500
        finally:
            if type(db) == MongoClient:
                db.close()

    def post(self):
        db = None
        survey_respondent_options = SurveySettings.getNoOfRespondents(SurveySettings)
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('params', type=str, help='')
            args = parser.parse_args()
            params = json.loads(args['params'])

            survey_no_of_respondents = params['survey_no_of_respondents'] if 'survey_no_of_respondents' in params else None
            survey_dashboard_password = params['survey_dashboard_password'] if 'survey_dashboard_password' in params else None

            if (
                survey_no_of_respondents == None or
                survey_dashboard_password == None
            ):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            if (survey_no_of_respondents not in survey_respondent_options):
                return {
                    'success' : False,
                    'message' : '`survey_no_of_respondents` parameter does not have the proper value'
                }, 400

            # Password checking and storage to follow
            password_min_char = 6
            regex = re.compile(r"^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$%^&])([a-zA-Z0-9!?@#$%^&]+)$")
            password_regex_check = regex.match(survey_dashboard_password)
            password_regex_check_result = password_regex_check.group(1) == survey_dashboard_password if password_regex_check != None else False
            password_length_check_result = len(survey_dashboard_password) >= password_min_char

            if (
                password_regex_check_result == False or
                password_length_check_result == False
            ):
                return {
                    'success' : False,
                    'message' : '`survey_dashboard_password` parameter does not have the proper value'
                }, 400

            # Hashing of password
            hashedPassword = self.hashPassword(survey_dashboard_password)

            survey_token = uuid.uuid4().hex[:6].upper()
            current_datetime = datetime.now()
            current_datetime_added_24_hrs = current_datetime + timedelta(days=1)

            data = {
                "token": survey_token,
                "dashboard_password": hashedPassword,
                "no_of_respondents": survey_no_of_respondents,
                "created_at": current_datetime,
                "expires_at": current_datetime_added_24_hrs
            }

            db = Database.connect()
            result = db.survey.insert_one(data).inserted_id
            if type(result) == ObjectId:
                return {
                    'success': True,
                    'message': 'Survey successfully created',
                    'token': survey_token,
                    'created_at': str(current_datetime)
                }
            
        except Exception as exception:
            return {'error': str(exception)}, 500
        finally:
            if type(db) == MongoClient:
                db.close()