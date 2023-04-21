import json
import os
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from datetime import datetime, timedelta
import hashlib

class User(Resource):
    def hashPassword(self, password):
        hashString = hashlib.sha1(password.encode('utf-8'))
        hashedString = hashString.hexdigest()
        no_of_iterations = 2
        for i in range(int(no_of_iterations)):
            hashedString = hashedString + str(i)
            hashString = hashlib.sha1(hashedString.encode('utf-8'))
            hashedString = hashString.hexdigest()
        return hashedString

    def post(self):
        db = None

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('params', type=str, help='')
            args = parser.parse_args()
            params = json.loads(args['params'])

            user_first_name = params['first_name'] if 'first_name' in params else None
            user_surname = params['surname'] if 'surname' in params else None
            user_password = params['password'] if 'password' in params else None

            if (
                user_first_name == None or
                user_surname == None or
                user_password == None
            ):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            if (
                user_first_name == "" or
                user_surname == "" or
                user_password == ""
            ):
                return {
                    'success' : False,
                    'message' : 'Cannot pass blank values'
                }, 400

            submittedPasswordHashed = self.hashPassword(user_password)

            db = Database.connect()
            cursor = db.cursor()

            insert_user = """INSERT INTO user (name, surname, password)
                VALUES (?, ?, ?)
            """
            cursor.execute(insert_user, (user_first_name, user_surname, submittedPasswordHashed,))
            db.commit()
            new_user_id = cursor.lastrowid

            # data = []
            # key = ('id', 'name', 'surname')
            # item = (result[0], result[1], result[2])
            # data.append(dict(zip(key, item)))

            # return {
            #     # 'id': str(result[0]),
            #     'hashed1': submittedPasswordHashed,
            #     # 'hashed2': result[3]
            # }

            if (new_user_id != None):
                return {
                    'success': True,
                    'data': {
                        'id': str(new_user_id),
                        'name': str(user_first_name + " " + user_surname)
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Entered credentials does not have a match'
                }, 400
            
            db.close()

        except Exception as exception:
            return {'error': str(exception)}, 500