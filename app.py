# app.py
from flask import Flask, request
import sqlite3
import subprocess

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, secret TEXT)')
    c.execute('INSERT OR IGNORE INTO users (id, username, secret) VALUES (1, "admin", "super_secret_flag{sqli_success}")')
    conn.commit()
    conn.close()

@app.route('/user')
def get_user():
    username = request.args.get('username', '')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Уязвимость 1: SQL Injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    
    try:
        c.execute(query)
        user = c.fetchone()
        return f"Данные пользователя: {user}" if user else "Пользователь не найден"
    except sqlite3.Error as e:
        return f"Ошибка БД: {e}"

@app.route('/ping')
def ping():
    host = request.args.get('host', '127.0.0.1')
    
    # Уязвимость 2: OS Command Injection (с учетом Windows cp866 для корректного отображения вывода)
    command = f"ping -n 1 {host}" 
    
    try:
        raw_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output = raw_output.decode('cp866', errors='ignore')
        return f"<pre>{output}</pre>"
    except subprocess.CalledProcessError as e:
        err_output = e.output.decode('cp866', errors='ignore') if hasattr(e, 'output') else str(e)
        return f"<pre>Ошибка выполнения:\n{err_output}</pre>"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
