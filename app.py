from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Función para conectar a la base de datos
def conectar():
    return sqlite3.connect('tareas.db')

# Crear la tabla si no existe
with conectar() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            completada INTEGER DEFAULT 0,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')


# Obtener todas las tareas
@app.route('/api/tareas', methods=['GET'])
def obtener_tareas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, descripcion, completada, fecha_creacion FROM tareas")
    tareas = [
        {
            "id": id_,
            "descripcion": desc,
            "completada": bool(comp),
            "fecha_creacion": fecha
        }
        for id_, desc, comp, fecha in cursor.fetchall()
    ]
    conn.close()
    return jsonify(tareas)

# Añadir una nueva tarea
@app.route('/api/tareas', methods=['POST'])
def crear_tarea():
    datos = request.json
    descripcion = datos.get("descripcion", "").strip()
    if not descripcion:
        return jsonify({"error": "Descripción vacía"}), 400

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tareas (descripcion) VALUES (?)", (descripcion,))
    conn.commit()
    nueva_id = cursor.lastrowid
    cursor.execute("SELECT fecha_creacion FROM tareas WHERE id = ?", (nueva_id,))
    fecha = cursor.fetchone()[0]
    conn.close()

    return jsonify({"id": nueva_id, "descripcion": descripcion, "completada": False, "fecha_creacion": fecha}), 201

# Marcar como completada
@app.route('/api/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea(id):
    datos = request.json
    descripcion = datos.get("descripcion")
    completada = datos.get("completada")

    conn = conectar()
    cursor = conn.cursor()

    if descripcion is not None:
        cursor.execute("UPDATE tareas SET descripcion = ? WHERE id = ?", (descripcion, id))

    if completada is not None:
        cursor.execute("UPDATE tareas SET completada = ? WHERE id = ?", (int(completada), id))

    conn.commit()
    conn.close()

    return jsonify({"id": id, "descripcion": descripcion, "completada": completada})

 # Eliminar una tarea
@app.route('/api/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"resultado": "Tarea eliminada"})
    print(f"Tarea con ID {id} eliminada de la base de datos.")

if __name__ == '__main__':
    from flask import send_from_directory

    @app.route('/')
    def home():
        return send_from_directory('static', 'tareas.html')


    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






