import sqlite3

try:
    connection = sqlite3.connect('rs2_note_app.db')
    cursor = connection.cursor()

    create_user_query = """CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        password TEXT NOT NULL
    );"""
    cursor.execute(create_user_query)

    create_note_query = """CREATE TABLE IF NOT EXISTS note (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_updated TEXT,
        FOREIGN KEY (user_id) 
            REFERENCES user (id)
    );"""
    cursor.execute(create_note_query)

    create_label_query = """CREATE TABLE IF NOT EXISTS label (
        id INTEGER PRIMARY KEY,
        name INTEGER
    );"""
    cursor.execute(create_label_query)

    create_note_label_query = """CREATE TABLE IF NOT EXISTS note_label (
        label_id INTEGER NOT NULL,
        note_id INTEGER NOT NULL,
        FOREIGN KEY (label_id) 
            REFERENCES label (id)
                ON DELETE CASCADE 
                ON UPDATE NO ACTION,
        FOREIGN KEY (note_id) 
            REFERENCES note (id)
                ON DELETE CASCADE 
                ON UPDATE NO ACTION
    );"""
    cursor.execute(create_note_label_query)

    insert_first_user = """INSERT INTO user (name, surname, password)
        VALUES ('JD', 'Camontoy', '55ff96e1444dcac08a7e11872f4b5afee34b457d');"""
    cursor.execute(insert_first_user)

    print('Database initialized')

    connection.commit()
    connection.close()
except Exception as e:
    print(e)