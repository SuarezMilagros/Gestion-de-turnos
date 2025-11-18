from flask import Flask, render_template, request, redirect, url_for
# Importamos la CLASE
from db_hospital import GestionTurnosHospital 

app = Flask(__name__)

# ----------------------------------------
# RUTAS PRINCIPALES (TURNOS)
# ----------------------------------------

@app.route('/')
def index():
    """Ruta principal: Muestra todos los turnos y el formulario de creación."""
    db = GestionTurnosHospital() 
    turnos = db.consultar_todos_turnos()
    entidades = db.obtener_entidades_para_form()
    db.cerrar() 
    
    return render_template('index.html', turnos=turnos, **entidades)

# --- RUTAS CRUD TURNOS ---
@app.route('/agregar', methods=['POST'])
def agregar_turno():
    """Ruta para CREAR un nuevo turno."""
    db = GestionTurnosHospital()
    if request.method == 'POST':
        db.agregar_turno(
            request.form['fecha'],
            request.form['horario'],
            request.form['id_paciente'],
            request.form['id_medico'],
            request.form['id_consultorio']
        )
    db.cerrar()
    return redirect(url_for('index'))

@app.route('/editar/<int:id_turno>', methods=['POST'])
def actualizar_turno(id_turno):
    """Ruta para ACTUALIZAR un turno existente."""
    db = GestionTurnosHospital()
    if request.method == 'POST':
        db.actualizar_turno(
            id_turno,
            request.form['fecha'],
            request.form['horario'],
            request.form['id_paciente'],
            request.form['id_medico'],
            request.form['id_consultorio']
        )
    db.cerrar()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id_turno>', methods=['POST'])
def eliminar_turno(id_turno):
    """Ruta para ELIMINAR un turno."""
    db = GestionTurnosHospital()
    db.eliminar_turno(id_turno)
    db.cerrar()
    return redirect(url_for('index'))

# ----------------------------------------
# RUTAS CRUD PARA MÉDICOS
# ----------------------------------------

@app.route('/medicos')
def medicos_index():
    """Ruta para MOSTRAR y CREAR médicos (Read y Create-Form)."""
    db = GestionTurnosHospital()
    medicos = db.consultar_medicos()
    db.cerrar()
    return render_template('medicos.html', medicos=medicos)

@app.route('/medico/agregar', methods=['POST'])
def medico_agregar():
    """Ruta para procesar la CREACIÓN de un médico."""
    if request.method == 'POST':
        db = GestionTurnosHospital()
        db.agregar_medico(
            request.form['nombre'],
            request.form['apellido'],
            request.form['especialidad'],
            request.form['telefono']
        )
        db.cerrar()
    return redirect(url_for('medicos_index'))

@app.route('/medico/editar/<int:id_medico>', methods=['GET', 'POST'])
def medico_editar(id_medico):
    """Ruta para MOSTRAR y PROCESAR la ACTUALIZACIÓN de un médico."""
    
    if request.method == 'POST':
        # Procesa el formulario de edición
        db = GestionTurnosHospital()
        db.actualizar_medico(
            id_medico,
            request.form['nombre'],
            request.form['apellido'],
            request.form['especialidad'],
            request.form['telefono']
        )
        db.cerrar()
        return redirect(url_for('medicos_index'))
    
    else:
        # Muestra el formulario de edición (Método GET)
        db = GestionTurnosHospital()
        medico = db.obtener_medico_por_id(id_medico)
        db.cerrar()
        
        if medico is None: # Si el médico no existe, volver a la lista
            return redirect(url_for('medicos_index'))
            
        return render_template('editar_medico.html', medico=medico)

@app.route('/medico/eliminar/<int:id_medico>', methods=['POST'])
def medico_eliminar(id_medico):
    """Ruta para ELIMINAR un médico (Delete)."""
    db = GestionTurnosHospital()
    db.eliminar_medico(id_medico)
    db.cerrar()
    return redirect(url_for('medicos_index'))

# ----------------------------------------
# RUTAS CRUD PARA PACIENTES
# ----------------------------------------

@app.route('/pacientes')
def pacientes_index():
    """Ruta para MOSTRAR y CREAR pacientes."""
    db = GestionTurnosHospital()
    pacientes = db.consultar_pacientes()
    db.cerrar()
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/paciente/agregar', methods=['POST'])
def paciente_agregar():
    """Ruta para procesar la CREACIÓN de un paciente."""
    if request.method == 'POST':
        db = GestionTurnosHospital()
        db.agregar_paciente(
            request.form['nombre'],
            request.form['apellido'],
            request.form['dni'],
            request.form['fecha_nacimiento'],
            request.form['genero'],
            request.form['telefono'],
            request.form['domicilio']
        )
        db.cerrar()
    return redirect(url_for('pacientes_index'))

@app.route('/paciente/editar/<int:id_paciente>', methods=['GET', 'POST'])
def paciente_editar(id_paciente):
    """Ruta para ACTUALIZAR un paciente."""
    
    if request.method == 'POST':
        db = GestionTurnosHospital()
        db.actualizar_paciente(
            id_paciente,
            request.form['nombre'],
            request.form['apellido'],
            request.form['dni'],
            request.form['fecha_nacimiento'],
            request.form['genero'],
            request.form['telefono'],
            request.form['domicilio']
        )
        db.cerrar()
        return redirect(url_for('pacientes_index'))
    
    else: # Método GET
        db = GestionTurnosHospital()
        paciente = db.obtener_paciente_por_id(id_paciente)
        db.cerrar()
        
        if paciente is None:
            return redirect(url_for('pacientes_index'))
            
        return render_template('editar_paciente.html', paciente=paciente)

@app.route('/paciente/eliminar/<int:id_paciente>', methods=['POST'])
def paciente_eliminar(id_paciente):
    """Ruta para ELIMINAR un paciente."""
    db = GestionTurnosHospital()
    db.eliminar_paciente(id_paciente)
    db.cerrar()
    return redirect(url_for('pacientes_index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)