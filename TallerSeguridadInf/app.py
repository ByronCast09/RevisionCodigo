from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_demo'

# Crear la base de datos si no existe
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT,
        role TEXT
    )
    ''')
    
    # Insertar algunos usuarios de prueba
    try:
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)", 
                      ('admin', 'admin123', 'admin@example.com', 'admin'))
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)", 
                      ('user1', 'password1', 'user1@example.com', 'user'))
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)", 
                      ('user2', 'password2', 'user2@example.com', 'user'))
    except sqlite3.IntegrityError:
        # Los usuarios ya existen
        pass
    
    conn.commit()
    conn.close()

# Inicializar la base de datos
init_db()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Login vulnerable a inyección SQL (Método 1)
@app.route('/login_vulnerable', methods=['GET', 'POST'])
def login_vulnerable():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # VULNERABLE: Concatenación directa de la entrada del usuario en la consulta SQL
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Corregimos la consulta para que funcione con inyección SQL
        query = f"SELECT * FROM users WHERE username = '{username}' OR username LIKE '%{username}%' AND password = '{password}'"
        
        # Mostrar la consulta SQL para fines educativos
        print(f"Consulta SQL ejecutada: {query}")
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            
            if user:
                session['logged_in'] = True
                session['username'] = user[1]
                session['role'] = user[4]
                flash('¡Has iniciado sesión correctamente! (Inyección SQL exitosa)', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Credenciales inválidas. Inténtalo de nuevo.'
        except sqlite3.Error as e:
            error = f"Error en la consulta SQL: {str(e)}"
        
        conn.close()
    
    return render_template('login_vulnerable.html', error=error)

# Búsqueda de usuarios vulnerable a inyección SQL (Método 2)
@app.route('/search_vulnerable', methods=['GET', 'POST'])
def search_vulnerable():
    results = []
    error = None
    
    if request.method == 'POST':
        search_term = request.form['search_term']
        
        # VULNERABLE: Concatenación directa en la cláusula WHERE
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = f"SELECT id, username, email, role FROM users WHERE username LIKE '%{search_term}%' OR email LIKE '%{search_term}%'"
        
        try:
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            error = f"Error en la consulta SQL: {str(e)}"
        
        conn.close()
    
    return render_template('search_vulnerable.html', results=results, error=error)

# Login seguro contra inyección SQL
@app.route('/login_secure', methods=['GET', 'POST'])
def login_secure():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # SEGURO: Uso de parámetros en la consulta SQL
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            
            if user:
                session['logged_in'] = True
                session['username'] = user[1]
                session['role'] = user[4]
                flash('¡Has iniciado sesión correctamente!', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Credenciales inválidas. Inténtalo de nuevo.'
        except sqlite3.Error as e:
            error = f"Error en la consulta SQL: {str(e)}"
        
        conn.close()
    
    return render_template('login_secure.html', error=error)

# Dashboard después de iniciar sesión
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash('Debes iniciar sesión primero', 'danger')
        return redirect(url_for('index'))
    
    return render_template('dashboard.html')

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)