import sqlite3

class Database:
    def connect():
        try:
            connection = sqlite3.connect('rs2_note_app.db')
            return connection
        except Exception as exception:
            return {'error': str(exception)}, 500