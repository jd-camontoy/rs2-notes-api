import json
import os
from flask import jsonify
from flask_restful import Resource, reqparse
from database import Database
from bson.objectid import ObjectId
from datetime import datetime
from pymongo import MongoClient

class SurveyResponse(Resource):
    def post(self):
        db = None
        selected_motivated = 1
        selected_demotivated = 2
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('params', type=str, help='')
            args = parser.parse_args()
            params = json.loads(args['params'])

            survey_token = params['survey_token'] if 'survey_token' in params else None
            answer_motivated = params['answer_motivated'] if 'answer_motivated' in params else None
            answer_keywords = params['answer_keywords'] if 'answer_keywords' in params else None
            survey_id = params['survey_id'] if 'survey_id' in params else None

            if (
                survey_token == None or
                answer_motivated == None or
                answer_keywords == None
            ):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            if answer_motivated == selected_motivated:
                answer_motivated = True
            elif answer_motivated == selected_demotivated:
                answer_motivated = False
            else:  
                return {
                    'success' : False,
                    'message' : '`answer_motivated` parameter does not have the proper value'
                }, 400


            if (
                not isinstance(answer_keywords, list) or
                not answer_keywords
            ):
                return {
                    'success' : False,
                    'message' : '`answer_keywords` parameter does not have the proper value'
                }, 400

            data = {
                "survey_token": survey_token,
                "motivated": answer_motivated,
                "keywords": answer_keywords,
                "created_at": datetime.now()
            }

            if (survey_id != None):
                data['survey_id'] = ObjectId(str(survey_id))

            db = Database.connect()
            result = db.survey_response.insert_one(data).inserted_id
            if type(result) == ObjectId:
                return {
                    'success': True,
                    'message': 'Survey response successfully submitted'
                }
        except Exception as exception:
            return {'error': str(exception)}, 500
        finally:
            if type(db) == MongoClient:
                db.close()