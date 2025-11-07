# Demostración de Inyección SQL con Flask

Este proyecto es una demostración educativa de vulnerabilidades de inyección SQL y cómo prevenirlas utilizando Flask y SQLite.

## Instalación

1. Instala las dependencias:
```
pip install -r requirements.txt
```

2. Ejecuta la aplicación:
```
python app.py
```

3. Abre tu navegador en `http://127.0.0.1:5000`

## Características

La aplicación incluye:

1. **Login vulnerable a inyección SQL (Método 1)**
   - Utiliza concatenación directa de strings en la consulta SQL
   - Vulnerable a bypass de autenticación

2. **Búsqueda de usuarios vulnerable a inyección SQL (Método 2)**
   - Utiliza concatenación directa en la cláusula WHERE
   - Vulnerable a ataques UNION y extracción de datos

3. **Login seguro contra inyección SQL**
   - Utiliza consultas parametrizadas
   - Resistente a ataques de inyección SQL

## Ejemplos de Ataques

### Login Vulnerable

- **Bypass de autenticación**: Ingresa `' OR '1'='1` como nombre de usuario y cualquier contraseña.
- **Comentar el resto de la consulta**: Ingresa `admin' --` como nombre de usuario (omite la contraseña).

### Búsqueda Vulnerable

- **Ver todos los usuarios**: Ingresa `' OR '1'='1` en el campo de búsqueda.
- **Ataque UNION**: Ingresa `' UNION SELECT 1,2,3,4 --` para probar la estructura de la tabla.
- **Extracción de datos**: Ingresa `' UNION SELECT id, username, password, role FROM users --` para extraer contraseñas.

### Login Seguro

- Intenta los mismos ataques que funcionaron en la página vulnerable y verás que aquí no funcionan.

## Usuarios de Prueba

- Usuario: admin, Contraseña: admin123
- Usuario: user1, Contraseña: password1
- Usuario: user2, Contraseña: password2

## Advertencia

Este proyecto es solo para fines educativos. No utilices estas técnicas en sistemas reales sin autorización explícita.