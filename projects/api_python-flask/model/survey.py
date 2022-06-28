import json
import os
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from datetime import datetime
from pymongo import MongoClient

class Survey(Resource):
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
