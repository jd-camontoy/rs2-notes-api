import json
import os
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from pymongo import MongoClient 

class Dashboard(Resource):
    def post(self):
        db = None
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, help='')
            args = parser.parse_args()

            token = args['token'] if 'token' in args else None

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
                current_response_count = db.survey_response.count_documents({ 'survey_token': token })
                motivated_response_count = db.survey_response.count_documents({ 'survey_token': token, 'motivated': True })
                demotivated_reponse_count = db.survey_response.count_documents({ 'survey_token': token, 'motivated': False })

                response_limit = data['no_of_respondents']
                mention_count_for_keyword = []
                data = db.survey_settings.find_one({}, { '_id': 0, 'keywords_selection': 1 })

                for keywords_selection_option in data['keywords_selection']:
                    keyword_result_motivated = db.survey_response.count_documents({ 
                        'survey_token': token,
                        'motivated': True,
                        'keywords': keywords_selection_option
                    })
                    keyword_result_demotivated = db.survey_response.count_documents({ 
                        'survey_token': token,
                        'motivated': False,
                        'keywords': keywords_selection_option
                    })
                    response_count_data = {
                        'keyword': keywords_selection_option,
                        'motivated': keyword_result_motivated,
                        'demotivated': keyword_result_demotivated
                    }
                    mention_count_for_keyword.append(response_count_data)

                data = {
                    'current_response_count': current_response_count,
                    'response_limit': response_limit,
                    'motivated_response_count': motivated_response_count,
                    'demotivated_response_count': demotivated_reponse_count,
                    'mention_count_for_keyword': mention_count_for_keyword
                }

                return {
                    'success': True,
                    'data': data
                }

        except Exception as exception:
            return {'error': str(exception)}, 500
        finally:
            if type(db) == MongoClient:
                db.close()