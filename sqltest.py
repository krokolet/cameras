import sqlite3

# Подключаемся к базе данных (создается автоматически, если её нет)
conn = sqlite3.connect('cameras.db')
cursor = conn.cursor()

# Создаем таблицу для хранения камер
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cameras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL UNIQUE,
        login TEXT NOT NULL,
        password TEXT NOT NULL,
        rtsp_url TEXT DEFAULT '',
        width INTEGER DEFAULT 640,
        height INTEGER DEFAULT 480,
        running BOOLEAN DEFAULT FALSE
    );
''')

# Закрываем транзакцию
conn.commit()