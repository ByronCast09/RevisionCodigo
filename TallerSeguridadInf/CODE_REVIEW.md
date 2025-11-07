# Code Review: Aplicación de Demostración de Inyección SQL

## Introducción

Este documento presenta un análisis detallado del código de la aplicación Flask diseñada para demostrar vulnerabilidades de inyección SQL y cómo prevenirlas. La aplicación incluye intencionalmente dos implementaciones vulnerables y una implementación segura para fines educativos.

## Estructura del Proyecto

```
├── app.py                  # Archivo principal de la aplicación Flask
├── database.db             # Base de datos SQLite
├── requirements.txt        # Dependencias del proyecto
└── templates/              # Plantillas HTML
    ├── dashboard.html      # Página del panel de control
    ├── index.html          # Página principal
    ├── login_secure.html   # Implementación segura de login
    ├── login_vulnerable.html # Implementación vulnerable de login
    └── search_vulnerable.html # Implementación vulnerable de búsqueda
```

## Análisis de Código

### 1. Inicialización de la Base de Datos

```python
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
        # Más inserciones...
    except sqlite3.IntegrityError:
        # Los usuarios ya existen
        pass
```

**Observaciones:**
- La función crea una tabla de usuarios si no existe
- Inserta usuarios de prueba con credenciales predefinidas
- Utiliza consultas parametrizadas para la inserción de datos (seguro)
- Maneja excepciones de integridad para evitar duplicados

### 2. Implementación Vulnerable: Login con Inyección SQL

```python
@app.route('/login_vulnerable', methods=['GET', 'POST'])
def login_vulnerable():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # VULNERABLE: Concatenación directa de la entrada del usuario en la consulta SQL
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Consulta vulnerable a inyección SQL
        query = f"SELECT * FROM users WHERE username = '{username}' OR username LIKE '%{username}%' AND password = '{password}'"
        
        # Mostrar la consulta SQL para fines educativos
        print(f"Consulta SQL ejecutada: {query}")
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            
            if user:
                # Iniciar sesión...
```

**Vulnerabilidad:**
- **Concatenación directa**: La entrada del usuario se inserta directamente en la consulta SQL sin sanitización
- **Operador OR**: La consulta incluye un operador OR que facilita la inyección
- **Operador LIKE**: Permite búsquedas parciales, aumentando la superficie de ataque

**Vector de ataque:**
- Ingresar `' OR '1'='1` como nombre de usuario
- La consulta se convierte en: `SELECT * FROM users WHERE username = '' OR '1'='1' OR username LIKE '%' OR '1'='1%' AND password = '...'`
- La condición `'1'='1'` siempre es verdadera, permitiendo el acceso sin credenciales válidas

### 3. Implementación Vulnerable: Búsqueda de Usuarios

```python
@app.route('/search_vulnerable', methods=['GET', 'POST'])
def search_vulnerable():
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
```

**Vulnerabilidad:**
- **Concatenación directa**: Similar al login vulnerable, la entrada del usuario se inserta sin sanitización
- **Operador LIKE con comodines**: Aumenta la superficie de ataque

**Vector de ataque:**
- Ingresar `%' OR '1'='1` para ver todos los usuarios
- Ingresar `%' UNION SELECT 1,2,3,4 --` para realizar un ataque UNION
- La consulta se convierte en: `SELECT id, username, email, role FROM users WHERE username LIKE '%%' OR '1'='1%' OR email LIKE '%%' OR '1'='1%'`

### 4. Implementación Segura: Login Parametrizado

```python
@app.route('/login_secure', methods=['GET', 'POST'])
def login_secure():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # SEGURO: Uso de parámetros en la consulta SQL
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
```

**Medidas de seguridad:**
- **Consultas parametrizadas**: Utiliza marcadores de posición (`?`) y pasa los valores como parámetros
- **Separación de datos y código**: El motor de base de datos trata los parámetros como datos, no como parte de la consulta
- **Sin concatenación directa**: Elimina el riesgo de inyección SQL

## Comparación de Métodos

| Aspecto | Implementación Vulnerable | Implementación Segura |
|---------|---------------------------|----------------------|
| Construcción de consulta | Concatenación directa de strings | Consultas parametrizadas |
| Tratamiento de entrada | Sin sanitización | Tratada como datos, no como código |
| Resistencia a inyección | Vulnerable | Resistente |
| Operadores de riesgo | OR, LIKE con comodines | Ninguno |

## Ejemplos de Inyección SQL

### Para el Login Vulnerable:
1. **Bypass de autenticación**: `' OR '1'='1`
   - Resultado: Acceso como el primer usuario en la base de datos
2. **Comentar resto de la consulta**: `admin'--`
   - Resultado: Acceso como admin sin necesidad de contraseña

### Para la Búsqueda Vulnerable:
1. **Ver todos los usuarios**: `%' OR '1'='1`
   - Resultado: Muestra todos los usuarios en la base de datos
2. **Ataque UNION**: `%' UNION SELECT 1,2,3,4 --`
   - Resultado: Combina resultados con datos arbitrarios

## Mejores Prácticas de Prevención

1. **Usar siempre consultas parametrizadas o preparadas**
2. **Implementar ORM (Object-Relational Mapping)** como SQLAlchemy
3. **Validar y sanitizar todas las entradas de usuario**
4. **Aplicar el principio de mínimo privilegio** en las conexiones a la base de datos
5. **Implementar WAF (Web Application Firewall)** para detectar y bloquear patrones de inyección
6. **Realizar auditorías de código regulares** para identificar vulnerabilidades

## Conclusión

Esta aplicación demuestra claramente el contraste entre implementaciones vulnerables y seguras frente a ataques de inyección SQL. Las implementaciones vulnerables ilustran cómo la concatenación directa de entradas de usuario en consultas SQL crea graves riesgos de seguridad, mientras que el uso de consultas parametrizadas proporciona una protección efectiva contra estos ataques.

Es importante recordar que esta aplicación está diseñada con fines educativos y no debe utilizarse en entornos de producción.