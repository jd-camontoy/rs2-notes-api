import json
import os
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from datetime import datetime, timedelta
import hashlib

class NoteList(Resource):
    def post(self):
        db = None

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('params', type=str, help='')
            args = parser.parse_args()
            params = json.loads(args['params'])

            user_id = params['user_id'] if 'user_id' in params else None

            if (user_id == None):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            if (user_id == ""):
                return {
                    'success' : False,
                    'message' : 'Cannot pass blank values'
                }, 400

            db = Database.connect()
            cursor = db.cursor()

            final_note_data = []

            search_notes = """
                SELECT id, title, content, created_at FROM note WHERE user_id=? ORDER BY created_at DESC
            """
            query_note_list_result = cursor.execute(search_notes, (user_id,))
            result_note_list = query_note_list_result.fetchall()

            search_note_labels = """
                SELECT label.name FROM label
                INNER JOIN note_label ON label.id = note_label.label_id
                WHERE note_label.note_id=?
            """

            for note in result_note_list:
                query_note_label_list_result = cursor.execute(search_note_labels, (note[0],))
                result_note_label_list = query_note_label_list_result.fetchall()
                note_label_list = []
                for note_label in result_note_label_list:
                    note_label_list.append(note_label[0])

                note_data = {
                    'id': note[0],
                    'title': note[1],
                    'content': note[2],
                    'created_at': note[3],
                    'labels': note_label_list
                }
                final_note_data.append(note_data)

            search_user_used_labels = """
                SELECT DISTINCT label.name FROM label
                INNER JOIN note_label ON label.id = note_label.label_id
                INNER JOIN note ON note_label.note_id = note.id
                WHERE note.user_id=?
            """
            query_user_used_labels_result = cursor.execute(search_user_used_labels, (user_id,))
            result_user_used_labels = query_user_used_labels_result.fetchall()
            user_used_labels = []
            for used_label in result_user_used_labels:
                user_used_labels.append(used_label[0])

            if (final_note_data != None):
                return {
                    'success': True,
                    'data': {
                        'notes': final_note_data,
                        'all_labels': user_used_labels
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