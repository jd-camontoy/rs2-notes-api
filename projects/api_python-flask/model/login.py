import json
import os
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from pymongo import MongoClient
from model.survey import Survey

class Login(Resource):
    def post(self):
        db = None

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('params', type=str, help='')
            args = parser.parse_args()
            params = json.loads(args['params'])

            survey_token = params['survey_token'] if 'survey_token' in params else None
            survey_dashboard_password = params['survey_dashboard_password'] if 'survey_dashboard_password' in params else None

            if (
                survey_token == None or
                survey_dashboard_password == None
            ):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            submittedPasswordHashed = Survey.hashPassword(Survey, survey_dashboard_password)

            db = Database.connect()
            data = db.survey.find_one({ 'token': survey_token, 'dashboard_password': submittedPasswordHashed })

            if (data != None):
                return {
                    'success': True,
                    'data': {
                        '_id': str(data['_id']),
                        'token': str(data['token']),
                        'created_at': str(data['created_at']),
                        'expires_at': str(data['expires_at'])
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Entered credentials does not have a match'
                }, 400

        except Exception as exception:
            return {'error': str(exception)}, 500
        finally:
            if type(db) == MongoClient:
                db.close()

        