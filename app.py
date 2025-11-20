from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
# Importamos la CLASE
from db_hospital import GestionTurnosHospital 

app = Flask(__name__)
# IMPORTANTE: La secret_key debe estar ANTES de usar session
app.secret_key = 'tu_clave_secreta_super_segura_cambiar_en_produccion_123456789'

# ----------------------------------------
# DECORADOR PARA PROTEGER RUTAS
# ----------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'dni_usuario' not in session:
            flash('Por favor, inicie sesión para acceder', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------------
# RUTAS DE AUTENTICACIÓN
# ----------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para iniciar sesión con DNI."""
    if request.method == 'POST':
        dni = request.form.get('dni')
        
        # Debug: Imprimir el DNI recibido
        print(f"DNI recibido: {dni}")
        
        db = GestionTurnosHospital()
        usuario = db.verificar_usuario(dni)
        db.cerrar()
        
        # Debug: Imprimir el usuario encontrado
        print(f"Usuario encontrado: {usuario}")
        
        if usuario:
            # Guardar información en la sesión
            session['dni_usuario'] = usuario['dni']
            session['nombre_usuario'] = f"{usuario['nombre']} {usuario['apellido']}"
            session['rol_usuario'] = usuario['rol']
            session['id_paciente'] = usuario['id_paciente']  # Guardar ID del paciente
            
            # Debug: Verificar que se guardó en la sesión
            print(f"Sesión guardada: {session}")
            
            flash(f'¡Bienvenido/a {session["nombre_usuario"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('DNI no encontrado. Por favor, verifique sus datos.', 'danger')
            return redirect(url_for('login'))
    
    # Si es GET, mostrar el formulario
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Ruta para cerrar sesión."""
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

# ----------------------------------------
# RUTAS PRINCIPALES (TURNOS) - PROTEGIDAS
# ----------------------------------------

@app.route('/')
@login_required
def index():
    """Ruta principal: Muestra todos los turnos y el formulario de creación."""
    db = GestionTurnosHospital()
    
    # Si el usuario tiene un paciente asociado, mostrar solo sus turnos
    if session.get('id_paciente'):
        turnos = db.consultar_turnos_paciente(session['id_paciente'])
        print(f"DEBUG - Usuario paciente: {session['nombre_usuario']}, ID: {session['id_paciente']}")
        print(f"DEBUG - Turnos del paciente: {len(turnos)}")
    else:
        # Si es admin, mostrar todos los turnos
        turnos = db.consultar_todos_turnos()
        print(f"DEBUG - Usuario admin: {session['nombre_usuario']}")
        print(f"DEBUG - Total de turnos: {len(turnos)}")
    
    entidades = db.obtener_entidades_para_form()
    
    print(f"DEBUG - Entidades obtenidas:")
    print(f"  - Pacientes: {len(entidades['pacientes'])}")
    print(f"  - Médicos: {len(entidades['medicos'])}")
    
    if entidades['medicos']:
        print(f"DEBUG - Primer médico: {entidades['medicos'][0]}")
    
    db.cerrar() 
    
    return render_template('index.html', turnos=turnos, **entidades)

# --- RUTAS CRUD TURNOS ---
@app.route('/agregar', methods=['POST'])
@login_required
def agregar_turno():
    """Ruta para CREAR un nuevo turno."""
    db = GestionTurnosHospital()
    if request.method == 'POST':
        # Si el usuario tiene paciente asociado, usar ese ID
        if session.get('id_paciente'):
            id_paciente = session['id_paciente']
        else:
            # Si es admin, permitir seleccionar paciente
            id_paciente = request.form.get('id_paciente')
        
        db.agregar_turno(
            request.form['fecha'],
            request.form['horario'],
            id_paciente,
            request.form['id_medico']
        )
        flash('Turno agregado exitosamente', 'success')
    db.cerrar()
    return redirect(url_for('index'))

@app.route('/editar/<int:id_turno>', methods=['POST'])
@login_required
def actualizar_turno(id_turno):
    """Ruta para ACTUALIZAR un turno existente."""
    db = GestionTurnosHospital()
    if request.method == 'POST':
        # Si el usuario tiene paciente asociado, usar ese ID
        if session.get('id_paciente'):
            id_paciente = session['id_paciente']
        else:
            # Si es admin, permitir seleccionar paciente
            id_paciente = request.form.get('id_paciente')
            
        db.actualizar_turno(
            id_turno,
            request.form['fecha'],
            request.form['horario'],
            id_paciente,
            request.form['id_medico']
        )
        flash('Turno actualizado exitosamente', 'success')
    db.cerrar()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id_turno>', methods=['POST'])
@login_required
def eliminar_turno(id_turno):
    """Ruta para ELIMINAR un turno."""
    db = GestionTurnosHospital()
    db.eliminar_turno(id_turno)
    db.cerrar()
    return redirect(url_for('index'))

# ----------------------------------------
# RUTAS CRUD PARA MÉDICOS - PROTEGIDAS
# ----------------------------------------

@app.route('/medicos')
@login_required
def medicos_index():
    """Ruta para MOSTRAR y CREAR médicos (Read y Create-Form)."""
    db = GestionTurnosHospital()
    medicos = db.consultar_medicos()
    db.cerrar()
    return render_template('medicos.html', medicos=medicos)

@app.route('/medico/agregar', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def medico_eliminar(id_medico):
    """Ruta para ELIMINAR un médico (Delete)."""
    db = GestionTurnosHospital()
    db.eliminar_medico(id_medico)
    db.cerrar()
    return redirect(url_for('medicos_index'))

# ----------------------------------------
# RUTAS CRUD PARA PACIENTES - PROTEGIDAS
# ----------------------------------------

@app.route('/pacientes')
@login_required
def pacientes_index():
    """Ruta para MOSTRAR y CREAR pacientes."""
    db = GestionTurnosHospital()
    pacientes = db.consultar_pacientes()
    db.cerrar()
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/paciente/agregar', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def paciente_eliminar(id_paciente):
    """Ruta para ELIMINAR un paciente."""
    db = GestionTurnosHospital()
    db.eliminar_paciente(id_paciente)
    db.cerrar()
    return redirect(url_for('pacientes_index'))

# ----------------------------------------
# RUTAS CRUD PARA USUARIOS - PROTEGIDAS
# ----------------------------------------

@app.route('/usuarios')
@login_required
def usuarios_index():
    """Ruta para MOSTRAR y CREAR usuarios."""
    db = GestionTurnosHospital()
    usuarios = db.consultar_usuarios()
    db.cerrar()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuario/agregar', methods=['POST'])
@login_required
def usuario_agregar():
    """Ruta para procesar la CREACIÓN de un usuario."""
    if request.method == 'POST':
        db = GestionTurnosHospital()
        db.agregar_usuario(
            request.form['nombre'],
            request.form['apellido'],
            request.form['dni'],
            request.form['rol']
        )
        db.cerrar()
        flash('Usuario agregado correctamente', 'success')
    return redirect(url_for('usuarios_index'))

@app.route('/usuario/editar/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
def usuario_editar(id_usuario):
    """Ruta para ACTUALIZAR un usuario."""
    
    if request.method == 'POST':
        db = GestionTurnosHospital()
        db.actualizar_usuario(
            id_usuario,
            request.form['nombre'],
            request.form['apellido'],
            request.form['dni'],
            request.form['rol']
        )
        db.cerrar()
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('usuarios_index'))
    
    else: # Método GET
        db = GestionTurnosHospital()
        usuario = db.obtener_usuario_por_id(id_usuario)
        db.cerrar()
        
        if usuario is None:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('usuarios_index'))
            
        return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuario/eliminar/<int:id_usuario>', methods=['POST'])
@login_required
def usuario_eliminar(id_usuario):
    """Ruta para ELIMINAR un usuario."""
    db = GestionTurnosHospital()
    db.eliminar_usuario(id_usuario)
    db.cerrar()
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('usuarios_index'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)