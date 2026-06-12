from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from datetime import datetime

app = Flask(__name__)
app.secret_key = "cecytosweb"

try:
    cliente = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=5000
    )

    cliente.server_info()

    db = cliente["cecytosweb"]
    usuarios = db["usuarios"]
    resultados_quiz = db["resultados_quiz"]

except ServerSelectionTimeoutError:
    cliente = None
    usuarios = None
    print("ERROR: No se pudo conectar a MongoDB")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if usuarios is None:
        return "Error: MongoDB no está conectado"

    if request.method == 'POST':

        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']

        existe = usuarios.find_one({"correo": correo})

        if existe:
            return "Este correo ya está registrado"

        usuarios.insert_one({
            "nombre": nombre,
            "correo": correo,
            "password": password
        })

        return redirect(url_for('login'))

    return render_template("registro.html")


@app.route('/login', methods=['GET', 'POST'])
def login():

    if usuarios is None:
        return "Error: MongoDB no está conectado"

    if request.method == 'POST':

        correo = request.form['correo']
        password = request.form['password']

        usuario = usuarios.find_one({
            "correo": correo,
            "password": password
        })

        if usuario:
            session['usuario'] = usuario['nombre']
            return redirect(url_for('inicio'))

        return "Correo o contraseña incorrectos"

    return render_template("login.html")


@app.route('/inicio')
def inicio():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    return render_template(
        "inicio.html",
        usuario=session['usuario']
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Módulos

@app.route('/modulo1')
def modulo1():
    return render_template("modulo1.html")


@app.route('/modulo2')
def modulo2():
    return render_template("modulo2.html")


@app.route('/modulo3')
def modulo3():
    return render_template("modulo3.html")


@app.route('/modulo4')
def modulo4():
    return render_template("modulo4.html")

@app.route('/guardar_quiz_modulo2', methods=['POST'])
def guardar_quiz_modulo2():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    respuestas_correctas = {
        "p1": "a",
        "p2": "b",
        "p3": "b",
        "p4": "a",
        "p5": "b",
        "p6": "a",
        "p7": "b",
        "p8": "b",
        "p9": "a",
        "p10": "b"
    }

    puntaje = 0
    respuestas_usuario = {}

    for pregunta, correcta in respuestas_correctas.items():

        respuesta = request.form.get(pregunta)

        respuestas_usuario[pregunta] = respuesta

        if respuesta == correcta:
            puntaje += 1

    porcentaje = round((puntaje / 10) * 100)

    resultados_quiz.insert_one({
        "usuario": session['usuario'],
        "modulo": "Modulo 2",
        "puntaje": puntaje,
        "porcentaje": porcentaje,
        "respuestas": respuestas_usuario,
        "fecha": datetime.now()
    })

    return render_template(
        "resultado_quiz.html",
        usuario=session['usuario'],
        puntaje=puntaje,
        porcentaje=porcentaje
    )

if __name__ == '__main__':
    app.run(debug=True)