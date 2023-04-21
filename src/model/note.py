import json
import os
from flask import jsonify
from flask_restful import Resource, reqparse, request
from database import Database
from datetime import datetime, timedelta
import hashlib

class Note(Resource):
    def post(self):
        db = None

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('params', type=str, help='')
            args = parser.parse_args()
            params = json.loads(args['params'])

            note_title = params['title'] if 'title' in params else None
            note_content = params['content'] if 'content' in params else None
            note_user_id = params['user_id'] if 'user_id' in params else None
            note_label_list = params['label_list'] if 'label_list' in params else None


            if (
                note_title == None or
                note_content == None or
                note_user_id == None or
                note_label_list == None
            ):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            if (
                note_title == "" or
                note_content == "" or
                note_user_id == "" or
                note_label_list == None
            ):
                return {
                    'success' : False,
                    'message' : 'Cannot pass blank values'
                }, 400

            db = Database.connect()
            cursor = db.cursor()

            search_label = """
                SELECT id FROM label WHERE name=? COLLATE NOCASE LIMIT 1
            """
            insert_label = """INSERT INTO label (name) VALUES (?)"""

            labels_to_insert = []

            for label in note_label_list:
                query_result_search_label = cursor.execute(search_label, (label,))
                result_search_label = query_result_search_label.fetchone()
                if (result_search_label):
                    labels_to_insert.append(result_search_label[0])
                else:
                    cursor.execute(insert_label, (label,))
                    db.commit()
                    new_label_id = cursor.lastrowid
                    labels_to_insert.append(new_label_id)                

            insert_user = """INSERT INTO note (title, content, created_at, user_id)
                VALUES (?, ?, datetime(), ?)
            """
            cursor.execute(insert_user, (note_title, note_content, note_user_id,))
            db.commit()
            new_note_id = cursor.lastrowid

            insert_note_label = """INSERT INTO note_label (label_id, note_id) VALUES (?, ?)"""

            if (labels_to_insert):
                for final_label_id in labels_to_insert:
                    cursor.execute(insert_note_label, (final_label_id, new_note_id,))
                    db.commit()

            if (new_note_id != None):
                return {
                    'success': True,
                    'data': {
                        'id': str(new_note_id),
                        'title': str(note_title)
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
    
    def put(self):
        db = None

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('params', type=str, help='')
            args = parser.parse_args()
            params = json.loads(args['params'])

            note_new_title = params['new_title'] if 'new_title' in params else None
            note_new_content = params['new_content'] if 'new_content' in params else None
            added_labels = params['added_labels'] if 'added_labels' in params else None
            removed_labels = params['removed_labels'] if 'removed_labels' in params else None
            note_id = params['note_id'] if 'note_id' in params else None

            if (
                (note_new_title != None and note_new_title == "") or
                (note_new_content != None and note_new_content == "") or
                (added_labels != None and not added_labels) or
                (removed_labels != None and not removed_labels) or
                (note_id != None and note_id == "")
            ):
                return {
                    'success' : False,
                    'message' : 'Cannot pass blank values'
                }, 400

            db = Database.connect()
            cursor = db.cursor()

            if (note_new_title and not note_new_content):
                update_query = """
                    UPDATE note
                    SET title=?
                    WHERE id=?
                """
                cursor.execute(update_query, (note_new_title, note_id,))

            if (note_new_content and not note_new_title):
                update_query = """
                    UPDATE note
                    SET content=?
                    WHERE id=?
                """
                cursor.execute(update_query, (note_new_content, note_id,))

            if (note_new_content and note_new_title):
                update_query = """
                    UPDATE note
                    SET title=?, content=?
                    WHERE id=?
                """
                cursor.execute(update_query, (note_new_title, note_new_content, note_id,))

            db.commit()
            affected_rows_note = cursor.rowcount
            
            affected_rows_deleted_note_label = 0
            affected_rows_deleted_label = 0

            labels_to_be_inserted = []
            note_labels_to_be_inserted = [];
            note_labels_to_be_deleted = [];

            if (added_labels or removed_labels):
                search_label = """
                    SELECT id FROM label WHERE name=? COLLATE NOCASE LIMIT 1
                """

                if (added_labels):
                    for added_label in added_labels:
                        query_result_added_label = cursor.execute(search_label, (added_label,))
                        result_search_label = query_result_added_label.fetchone()
                        if (result_search_label):
                            note_labels_to_be_inserted.append(result_search_label[0])
                        else:
                            labels_to_be_inserted.append(added_label)
                
                if (removed_labels):
                    for removed_label in removed_labels:
                        query_result_remove_label = cursor.execute(search_label, (removed_label,))
                        result_search_label = query_result_remove_label.fetchone()
                        if (result_search_label):
                            note_labels_to_be_deleted.append(result_search_label[0])

                insert_label = """INSERT INTO label (name) VALUES (?)"""

                if (labels_to_be_inserted):
                    for new_label in labels_to_be_inserted:
                        cursor.execute(insert_label, (new_label,))
                        db.commit()
                        new_label_id = cursor.lastrowid
                        note_labels_to_be_inserted.append(new_label_id)   

                insert_note_label = """INSERT INTO note_label (label_id, note_id) VALUES (?, ?)"""

                if (note_labels_to_be_inserted):
                    for new_note_label in note_labels_to_be_inserted:
                        cursor.execute(insert_note_label, (new_note_label, note_id,))
                        db.commit()

                delete_note_label = """
                    DELETE FROM note_label WHERE note_id=? AND label_id=?
                """

                if (note_labels_to_be_deleted):
                    for note_label_to_be_deleted in note_labels_to_be_deleted:
                        cursor.execute(delete_note_label, (note_id, note_label_to_be_deleted,))
                        db.commit()
                        affected_rows_deleted_note_label = cursor.rowcount
                
                    query_deleted_label_usage = """SELECT COUNT(*) FROM note_label WHERE label_id=?"""
                    delete_label = """DELETE FROM label WHERE id=?"""

                    for note_label_to_be_deleted in note_labels_to_be_deleted:
                        query_result_usage_label = cursor.execute(query_deleted_label_usage, (note_label_to_be_deleted,))
                        result_usage_label = query_result_usage_label.fetchone()
                        if (result_usage_label and result_usage_label[0] <= 0):
                            cursor.execute(delete_label, (note_label_to_be_deleted,))
                            db.commit()
                            affected_rows_deleted_label = cursor.rowcount

            if (affected_rows_note):
                return {
                    'success': True,
                    'data': {
                        'id': str(note_id),
                        'deleted_note_labels': affected_rows_deleted_note_label,
                        'deleted_labels': affected_rows_deleted_label
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

    def delete(self):
        db = None

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('params', type=str, help='')
            args = parser.parse_args()
            params = json.loads(args['params'])

            note_id = params['note_id'] if 'note_id' in params else None

            if (note_id == None):
                return {
                    'success' : False,
                    'message' : 'Incomplete parameters'
                }, 400

            if (note_id == ""):
                return {
                    'success' : False,
                    'message' : 'Cannot pass blank values'
                }, 400

            db = Database.connect()
            cursor = db.cursor()

            delete_note = """
                DELETE FROM note WHERE id=?
            """

            cursor.execute(delete_note, (note_id,))
            db.commit()
            affected_rows = cursor.rowcount

            if (affected_rows):
                return {
                    'success': True,
                    'data': {
                        'id': str(note_id),
                        'affected_rows': str(affected_rows)
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

