import sqlite3
import os
from datetime import datetime

class GestionTurnosHospital:
    """Clase para la conexión y gestión de la base de datos SQLite."""
    
    def __init__(self, nombre_db='hospital_turnos.db'):
        """Inicializa la conexión, crea tablas y verifica datos iniciales."""
        self.nombre_db = nombre_db
        self.conexion = None
        self.cursor = None
        
        # Comprobar si la BD existe
        db_existe = os.path.exists(self.nombre_db)
        
        if self.conectar():
            self.crear_tablas()
            
            # Si la base de datos se acaba de crear (o está vacía), insertar datos
            try:
                # Comprobamos si hay algún médico
                medicos = self.cursor.execute('SELECT 1 FROM medicos').fetchone()
                if not medicos:
                    print("Base de datos vacía detectada. Insertando datos iniciales...")
                    self.insertar_datos_iniciales()
                else:
                    print("La base de datos ya tiene datos.")
            except sqlite3.Error:
                # Si la tabla 'medicos' no existe (error raro), igual intentamos insertar
                print("Error comprobando medicos. Insertando datos iniciales...")
                self.insertar_datos_iniciales()

    def conectar(self):
        """Conecta a la base de datos SQLite."""
        try:
            self.conexion = sqlite3.connect(self.nombre_db)
            # Esta línea es CLAVE para que los datos vengan como diccionarios
            self.conexion.row_factory = sqlite3.Row 
            self.cursor = self.conexion.cursor()
            return True
        except sqlite3.Error as e:
            print(f"✗ Error al conectar: {e}")
            return False
        
    def crear_tablas(self):
        """Crea todas las tablas de la base de datos si no existen."""
        if not self.conexion: return False
        try:
            # Tabla Usuarios (NUEVA)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(50) NOT NULL,
                    apellido VARCHAR(50) NOT NULL,
                    dni VARCHAR(20) UNIQUE NOT NULL,
                    rol VARCHAR(20) DEFAULT 'usuario',
                    id_paciente INTEGER,
                    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente)
                )
            ''')
            
            # Tabla Pacientes
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS pacientes (
                    id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(50) NOT NULL,
                    apellido VARCHAR(50) NOT NULL,
                    dni VARCHAR(20) UNIQUE NOT NULL,
                    fecha_nacimiento DATE NOT NULL,
                    genero VARCHAR(20),
                    telefono VARCHAR(20),
                    domicilio VARCHAR(100)
                )
            ''')
            
            # Tabla Médicos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS medicos (
                    id_medico INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(50) NOT NULL,
                    apellido VARCHAR(50) NOT NULL,
                    especialidad VARCHAR(50) NOT NULL,
                    telefono VARCHAR(20)
                )
            ''')
            
            # Tabla Turnos (SIN consultorio)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS turnos (
                    id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATE NOT NULL,
                    horario TIME NOT NULL,
                    id_paciente INTEGER NOT NULL,
                    id_medico INTEGER NOT NULL,
                    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
                    FOREIGN KEY (id_medico) REFERENCES medicos(id_medico)
                )
            ''')
            
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Error al crear tablas: {e}")
            return False
        
    def insertar_datos_iniciales(self):
        """Inserta los datos iniciales en todas las tablas (VERSIÓN COMPLETA)."""
        try:
            # Insertar Pacientes PRIMERO
            pacientes = [
                ('Marcos', 'Aguero', '35123456', '1990-05-15', 'Masculino', '11-2345-6789', 'Av. Corrientes 1234, CABA'),
                ('Emmanuel', 'Gramajo', '38456789', '1995-08-22', 'Masculino', '11-3456-7890', 'Calle San Martín 567, Buenos Aires'),
                ('Milagros', 'Suarez', '42665700', '1998-11-30', 'Femenino', '11-4567-8901', 'Av. Rivadavia 890, CABA')
            ]
            self.cursor.executemany('''
                INSERT OR IGNORE INTO pacientes (nombre, apellido, dni, fecha_nacimiento, genero, telefono, domicilio)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', pacientes)
            
            # Insertar pacientes
            usuarios = [
                ('Admin', 'Sistema', '12345678', 'admin', None), 
                ('Marcos', 'Aguero', '35123456', 'usuario', 1),   
                ('Emmanuel', 'Gramajo', '38456789', 'usuario', 2), 
                ('Milagros', 'Suarez', '42665700', 'usuario', 3)   
            ]
            self.cursor.executemany('''
                INSERT OR IGNORE INTO usuarios (nombre, apellido, dni, rol, id_paciente)
                VALUES (?, ?, ?, ?, ?)
            ''', usuarios)
            
            # Insertar Médicos
            medicos = [
                ('María', 'González', 'Cardiología', '11-5678-9012'),
                ('Juan', 'Pérez', 'Pediatría', '11-6789-0123'),
                ('Ana', 'Martínez', 'Traumatología', '11-7890-1234'),
                ('Carlos', 'López', 'Clínica Médica', '11-8901-2345')
            ]
            self.cursor.executemany('''
                INSERT OR IGNORE INTO medicos (nombre, apellido, especialidad, telefono)
                VALUES (?, ?, ?, ?)
            ''', medicos)
            
            # Insertar Turnos de ejemplo (SIN consultorio)
            turnos = [
                ('2025-11-20', '09:00:00', 1, 1),
                ('2025-11-20', '10:30:00', 2, 2),
                ('2025-11-21', '14:00:00', 3, 3),
                ('2025-11-22', '11:00:00', 1, 4)
            ]
            self.cursor.executemany('''
                INSERT OR IGNORE INTO turnos (fecha, horario, id_paciente, id_medico)
                VALUES (?, ?, ?, ?)
            ''', turnos)
            
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Error al insertar datos: {e}")
            return False

    # --- MÉTODOS DE AUTENTICACIÓN (NUEVO) ---
    def verificar_usuario(self, dni):
        """Verifica si existe un usuario con el DNI proporcionado."""
        try:
            self.cursor.execute('SELECT * FROM usuarios WHERE dni = ?', (dni,))
            fila = self.cursor.fetchone()
            if fila:
                return dict(fila)
            else:
                return None
        except sqlite3.Error as e:
            print(f"✗ Error al verificar usuario: {e}")
            return None

    # --- MÉTODOS CRUD (USUARIOS) ---
    def consultar_usuarios(self):
        """Consulta todos los usuarios."""
        try:
            self.cursor.execute('SELECT * FROM usuarios ORDER BY apellido')
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"✗ Error al consultar usuarios: {e}")
            return []

    def obtener_usuario_por_id(self, id_usuario):
        """Obtiene un usuario específico por su ID."""
        try:
            self.cursor.execute('SELECT * FROM usuarios WHERE id_usuario = ?', (id_usuario,))
            fila = self.cursor.fetchone()
            if fila:
                return dict(fila)
            else:
                return None
        except sqlite3.Error as e:
            print(f"✗ Error al obtener usuario: {e}")
            return None

    def agregar_usuario(self, nombre, apellido, dni, rol='usuario', id_paciente=None):
        """Agrega un nuevo usuario."""
        try:
            self.cursor.execute('''
                INSERT INTO usuarios (nombre, apellido, dni, rol, id_paciente)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, apellido, dni, rol, id_paciente))
            self.conexion.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"✗ Error al agregar usuario: {e}")
            return None

    def actualizar_usuario(self, id_usuario, nombre, apellido, dni, rol, id_paciente=None):
        """Actualiza un usuario existente."""
        try:
            self.cursor.execute('''
                UPDATE usuarios SET nombre=?, apellido=?, dni=?, rol=?, id_paciente=?
                WHERE id_usuario=?
            ''', (nombre, apellido, dni, rol, id_paciente, id_usuario))
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Error al actualizar usuario: {e}")
            return False

    def eliminar_usuario(self, id_usuario):
        """Elimina un usuario."""
        try:
            self.cursor.execute('DELETE FROM usuarios WHERE id_usuario = ?', (id_usuario,))
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Error al eliminar usuario: {e}")
            return False

    # --- Métodos CRUD (TURNOS) ---
    def agregar_turno(self, fecha, horario, id_paciente, id_medico):
        try:
            self.cursor.execute('''
                INSERT INTO turnos (fecha, horario, id_paciente, id_medico)
                VALUES (?, ?, ?, ?)
            ''', (fecha, horario, id_paciente, id_medico))
            self.conexion.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e: 
            print(f"✗ Error al agregar turno: {e}")
            return None

    def consultar_todos_turnos(self):
        try:
            self.cursor.execute('''
                SELECT 
                    t.id_turno, t.fecha, t.horario,
                    p.nombre || ' ' || p.apellido AS paciente, p.id_paciente,
                    m.nombre || ' ' || m.apellido AS medico, m.id_medico, m.especialidad
                FROM turnos t
                JOIN pacientes p ON t.id_paciente = p.id_paciente
                JOIN medicos m ON t.id_medico = m.id_medico
                ORDER BY t.fecha, t.horario
            ''')
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"✗ Error al consultar turnos: {e}")
            return []

    def consultar_turnos_paciente(self, id_paciente):
        """Consulta los turnos de un paciente específico"""
        try:
            self.cursor.execute('''
                SELECT 
                    t.id_turno, t.fecha, t.horario,
                    p.nombre || ' ' || p.apellido AS paciente, p.id_paciente,
                    m.nombre || ' ' || m.apellido AS medico, m.id_medico, m.especialidad
                FROM turnos t
                JOIN pacientes p ON t.id_paciente = p.id_paciente
                JOIN medicos m ON t.id_medico = m.id_medico
                WHERE t.id_paciente = ?
                ORDER BY t.fecha, t.horario
            ''', (id_paciente,))
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"✗ Error al consultar turnos del paciente: {e}")
            return []

    def obtener_entidades_para_form(self):
        """Obtiene las entidades necesarias para los formularios"""
        try:
            # Obtener pacientes
            self.cursor.execute('SELECT id_paciente, nombre, apellido, nombre || " " || apellido AS nombre_completo FROM pacientes ORDER BY apellido')
            pacientes = [dict(row) for row in self.cursor.fetchall()]
            
            # Obtener médicos
            self.cursor.execute('SELECT id_medico, nombre, apellido, especialidad, nombre || " " || apellido AS nombre_completo FROM medicos ORDER BY apellido')
            medicos = [dict(row) for row in self.cursor.fetchall()]
            
            print(f"DEBUG - Pacientes encontrados: {len(pacientes)}")
            print(f"DEBUG - Médicos encontrados: {len(medicos)}")
            
            return {
                'pacientes': pacientes,
                'medicos': medicos
            }
        except sqlite3.Error as e:
            print(f"✗ Error al obtener entidades: {e}")
            return {'pacientes': [], 'medicos': []}

    def actualizar_turno(self, id_turno, fecha, horario, id_paciente, id_medico):
        try:
            self.cursor.execute('''
                UPDATE turnos SET fecha=?, horario=?, id_paciente=?, id_medico=?
                WHERE id_turno=?
            ''', (fecha, horario, id_paciente, id_medico, id_turno))
            self.conexion.commit()
            return True
        except sqlite3.Error as e: 
            print(f"✗ Error al actualizar turno: {e}")
            return False

    def eliminar_turno(self, id_turno):
        try:
            self.cursor.execute('DELETE FROM turnos WHERE id_turno = ?', (id_turno,))
            self.conexion.commit()
            return True
        except sqlite3.Error as e: print(f"✗ Error al eliminar turno: {e}")

    # --- MÉTODOS CRUD (MÉDICOS) ---
    def consultar_medicos(self):
        try:
            self.cursor.execute('SELECT * FROM medicos ORDER BY apellido')
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"✗ Error al consultar médicos: {e}")
            return []

    def obtener_medico_por_id(self, id_medico):
        try:
            self.cursor.execute('SELECT * FROM medicos WHERE id_medico = ?', (id_medico,))
            fila = self.cursor.fetchone()
            if fila:
                return dict(fila)
            else:
                return None
        except sqlite3.Error as e:
            print(f"✗ Error al obtener médico: {e}")
            return None

    def agregar_medico(self, nombre, apellido, especialidad, telefono):
        try:
            self.cursor.execute('''
                INSERT INTO medicos (nombre, apellido, especialidad, telefono)
                VALUES (?, ?, ?, ?)
            ''', (nombre, apellido, especialidad, telefono))
            self.conexion.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e: print(f"✗ Error al agregar médico: {e}")

    def actualizar_medico(self, id_medico, nombre, apellido, especialidad, telefono):
        try:
            self.cursor.execute('''
                UPDATE medicos SET nombre=?, apellido=?, especialidad=?, telefono=?
                WHERE id_medico=?
            ''', (nombre, apellido, especialidad, telefono, id_medico))
            self.conexion.commit()
            return True
        except sqlite3.Error as e: print(f"✗ Error al actualizar médico: {e}")

    def eliminar_medico(self, id_medico):
        try:
            self.cursor.execute('DELETE FROM medicos WHERE id_medico = ?', (id_medico,))
            self.conexion.commit()
            return True
        except sqlite3.Error as e: print(f"✗ Error al eliminar médico: {e}")

    # --- MÉTODOS CRUD (PACIENTES) ---
    def consultar_pacientes(self):
        try:
            self.cursor.execute('SELECT * FROM pacientes ORDER BY apellido')
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"✗ Error al consultar pacientes: {e}")
            return []

    def obtener_paciente_por_id(self, id_paciente):
        try:
            self.cursor.execute('SELECT * FROM pacientes WHERE id_paciente = ?', (id_paciente,))
            fila = self.cursor.fetchone()
            if fila:
                return dict(fila)
            else:
                return None
        except sqlite3.Error as e:
            print(f"✗ Error al obtener paciente: {e}")
            return None

    def agregar_paciente(self, nombre, apellido, dni, fecha_nac, genero, telefono, domicilio):
        try:
            self.cursor.execute('''
                INSERT INTO pacientes (nombre, apellido, dni, fecha_nacimiento, genero, telefono, domicilio)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, apellido, dni, fecha_nac, genero, telefono, domicilio))
            self.conexion.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"✗ Error al agregar paciente: {e}")
            return None

    def actualizar_paciente(self, id_paciente, nombre, apellido, dni, fecha_nac, genero, telefono, domicilio):
        try:
            self.cursor.execute('''
                UPDATE pacientes 
                SET nombre=?, apellido=?, dni=?, fecha_nacimiento=?, genero=?, telefono=?, domicilio=?
                WHERE id_paciente=?
            ''', (nombre, apellido, dni, fecha_nac, genero, telefono, domicilio, id_paciente))
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Error al actualizar paciente: {e}")
            return False

    def eliminar_paciente(self, id_paciente):
        try:
            # Nota: Si el paciente tiene turnos, esto podría fallar si la FK tiene restricción
            self.cursor.execute('DELETE FROM pacientes WHERE id_paciente = ?', (id_paciente,))
            self.conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Error al eliminar paciente (puede tener turnos asociados): {e}")
            return False

    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        if self.conexion:
            self.conexion.close()