import os
from typing import List

import hashlib

# Parche: reemplazar md5 global sin importar cuándo se importe reportlab
_orig_md5 = hashlib.md5


def md5_fixed(*args, **kwargs):
    # ignorar el argumento incompatible
    kwargs.pop("usedforsecurity", None)
    return _orig_md5(*args, **kwargs)


hashlib.md5 = md5_fixed
# ------------------------------------------------

# main.py
from flask import Flask, request, render_template_string, redirect, url_for, send_file, flash, abort, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import MetaData, event, text
from sqlalchemy.engine import Engine
from io import BytesIO
from datetime import datetime
from functools import wraps

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.lib.pagesizes import A4
import sys
import traceback
from dotenv import load_dotenv

# override=False: en Render/Railway las variables del hosting no las pisa un .env del repo.
load_dotenv(override=False)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def admin_required(fn):

    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.rol != "admin":
            abort(403)
        return fn(*args, **kwargs)

    return wrapper


def operador_required(fn):

    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        # operador y admin pueden entrar
        if current_user.rol not in ("admin", "operador"):
            abort(403)
        return fn(*args, **kwargs)

    return wrapper


app = Flask(__name__)


def _postgres_connect_args(database_url: str) -> dict:
    """Supabase: SSL; solo modo transaccional (:6543) sin prepared statements (PgBouncer/Supavisor)."""
    connect_args: dict = {}
    if "supabase.co" in database_url or "pooler.supabase.com" in database_url:
        connect_args["sslmode"] = "require"
    if ":6543" in database_url:
        connect_args["prepare_threshold"] = None
    # Supavisor/pooler puede dejar search_path vacío → "no schema has been selected to create in"
    du = database_url.strip().lower()
    if du.startswith("postgresql") or du.startswith("postgres://"):
        connect_args["options"] = "-c search_path=public"
    return connect_args


from db_uri import resolve_database_uri

_database_url = resolve_database_uri()
_du_lower = _database_url.strip().lower()
_use_pg_public_schema = _du_lower.startswith(
    "postgresql"
) or _du_lower.startswith("postgres://")
app.config["SQLALCHEMY_DATABASE_URI"] = _database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
_engine_opts = {
    "pool_pre_ping": True,
    "connect_args": _postgres_connect_args(_database_url),
}
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = _engine_opts
app.secret_key = os.environ.get("SECRET_KEY") or "dev-only-cambiar-en-produccion"
if (
    app.secret_key == "dev-only-cambiar-en-produccion"
    and os.environ.get("FLASK_DEBUG", "1") != "1"
):
    raise RuntimeError(
        "Define SECRET_KEY en el entorno cuando FLASK_DEBUG no está activado."
    )

if os.environ.get("FLASK_DEBUG", "1") != "1":
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )


@app.errorhandler(500)
def error_500(e):
    if os.environ.get("FLASK_DEBUG") == "1":
        return f"<pre>{traceback.format_exc()}</pre>", 500
    return "Error interno del servidor.", 500

db = SQLAlchemy(
    app,
    metadata=MetaData(schema="public") if _use_pg_public_schema else None,
)


@event.listens_for(Engine, "connect")
def _pg_set_search_path(dbapi_conn, _connection_record):
    """Pooler Supabase puede dejar search_path vacío; el SQL crudo y DDL lo necesitan."""
    if "psycopg" not in type(dbapi_conn).__module__:
        return
    cur = dbapi_conn.cursor()
    try:
        cur.execute("SET SESSION search_path TO public")
    finally:
        cur.close()


# ======================== SISTEMA DE LOGIN CON CLAVE ========================
login_manager = LoginManager()
login_manager.init_app(app)


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    rol = db.Column(
        db.String(20),
        default="visualizador"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(Usuario, int(user_id))


def crear_usuarios_default():
    admin = Usuario.query.filter_by(username="admin").first()

    if not admin:
        admin = Usuario(
            username="admin",
            rol="admin"
        )
        admin.set_password("1234")

        db.session.add(admin)
        db.session.commit()
        print("✅ Admin creado")
    else:
        print("⚠️ Admin ya existe, no se crea")




# ================================================================


# =========================
# MODELOS (con campos para imagenes en BLOB)
# =========================
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(50), nullable=True)
    vehiculos = relationship("Vehiculo",
                             backref="cliente",
                             cascade="all,delete")


class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patente = db.Column(db.String(20), nullable=False)
    modelo = db.Column(db.String(100), nullable=True)
    cliente_id = db.Column(db.Integer,
                           db.ForeignKey("cliente.id"),
                           nullable=False)
    servicios = relationship("Servicio",
                             backref="vehiculo",
                             cascade="all,delete")
    ots = relationship("OT", backref="vehiculo", cascade="all,delete")
    # columnas para imagen (BLOB)
    foto = db.Column(db.LargeBinary, nullable=True)
    foto_mime = db.Column(db.String(80), nullable=True)


class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer,
                            db.ForeignKey("vehiculo.id"),
                            nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.Text, nullable=False)
    costo = db.Column(db.Float, nullable=True)


class OT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    vehiculo_id = db.Column(db.Integer,
                            db.ForeignKey("vehiculo.id"),
                            nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion_trabajo = db.Column(db.Text, nullable=False)
    observaciones = db.Column(db.Text)
    costo_estimado = db.Column(db.Float, nullable=True)
    estado = db.Column(db.String(30), default="Abierta")
    tipo_ot = db.Column(db.String(20), default="externo")
    # Abierta / En progreso / Cerrada
    # imagen opcional en OT
    foto = db.Column(db.LargeBinary, nullable=True)
    foto_mime = db.Column(db.String(80), nullable=True)
    repuestos_usados = db.relationship("RepuestoUsado",
                                       backref="ot",
                                       cascade="all,delete")


class GastoST(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(500), nullable=False)
    costo = db.Column(db.Float, nullable=True)


class Repuesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    nombre = db.Column(db.String(120), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    precio = db.Column(db.Float, nullable=False, default=0)


class RepuestoUsado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ot_id = db.Column(db.Integer, db.ForeignKey("ot.id"), nullable=False)
    repuesto_id = db.Column(db.Integer,
                            db.ForeignKey("repuesto.id"),
                            nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

    repuesto = db.relationship("Repuesto")


class Cotizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    numero = db.Column(db.String(50), unique=True)

    cliente = db.Column(db.String(200))
    rut = db.Column(db.String(50))
    contacto = db.Column(db.String(100))

    fecha_documento = db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)

    descripcion = db.Column(db.Text)

    cantidad = db.Column(db.Integer)
    valor = db.Column(db.Float)

    neto = db.Column(db.Float)
    iva = db.Column(db.Float)
    total = db.Column(db.Float)


# =========================
# PLANTILLA BASE (Bootstrap + DataTables)
# =========================
base_template = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Taller</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css" rel="stylesheet">
  <style> body { padding-bottom:60px; } .thumb { max-width:160px; max-height:110px; object-fit:cover; border-radius:6px; } </style>
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
  <div class="container-fluid">
    <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">EGAÑA AUTOMOTRIZ</a>

    <!-- Botón hamburguesa (aparece en celular) -->
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain">
      <span class="navbar-toggler-icon"></span>
    </button>

    <!-- Menú colapsable -->
    <div class="collapse navbar-collapse" id="navbarMain">

      <!-- Links a la izquierda -->
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">

       <li class="nav-item">
         <a class="nav-link" href="{{ url_for('index') }}">Inicio</a>
       </li>

       {# =======================
          admin/operador: TODO lo operativo
          ======================= #}
       {% if current_user.is_authenticated and current_user.rol in ["admin", "operador"] %}

         <li class="nav-item"><a class="nav-link" href="{{ url_for('clientes') }}">Clientes</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('vehiculos') }}">Vehículos</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('servicios_list') }}">Servicios</a></li>

         {% set en_inicio = (request.path == '/' or request.path == '/index') %}
         {% if not en_inicio %}
           <li class="nav-item"><a class="nav-link" href="{{ url_for('ots_list') }}">OTs</a></li>
         {% endif %}

         <li class="nav-item"><a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('ganancias') }}">Ganancias</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('ganancias_ots') }}">Ganancias OTs</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('gastos_list') }}">Gastos ST</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('inventario') }}">Inventario</a></li>

       {% endif %}

       {# =======================
          visualizador: SOLO clientes/vehículos/servicios
          ======================= #}
       {% if current_user.is_authenticated and current_user.rol == "visualizador" %}

         <li class="nav-item"><a class="nav-link" href="{{ url_for('clientes') }}">Clientes</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('vehiculos') }}">Vehículos</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('servicios_list') }}">Servicios</a></li>
        

       {% endif %}

       {# =======================
          lector/admin/operador: tareas + horas
          ======================= #}
       {% if current_user.is_authenticated and current_user.rol in ["admin", "operador", "lector"] %}
         <li class="nav-item"><a class="nav-link" href="{{ url_for('horas_list') }}">Toma de horas</a></li>
         <li class="nav-item"><a class="nav-link" href="{{ url_for('tareas_list') }}">Tareas</a></li>
       {% endif %}

       {# =======================
          SOLO admin: usuarios
          ======================= #}
       {% if current_user.is_authenticated and current_user.rol == "admin" %}
         <li class="nav-item">
           <a class="nav-link text-warning" href="/usuarios">Usuarios</a>
         </li>
         <li class="nav-item">
           <a class="nav-link" href="/cotizaciones">Cotizaciones</a>
         </li>
       {% endif %}







       

      </ul>

      <!-- Usuario + salir a la derecha -->
      {% if current_user.is_authenticated %}
      <div class="d-flex flex-column flex-lg-row gap-2 align-items-lg-center">
        <span class="text-white small">
          Usuario: <b>{{ current_user.username }}</b> ({{ current_user.rol }})
        </span>
        <a href="{{ url_for('logout') }}" class="btn btn-outline-danger btn-sm">Salir</a>
      </div>
      {% endif %}
    </div>
  </div>
</nav>


<div class="{{ container_class }}">


  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for cat, msg in messages %}
        <div class="alert alert-{{ 'danger' if cat=='error' else cat }} alert-dismissible fade show" role="alert">
          {{ msg }} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      {% endfor %}
    {% endif %}
  {% endwith %}
  {{ content|safe }}
</div>





<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script>
$(document).ready(function(){
  $('.datatable').DataTable({"language": {"url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"}, "pageLength": 10});
});
</script>
</body>
</html>
"""


def render(content, **ctx):
    is_admin = current_user.is_authenticated and current_user.rol == "admin"

    # si me pasan home=True entonces pantalla completa
    is_home = ctx.pop("home", False)
    container_class = "container-fluid px-0 py-0" if is_home else "container py-4"

    return render_template_string(
        base_template,
        content=content,
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        is_admin=is_admin,
        container_class=container_class,  # 👈 nueva variable para el template
        **ctx)


def has_column(table: str, column: str) -> bool:
    """SQLite: PRAGMA; PostgreSQL: information_schema."""
    dialect = db.engine.dialect.name
    with db.engine.connect() as con:
        if dialect == "sqlite":
            res = con.execute(text(f"PRAGMA table_info('{table}')")).fetchall()
            cols = [r[1] for r in res]
            return column in cols
        q = text(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = :t AND column_name = :c
            """
        )
        return con.execute(q, {"t": table, "c": column}).first() is not None


def _blob_sql_type():
    return "BLOB" if db.engine.dialect.name == "sqlite" else "BYTEA"


def ensure_columns():
    # VEHICULO: foto / foto_mime
    blob_t = _blob_sql_type()
    if not has_column("vehiculo", "foto"):
        with db.engine.connect() as con:
            try:
                con.execute(text(f"ALTER TABLE vehiculo ADD COLUMN foto {blob_t}"))
                con.commit()
                print("✔ Columna agregada: vehiculo.foto")
            except Exception as e:
                print("⚠ Error vehiculo.foto:", e)

    if not has_column("vehiculo", "foto_mime"):
        with db.engine.connect() as con:
            try:
                con.execute(
                    text("ALTER TABLE vehiculo ADD COLUMN foto_mime VARCHAR(80)")
                )
                con.commit()
                print("✔ Columna agregada: vehiculo.foto_mime")
            except Exception as e:
                print("⚠ Error vehiculo.foto_mime:", e)

    # OT: foto / foto_mime / tipo_ot
    if not has_column("ot", "foto"):
        with db.engine.connect() as con:
            try:
                con.execute(text(f"ALTER TABLE ot ADD COLUMN foto {blob_t}"))
                con.commit()
                print("✔ Columna agregada: ot.foto")
            except Exception as e:
                print("⚠ Error ot.foto:", e)

    if not has_column("ot", "foto_mime"):
        with db.engine.connect() as con:
            try:
                con.execute(text("ALTER TABLE ot ADD COLUMN foto_mime VARCHAR(80)"))
                con.commit()
                print("✔ Columna agregada: ot.foto_mime")
            except Exception as e:
                print("⚠ Error ot.foto_mime:", e)

    if not has_column("ot", "tipo_ot"):
        with db.engine.connect() as con:
            try:
                con.execute(
                    text(
                        "ALTER TABLE ot ADD COLUMN tipo_ot VARCHAR(20) DEFAULT 'externo'"
                    )
                )
                con.commit()
                print("✔ Columna agregada: ot.tipo_ot")
            except Exception as e:
                print("⚠ Error ot.tipo_ot:", e)

    # REPUESTO (solo SQLite): migración legada con columna descripcion
    if db.engine.dialect.name == "sqlite":
        with db.engine.connect() as con:
            try:
                res = con.execute(text("PRAGMA table_info('repuesto')")).fetchall()
                cols = [r[1] for r in res]
                if "descripcion" in cols:
                    print(
                        "❗ Tabla repuesto tiene restos de 'descripcion'. Recreando tabla..."
                    )
                    con.execute(text("PRAGMA foreign_keys=off;"))
                    con.execute(text("DROP TABLE IF EXISTS repuesto;"))
                    con.execute(
                        text("""
                        CREATE TABLE repuesto (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            codigo VARCHAR,
                            nombre VARCHAR NOT NULL,
                            stock INTEGER NOT NULL DEFAULT 0,
                            precio FLOAT NOT NULL DEFAULT 0
                        );
                    """)
                    )
                    con.execute(text("PRAGMA foreign_keys=on;"))
                    con.commit()
                    print("✔ Tabla repuesto recreada correctamente.")
            except Exception as e:
                print("⚠ Error revisando/recreando repuesto:", e)

    # REPUESTO: columnas faltantes
    if not has_column("repuesto", "codigo"):
        with db.engine.connect() as con:
            try:
                con.execute(text("ALTER TABLE repuesto ADD COLUMN codigo VARCHAR(50)"))
                con.commit()
                print("✔ repuesto.codigo agregado")
            except Exception as e:
                print("⚠ Error repuesto.codigo:", e)

    if not has_column("repuesto", "nombre"):
        with db.engine.connect() as con:
            try:
                con.execute(text("ALTER TABLE repuesto ADD COLUMN nombre VARCHAR(120)"))
                con.commit()
                print("✔ repuesto.nombre agregado")
            except Exception as e:
                print("⚠ Error repuesto.nombre:", e)

    if not has_column("repuesto", "stock"):
        with db.engine.connect() as con:
            try:
                con.execute(
                    text("ALTER TABLE repuesto ADD COLUMN stock INTEGER DEFAULT 0")
                )
                con.commit()
                print("✔ repuesto.stock agregado")
            except Exception as e:
                print("⚠ Error repuesto.stock:", e)

    if not has_column("repuesto", "precio"):
        with db.engine.connect() as con:
            try:
                con.execute(
                    text("ALTER TABLE repuesto ADD COLUMN precio FLOAT DEFAULT 0")
                )
                con.commit()
                print("✔ repuesto.precio agregado")
            except Exception as e:
                print("⚠ Error repuesto.precio:", e)


# =========================
# RUTAS PRINCIPALES
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        user = Usuario.query.filter_by(
            username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos", "danger")
    content = """
    <div class="row justify-content-center mt-5">
      <div class="col-md-4">
        <div class="card shadow p-4">
          <h3 class="text-center mb-4">Iniciar Sesión</h3>
          <form method="POST">
            <input name="username" class="form-control mb-3" placeholder="Usuario" required autofocus>
            <input name="password" type="password" class="form-control mb-3" placeholder="Contraseña" required>
            <button class="btn btn-primary w-100">Entrar</button>
          </form>
          <hr>
          <small>
        
          </small>
        </div>
      </div>
    </div>
    """
    return render(content)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Obliga login en todas las páginas


@app.route("/healthz")
def healthz():
    return "ok", 200


@app.before_request
def proteger_rutas():
    # permitir sin login: login, static, healthz
    if request.endpoint not in ["login", "static", "healthz"
                                ] and not current_user.is_authenticated:
        return redirect(url_for("login"))

    # si es lector: SOLO permitir tareas y horas + logout + index
    if current_user.is_authenticated and getattr(current_user, "rol",
                                                 None) == "lector":
        permitidos = {
            "index",
            "logout",
            "healthz",
            "tareas_list",
            "tareas_new",
            "tareas_edit",
            "tareas_delete",
            "horas_list",
            "horas_new",
            "horas_edit",
            "horas_delete",
        }
        if request.endpoint not in permitidos:
            abort(403)


@app.route("/")
@login_required
def index():
    content = """<style>
      body {
        background: #000 !important;
      }
      .home-hero {
        position: fixed;
        top: 56px; /* altura navbar */
        left: 0;
        width: 100vw;
        height: calc(100vh - 56px);
        z-index: -1;
      }
      .home-hero img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      .home-overlay {
        position: absolute;
        top: 12%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.65);
        padding: 30px 60px;
        border-radius: 12px;
        color: white;
        text-align: center;
      }
    </style>

    <div class="home-hero">
      <img src="https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=2400&q=80">
      <div class="home-overlay">
        <h1 class="fw-bold">EGAÑA AUTOMOTRIZ</h1>
        <p class="fs-4 mb-0">Sistema de gestión del taller</p>
      </div>
    </div>
    """
    return render(content)


from flask_login import current_user


@app.route("/inventario")
@login_required
def inventario():
    lista = Repuesto.query.order_by(Repuesto.nombre).all()

    is_admin = current_user.is_authenticated and current_user.rol == "admin"

    btn_add = ""
    if is_admin:
        btn_add = "<a class='btn btn-success mb-3' href='/inventario/new'>Agregar</a>"

    content = f"""
    <h3>Inventario (Herramientas / Items)</h3>
    {btn_add}

    <table class='table table-striped datatable'>
        <thead class='table-dark'>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Stock</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
    """

    for r in lista:
        btn_edit = ""
        if is_admin:
            btn_edit = f"<a class='btn btn-sm btn-warning' href='/inventario/{r.id}/edit'>Editar</a>"

        content += f"""
        <tr>
          <td>{r.id}</td>
          <td>{r.nombre}</td>
          <td>{r.stock}</td>
          <td>{btn_edit}</td>
        </tr>
        """

    content += "</tbody></table>"
    return render(content)


# inventario
@app.route("/inventario/new", methods=["GET", "POST"])
@login_required
@admin_required
def inventario_new():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        stock_raw = request.form.get("stock", "").strip()

        if not nombre:
            flash("Nombre es obligatorio.", "danger")
            return redirect("/inventario/new")

        try:
            stock = int(float(stock_raw.replace(",", "."))) if stock_raw else 0
        except ValueError:
            flash("Stock inválido.", "danger")
            return redirect("/inventario/new")

        # generar código único simple
        codigo = f"ITEM-{int(datetime.utcnow().timestamp())}"

        r = Repuesto()
        r.nombre = nombre
        r.stock = stock

        db.session.add(r)
        db.session.commit()

        flash("Guardado correctamente.", "success")
        return redirect("/inventario")

    content = """
    <h3>Agregar al inventario</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Nombre</label>
        <input name="nombre" class="form-control" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Stock</label>
        <input name="stock" class="form-control" placeholder="Ej: 10" value="0">
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-success">Guardar</button>
        <a class="btn btn-secondary" href="/inventario">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/inventario/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def inventario_edit(item_id):
    r = Repuesto.query.get_or_404(item_id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        stock_raw = request.form.get("stock", "").strip()

        if not nombre:
            flash("Nombre es obligatorio.", "danger")
            return redirect(f"/inventario/{r.id}/edit")

        try:
            stock = int(float(stock_raw.replace(",", "."))) if stock_raw else 0
        except:
            flash("Stock inválido.", "danger")
            return redirect(f"/inventario/{r.id}/edit")

        # Si usas codigo=nombre, debe mantenerse único:
        # ✅ opción segura: no cambiar codigo si ya existe
        r.nombre = nombre
        r.stock = stock
        # r.codigo se mantiene como está, para evitar choques

        db.session.commit()
        flash("Actualizado correctamente.", "success")
        return redirect("/inventario")

    content = f"""
    <h3>Editar item #{r.id}</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Nombre</label>
        <input name="nombre" class="form-control" value="{r.nombre}" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Stock</label>
        <input name="stock" class="form-control" value="{r.stock}" required>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-primary">Guardar cambios</button>
        <a class="btn btn-secondary" href="/inventario">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


# =========================
# cotizaciones
# =========================
@app.route("/cotizaciones")
@login_required
def cotizaciones_list():
    lista = Cotizacion.query.order_by(Cotizacion.id.desc()).all()

    content = """
    <h3>Cotizaciones</h3>
    <a class="btn btn-success mb-3" href="/cotizaciones/new">Nueva cotización</a>

    <table class="table table-striped datatable">
    <thead class="table-dark">
    <tr>
    <th>Nº</th>
    <th>Cliente</th>
    <th>Fecha</th>
    <th>Total</th>
    <th>Acciones</th>
    </tr>
    </thead>
    <tbody>
    """

    for c in lista:
        content += f"""
        <tr>
        <td>{c.numero}</td>
        <td>{c.cliente}</td>
        <td>{c.fecha_documento}</td>
        <td>{int(c.total or 0)}</td>
        <td>
          <a class="btn btn-sm btn-warning me-1" href="/cotizaciones/{c.id}/edit">Editar</a>
          <a class="btn btn-sm btn-primary me-1" href="/cotizaciones/{c.id}/pdf">PDF</a>
          <a class="btn btn-sm btn-danger" href="/cotizaciones/{c.id}/delete"
             onclick="return confirm('¿Eliminar cotización?')">Eliminar</a>
        </td>
        </tr>
        """

    content += "</tbody></table>"

    return render(content)


@app.route("/cotizaciones/new", methods=["GET", "POST"])
@login_required
def cotizacion_new():
    if request.method == "POST":
        cliente = request.form.get("cliente", "").strip()
        rut = request.form.get("rut", "").strip()
        contacto = request.form.get("contacto", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        cantidad_raw = request.form.get("cantidad", "").strip()
        valor_raw = request.form.get("valor", "").strip()
        fecha_doc_raw = request.form.get("fecha_documento", "").strip()
        fecha_venc_raw = request.form.get("fecha_vencimiento", "").strip()

        if not cliente or not descripcion:
            flash("Cliente y descripción son obligatorios.", "danger")
            return redirect("/cotizaciones/new")

        try:
            cantidad = int(float(cantidad_raw.replace(
                ",", "."))) if cantidad_raw else 1
        except:
            flash("Cantidad inválida.", "danger")
            return redirect("/cotizaciones/new")

        try:
            valor = float(valor_raw.replace(".", "").replace(
                ",", ".")) if valor_raw else 0
        except:
            flash("Valor inválido.", "danger")
            return redirect("/cotizaciones/new")

        try:
            fecha_documento = datetime.strptime(
                fecha_doc_raw, "%Y-%m-%d").date(
                ) if fecha_doc_raw else datetime.utcnow().date()
        except:
            flash("Fecha documento inválida.", "danger")
            return redirect("/cotizaciones/new")

        try:
            fecha_vencimiento = datetime.strptime(
                fecha_venc_raw, "%Y-%m-%d").date(
                ) if fecha_venc_raw else datetime.utcnow().date()
        except:
            flash("Fecha vencimiento inválida.", "danger")
            return redirect("/cotizaciones/new")

        neto = cantidad * valor
        iva = neto * 0.19
        total = neto + iva

        # NUMERACIÓN CORRELATIVA SOLO CON NÚMEROS SIMPLES
        todas = Cotizacion.query.all()
        ultimo_numero = 0

        for cot in todas:
            valor_num = str(cot.numero).strip()
            if valor_num.isdigit():
                n = int(valor_num)
                if n > ultimo_numero:
                    ultimo_numero = n

        numero = str(ultimo_numero + 1)

        c = Cotizacion()

        c.numero = numero
        c.cliente = cliente
        c.rut = rut
        c.contacto = contacto
        c.descripcion = descripcion
        c.cantidad = cantidad
        c.valor = valor
        c.neto = neto
        c.iva = iva
        c.total = total
        c.fecha_documento = fecha_documento
        c.fecha_vencimiento = fecha_vencimiento

        db.session.add(c)
        db.session.commit()
        flash("Cotización creada.", "success")
        return redirect("/cotizaciones")

    hoy = datetime.utcnow().strftime("%Y-%m-%d")

    content = f"""
    <h3>Nueva Cotización</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Cliente</label>
        <input name="cliente" class="form-control" required>
      </div>

      <div class="row g-2">
        <div class="col-md-4 mb-3">
          <label class="form-label">RUT</label>
          <input name="rut" class="form-control">
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Contacto</label>
          <input name="contacto" class="form-control">
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Cantidad</label>
          <input name="cantidad" class="form-control" value="1" required>
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">Descripción</label>
        <textarea name="descripcion" class="form-control" rows="4" required></textarea>
      </div>

      <div class="row g-2">
        <div class="col-md-4 mb-3">
          <label class="form-label">Valor unitario</label>
          <input name="valor" class="form-control" required>
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Fecha documento</label>
          <input type="date" name="fecha_documento" class="form-control" value="{hoy}">
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Fecha vencimiento</label>
          <input type="date" name="fecha_vencimiento" class="form-control" value="{hoy}">
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-success">Guardar</button>
        <a class="btn btn-secondary" href="/cotizaciones">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/cotizaciones/<int:id>/edit", methods=["GET", "POST"])
@login_required
def cotizacion_edit(id):
    c = Cotizacion.query.get_or_404(id)

    if request.method == "POST":
        cliente = request.form.get("cliente", "").strip()
        rut = request.form.get("rut", "").strip()
        contacto = request.form.get("contacto", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        cantidad_raw = request.form.get("cantidad", "").strip()
        valor_raw = request.form.get("valor", "").strip()
        fecha_doc_raw = request.form.get("fecha_documento", "").strip()
        fecha_venc_raw = request.form.get("fecha_vencimiento", "").strip()

        if not cliente or not descripcion:
            flash("Cliente y descripción son obligatorios.", "danger")
            return redirect(f"/cotizaciones/{c.id}/edit")

        try:
            cantidad = int(float(cantidad_raw.replace(
                ",", "."))) if cantidad_raw else 1
        except:
            flash("Cantidad inválida.", "danger")
            return redirect(f"/cotizaciones/{c.id}/edit")

        try:
            valor = float(valor_raw.replace(".", "").replace(
                ",", ".")) if valor_raw else 0
        except:
            flash("Valor inválido.", "danger")
            return redirect(f"/cotizaciones/{c.id}/edit")

        try:
            fecha_documento = datetime.strptime(
                fecha_doc_raw, "%Y-%m-%d").date(
                ) if fecha_doc_raw else datetime.utcnow().date()
        except:
            flash("Fecha documento inválida.", "danger")
            return redirect(f"/cotizaciones/{c.id}/edit")

        try:
            fecha_vencimiento = datetime.strptime(
                fecha_venc_raw, "%Y-%m-%d").date(
                ) if fecha_venc_raw else datetime.utcnow().date()
        except:
            flash("Fecha vencimiento inválida.", "danger")
            return redirect(f"/cotizaciones/{c.id}/edit")

        neto = cantidad * valor
        iva = neto * 0.19
        total = neto + iva

        c.cliente = cliente
        c.rut = rut
        c.contacto = contacto
        c.descripcion = descripcion
        c.cantidad = cantidad
        c.valor = valor
        c.neto = neto
        c.iva = iva
        c.total = total
        c.fecha_documento = fecha_documento
        c.fecha_vencimiento = fecha_vencimiento

        db.session.commit()
        flash("Cotización actualizada.", "success")
        return redirect("/cotizaciones")

    fecha_doc = c.fecha_documento.strftime(
        "%Y-%m-%d") if c.fecha_documento else ""
    fecha_venc = c.fecha_vencimiento.strftime(
        "%Y-%m-%d") if c.fecha_vencimiento else ""

    content = f"""
    <h3>Editar Cotización Nº {c.numero}</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Cliente</label>
        <input name="cliente" class="form-control" value="{c.cliente or ''}" required>
      </div>

      <div class="row g-2">
        <div class="col-md-4 mb-3">
          <label class="form-label">RUT</label>
          <input name="rut" class="form-control" value="{c.rut or ''}">
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Contacto</label>
          <input name="contacto" class="form-control" value="{c.contacto or ''}">
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Cantidad</label>
          <input name="cantidad" class="form-control" value="{c.cantidad or 1}" required>
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">Descripción</label>
        <textarea name="descripcion" class="form-control" rows="4" required>{c.descripcion or ''}</textarea>
      </div>

      <div class="row g-2">
        <div class="col-md-4 mb-3">
          <label class="form-label">Valor unitario</label>
          <input name="valor" class="form-control" value="{int(c.valor) if c.valor is not None else 0}" required>
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Fecha documento</label>
          <input type="date" name="fecha_documento" class="form-control" value="{fecha_doc}">
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Fecha vencimiento</label>
          <input type="date" name="fecha_vencimiento" class="form-control" value="{fecha_venc}">
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-primary">Guardar cambios</button>
        <a class="btn btn-secondary" href="/cotizaciones">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/cotizaciones/<int:id>/delete")
@login_required
def cotizacion_delete(id):
    c = Cotizacion.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash("Cotización eliminada.", "success")
    return redirect("/cotizaciones")


@app.route("/cotizaciones/reset_numeracion")
@login_required
@admin_required
def reset_numeracion_cotizaciones():
    lista = Cotizacion.query.order_by(Cotizacion.id.asc()).all()

    contador = 1
    for c in lista:
        c.numero = str(contador)
        contador += 1

    db.session.commit()
    return "Numeración de cotizaciones reiniciada correctamente"


@app.route("/cotizaciones/<int:id>/pdf")
@login_required
def cotizacion_pdf(id):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
    from io import BytesIO
    import urllib.request

    c = Cotizacion.query.get_or_404(id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=A4,
                            rightMargin=35,
                            leftMargin=35,
                            topMargin=30,
                            bottomMargin=30)

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(name="Titulo",
                                 parent=styles["Heading1"],
                                 fontName="Helvetica-Bold",
                                 fontSize=16,
                                 leading=20,
                                 alignment=TA_RIGHT,
                                 textColor=colors.black)

    style_sub = ParagraphStyle(name="Sub",
                               parent=styles["Normal"],
                               fontName="Helvetica",
                               fontSize=9,
                               leading=12,
                               alignment=TA_LEFT,
                               textColor=colors.black)

    style_label = ParagraphStyle(name="Label",
                                 parent=styles["Normal"],
                                 fontName="Helvetica-Bold",
                                 fontSize=9,
                                 leading=12,
                                 textColor=colors.black)

    style_normal = ParagraphStyle(name="NormalCustom",
                                  parent=styles["Normal"],
                                  fontName="Helvetica",
                                  fontSize=9,
                                  leading=12,
                                  textColor=colors.black)

    style_total = ParagraphStyle(name="Total",
                                 parent=styles["Normal"],
                                 fontName="Helvetica-Bold",
                                 fontSize=10,
                                 leading=13,
                                 alignment=TA_RIGHT,
                                 textColor=colors.black)

    story = []

    # =========================
    # LOGO + ENCABEZADO
    # =========================
    logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoO9kvULPTw3uLlRBM0c8LI3EXronn_x6sDQ&s"
    logo_buffer = BytesIO()
    try:
        logo_buffer.write(urllib.request.urlopen(logo_url).read())
        logo_buffer.seek(0)
        logo = Image(logo_buffer, width=85, height=85)
    except:
        logo = Paragraph("EGAÑA AUTOMOTRIZ", style_label)

    encabezado_izq = [
        logo,
        Spacer(1, 4),
        Paragraph("Egaña Automotriz", style_label),
        Paragraph("Giro: Compra y venta de vehículos nuevos o usados",
                  style_sub),
        Paragraph("RUT: 77.728.698-6", style_sub),
        Paragraph("Dirección: Egaña 931", style_sub),
        Paragraph("Comuna: Puerto Montt", style_sub),
        Paragraph("Correo: ADMINISTRACION@EGANA.CL", style_sub),
        Paragraph("Teléfono: 9 7603 4758", style_sub),
    ]

    encabezado_der = [
        Paragraph(f"COTIZACIÓN Nº {c.numero}", style_title),
        Spacer(1, 8),
        Paragraph(
            f"<b>Fecha documento:</b> {c.fecha_documento.strftime('%d-%m-%Y') if c.fecha_documento else '—'}",
            style_normal),
        Paragraph(
            f"<b>Fecha vencimiento:</b> {c.fecha_vencimiento.strftime('%d-%m-%Y') if c.fecha_vencimiento else '—'}",
            style_normal),
    ]

    t_header = Table([[encabezado_izq, encabezado_der]], colWidths=[300, 210])
    t_header.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

    story.append(t_header)
    story.append(Spacer(1, 12))

    # =========================
    # DATOS CLIENTE
    # =========================
    datos_cliente = [
        [
            Paragraph("<b>SEÑOR:</b>", style_label),
            Paragraph(c.cliente or "—", style_normal)
        ],
        [
            Paragraph("<b>RUT:</b>", style_label),
            Paragraph(c.rut or "—", style_normal)
        ],
        [
            Paragraph("<b>CONTACTO:</b>", style_label),
            Paragraph(c.contacto or "—", style_normal)
        ],
    ]

    t_cliente = Table(datos_cliente, colWidths=[90, 420])
    t_cliente.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F0F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

    story.append(t_cliente)
    story.append(Spacer(1, 12))

    # =========================
    # TABLA DETALLE
    # =========================
    cantidad_txt = str(int(c.cantidad)) if c.cantidad is not None else "0"
    valor_txt = f"{int(float(c.valor)):,}".replace(
        ",", ".") if c.valor is not None else "0"
    neto_txt = f"{int(float(c.neto)):,}".replace(
        ",", ".") if c.neto is not None else "0"
    iva_txt = f"{int(float(c.iva)):,}".replace(
        ",", ".") if c.iva is not None else "0"
    total_txt = f"{int(float(c.total)):,}".replace(
        ",", ".") if c.total is not None else "0"

    detalle_data = [[
        Paragraph("<b>DESCRIPCIÓN</b>", style_normal),
        Paragraph("<b>Cant.</b>", style_normal),
        Paragraph("<b>Valor</b>", style_normal),
    ],
                    [
                        Paragraph((c.descripcion
                                   or "—").replace("\n", "<br/>"),
                                  style_normal),
                        Paragraph(cantidad_txt, style_normal),
                        Paragraph(valor_txt, style_normal),
                    ]]

    t_detalle = Table(detalle_data, colWidths=[360, 60, 90])
    t_detalle.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.black),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

    story.append(t_detalle)
    story.append(Spacer(1, 14))

    # =========================
    # TOTALES
    # =========================
    totales = [
        ["NETO:", neto_txt],
        ["IVA 19%:", iva_txt],
        ["TOTAL:", total_txt],
    ]

    t_totales = Table(totales, colWidths=[120, 120], hAlign="RIGHT")
    t_totales.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F0F0")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

    story.append(t_totales)
    story.append(Spacer(1, 18))

    # =========================
    # DATOS TRANSFERENCIA
    # =========================
    story.append(Paragraph("<b>Datos de transferencia</b>", style_label))
    story.append(Spacer(1, 6))

    transferencia = [
        [Paragraph("COMERCIAL REY AGUIRRE SPA", style_normal)],
        [Paragraph("77728698-6", style_normal)],
        [Paragraph("Banco ITAU", style_normal)],
        [Paragraph("Cuenta Corriente", style_normal)],
        [Paragraph("230972615", style_normal)],
        [Paragraph("ADMINISTRACION@EGANA.CL", style_normal)],
    ]

    t_transfer = Table(transferencia, colWidths=[250])
    t_transfer.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

    story.append(t_transfer)
    story.append(Spacer(1, 18))

    # =========================
    # OBSERVACIÓN FINAL
    # =========================
    story.append(
        Paragraph(
            "Esta cotización está sujeta a confirmación de stock, disponibilidad y vigencia hasta la fecha indicada.",
            style_sub))

    doc.build(story)
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name=f"cotizacion_{c.numero}.pdf",
                     mimetype="application/pdf")


# =========================
# Usuarios
# =========================
@app.route("/usuarios")
@admin_required
def usuarios_list():
    lista = Usuario.query.order_by(Usuario.id.asc()).all()

    content = """
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Usuarios</h3>
      <a class="btn btn-success" href="/usuarios/new">Nuevo usuario</a>
    </div>

    <table class="table table-striped">
      <thead class="table-dark">
        <tr><th>ID</th><th>Usuario</th><th>Rol</th><th>Acciones</th></tr>
      </thead>
      <tbody>
    """

    for u in lista:
        content += f"""
        <tr>
          <td>{u.id}</td>
          <td>{u.username}</td>
          <td>{u.rol}</td>
          <td>
            <a class="btn btn-sm btn-warning" href="/usuarios/{u.id}/edit">Editar</a>
          </td>
        </tr>
        """

    content += "</tbody></table>"
    return render(content)


@app.route("/usuarios/new", methods=["GET", "POST"])
@admin_required
def usuario_new():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        rol = request.form.get("rol", "visualizador").strip()

        if not username or not password:
            flash("Usuario y contraseña son obligatorios.", "danger")
            return redirect("/usuarios/new")

        if Usuario.query.filter_by(username=username).first():
            flash("Ese usuario ya existe.", "danger")
            return redirect("/usuarios/new")

        u = Usuario()
        u.username = username
        u.rol = rol

        u.set_password(password)

        db.session.add(u)
        db.session.commit()

        flash("Usuario creado.", "success")
        return redirect("/usuarios")

    content = """
    <h3>Nuevo Usuario</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Usuario</label>
        <input name="username" class="form-control" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Contraseña</label>
        <input name="password" type="password" class="form-control" required>
      </div>

     <div class="mb-3">
       <label class="form-label">Rol</label>
       <select name="rol" class="form-select">
         <option value="admin">admin</option>
         <option value="operador">operador</option>
         <option value="lector">lector</option>
         <option value="visualizador" selected>visualizador</option>
       </select>

     </div>


      <div class="d-flex gap-2">
        <button class="btn btn-success">Crear</button>
        <a class="btn btn-secondary" href="/usuarios">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/usuarios/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def usuario_edit(user_id):
    u = Usuario.query.get_or_404(user_id)

    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        new_rol = request.form.get("rol", "visualizador").strip()
        new_pass = request.form.get("password", "").strip()

        # validar username
        if not new_username:
            flash("Usuario no puede quedar vacío.", "danger")
            return redirect(f"/usuarios/{u.id}/edit")

        # si cambia el username, que no exista ya
        if new_username != u.username and Usuario.query.filter_by(
                username=new_username).first():
            flash("Ese nombre de usuario ya está en uso.", "danger")
            return redirect(f"/usuarios/{u.id}/edit")

        u.username = new_username
        u.rol = new_rol

        if new_pass:
            u.set_password(new_pass)

        db.session.commit()
        flash("Usuario actualizado.", "success")
        return redirect("/usuarios")

    sel_admin = "selected" if u.rol == "admin" else ""
    sel_op = "selected" if u.rol == "operador" else ""
    sel_lector = "selected" if u.rol == "lector" else ""
    sel_vis = "selected" if u.rol == "visualizador" else ""

    content = f"""
    <h3>Editar Usuario (ID {u.id})</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Usuario</label>
        <input name="username" class="form-control" value="{u.username}" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Rol</label>
        <select name="rol" class="form-select">
          <option value="admin" {sel_admin}>admin</option>
          <option value="visualizador" {sel_vis}>visualizador</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Nueva contraseña (dejar vacío para NO cambiar)</label>
        <input name="password" type="password" class="form-control">
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-primary">Guardar</button>
        <a class="btn btn-secondary" href="/usuarios">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


# =========================
# DASHBOARD
# =========================
@app.route("/HISTORIAL")
@login_required
def dashboard():
    ultimos = OT.query.order_by(OT.fecha_creacion.desc()).limit(5).all()
    content = "<h3>Dashboard</h3><div class='card p-3 mb-3'><h5>Últimas OTs</h5><ul>"
    for ot in ultimos:
        content += f"<li>OT {ot.numero} — {ot.vehiculo.patente} — {ot.estado} — {ot.fecha_creacion.strftime('%Y-%m-%d')}</li>"
    content += "</ul></div>"
    return render(content)


# =========================
# gana
# =========================


@app.route("/ganancias")
def ganancias():
    from sqlalchemy import func, extract

    # Suma total de todos los costos
    total_general = db.session.query(func.sum(Servicio.costo)).scalar() or 0

    # Suma por mes
    totales_mensuales = (db.session.query(
        extract("year", Servicio.fecha).label("anio"),
        extract("month", Servicio.fecha).label("mes"),
        func.sum(Servicio.costo).label("total")).group_by(
            "anio", "mes").order_by("anio", "mes").all())

    content = f"""
    <h3>Ganancias CARWASH</h3>

    <div class='card p-3 mb-4'>
        <h4>Total general ganado:</h4>
        <h2 class='text-success'>$ {total_general:,.0f}</h2>
    </div>

    <h4>Ganancias por mes</h4>
    <table class="table table-striped datatable">
        <thead class="table-dark">
            <tr>
                <th>Año</th>
                <th>Mes</th>
                <th>Total ganado</th>
                <th>PDF</th>

            </tr>
        </thead>
        <tbody">
    """

    # Rellenar tabla con los totales mensuales
    for anio, mes, total in totales_mensuales:
        total_fmt = f"$ {total:,.0f}"
        content += f"""
        <tr>
          <td>{int(anio)}</td>
          <td>{int(mes)}</td>
          <td>{total_fmt}</td>
          <td>
            <a class="btn btn-sm btn-danger" href="/ganancias/pdf/{int(anio)}/{int(mes)}">PDF</a>
          </td>
        </tr>
        """

    content += """
        </tbody>
    </table>
    """

    return render(content)


@app.route("/ganancias_ots")
def ganancias_ots():
    from sqlalchemy import func, extract

    # Totales generales
    total_general = db.session.query(func.sum(OT.costo_estimado)).scalar() or 0
    total_externo = db.session.query(func.sum(
        OT.costo_estimado)).filter(OT.tipo_ot == "externo").scalar() or 0
    total_propio = db.session.query(func.sum(
        OT.costo_estimado)).filter(OT.tipo_ot == "propio").scalar() or 0
    total_venta = db.session.query(func.sum(
        OT.costo_estimado)).filter(OT.tipo_ot == "venta").scalar() or 0

    # Totales por mes y por tipo
    totales_mensuales = (db.session.query(
        extract("year", OT.fecha_creacion).label("anio"),
        extract("month", OT.fecha_creacion).label("mes"),
        OT.tipo_ot.label("tipo"),
        func.sum(OT.costo_estimado).label("total")).group_by(
            "anio", "mes", "tipo").order_by("anio", "mes", "tipo").all())

    tabla_html = ""
    for anio, mes, tipo, total in totales_mensuales:
        tipo_txt = tipo or "externo"
        if tipo_txt == "externo":
            tipo_mostrar = "Auto externo"
        elif tipo_txt == "propio":
            tipo_mostrar = "Auto propio"
        elif tipo_txt == "venta":
            tipo_mostrar = "Auto por venta"
        else:
            tipo_mostrar = tipo_txt

        total_txt = f"$ {total:,.0f}" if total is not None else "$ 0"

        tabla_html += f"""
        <tr>
            <td>{int(anio)}</td>
            <td>{int(mes)}</td>
            <td>{tipo_mostrar}</td>
            <td>{total_txt}</td>
        </tr>
        """

    content = f"""
    <h3>Ganancias de Órdenes de Trabajo</h3>

    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card p-3">
                <h5>Total general</h5>
                <h3 class="text-success">$ {total_general:,.0f}</h3>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card p-3">
                <h5>Autos externos</h5>
                <h3 class="text-primary">$ {total_externo:,.0f}</h3>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card p-3">
                <h5>Autos propios</h5>
                <h3 class="text-warning">$ {total_propio:,.0f}</h3>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card p-3">
                <h5>Autos por venta</h5>
                <h3 class="text-danger">$ {total_venta:,.0f}</h3>
            </div>
        </div>
    </div>

    <h4>Ganancias mensuales por tipo de OT</h4>
    <table class="table table-striped datatable">
        <thead class="table-dark">
            <tr>
                <th>Año</th>
                <th>Mes</th>
                <th>Tipo OT</th>
                <th>Total ganado</th>
            </tr>
        </thead>
        <tbody>
            {tabla_html}
        </tbody>
    </table>
    """

    return render(content)


@app.route("/ganancias/pdf/<int:anio>/<int:mes>")
def ganancias_pdf(anio, mes):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from io import BytesIO
    import urllib.request
    from sqlalchemy import func, extract

    # 1) Total del mes
    total_mes = (db.session.query(func.sum(Servicio.costo)).filter(
        extract("year", Servicio.fecha) == anio).filter(
            extract("month", Servicio.fecha) == mes).scalar() or 0)

    # 2) Detalle de servicios del mes
    servicios = (Servicio.query.filter(
        extract("year", Servicio.fecha) == anio).filter(
            extract("month", Servicio.fecha) == mes).order_by(
                Servicio.fecha.asc()).all())

    # Nombre del mes para título
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
        "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    mes_nombre = meses[mes - 1] if 1 <= mes <= 12 else str(mes)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=A4,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=40,
                            bottomMargin=40)

    styles = getSampleStyleSheet()
    title = styles["Heading1"]
    title.fontSize = 16
    title.leading = 20

    subtitle = styles["Heading2"]
    subtitle.fontSize = 12
    subtitle.leading = 14

    normal = styles["BodyText"]
    normal.fontSize = 10
    normal.leading = 12

    story = []

    # -------------------------------
    # LOGO (igual que en OT)
    # -------------------------------
    logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoO9kvULPTw3uLlRBM0c8LI3EXronn_x6sDQ&s"
    logo_buffer = BytesIO()
    logo_buffer.write(urllib.request.urlopen(logo_url).read())
    logo_buffer.seek(0)
    logo = Image(logo_buffer, width=100, height=100)
    logo.hAlign = "LEFT"

    story.append(logo)
    story.append(Spacer(1, 10))

    # Línea dorada
    story.append(Paragraph("<font color='#DAA520'><hr/></font>", normal))
    story.append(Spacer(1, 10))

    # -------------------------------
    # TÍTULO
    # -------------------------------
    story.append(
        Paragraph(f"<b>Ganancias CARWASH — {mes_nombre} {anio}</b>", title))
    story.append(Spacer(1, 8))

    # -------------------------------
    # RESUMEN (Total del mes)
    # -------------------------------
    story.append(Paragraph("Resumen del mes", subtitle))
    data_resumen = [
        ["Año", str(anio)],
        ["Mes", f"{mes:02d} — {mes_nombre}"],
        ["Total ganado", f"$ {total_mes:,.0f}"],
        ["Cantidad de servicios", str(len(servicios))],
    ]

    table_res = Table(data_resumen, colWidths=[140, 300])
    table_res.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
    story.append(table_res)
    story.append(Spacer(1, 14))

    # Línea dorada
    story.append(Paragraph("<font color='#DAA520'><hr/></font>", normal))
    story.append(Spacer(1, 12))

    # -------------------------------
    # DETALLE (tabla de servicios)
    # -------------------------------
    story.append(Paragraph("Detalle de servicios del mes", subtitle))
    story.append(Spacer(1, 8))

    # 👇 OJO: aquí asumo que "Servicio" tiene:
    # - fecha (datetime/date)
    # - costo (num)
    # - opcional: descripcion o nombre o tipo
    #
    # Cambia servicio_txt según tu modelo.
    detalle = [["Fecha", "Servicio", "Costo"]]
    for s in servicios:
        fecha_txt = s.fecha.strftime("%Y-%m-%d") if s.fecha else "—"

        # Cambia el campo según tu modelo:
        servicio_txt = getattr(s, "descripcion", None) or getattr(
            s, "nombre", None) or getattr(s, "tipo", None) or "—"

        costo_txt = f"$ {s.costo:,.0f}" if s.costo is not None else "—"
        detalle.append([fecha_txt, str(servicio_txt), costo_txt])

    table_det = Table(detalle, colWidths=[90, 260, 90])
    table_det.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.black),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("ALIGN", (2, 1), (2, -1), "RIGHT"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ]))
    story.append(table_det)
    story.append(Spacer(1, 12))

    # Construir PDF
    doc.build(story)

    buffer.seek(0)
    filename = f"GANANCIAS_{anio}_{mes:02d}.pdf"
    return send_file(buffer,
                     as_attachment=True,
                     download_name=filename,
                     mimetype="application/pdf")


# =========================
# RENDEREO DE IMÁGENES (desde BLOB)
# =========================
@app.route("/image/vehiculo/<int:veh_id>")
@login_required
def vehiculo_image(veh_id):
    v = Vehiculo.query.get_or_404(veh_id)
    if not v.foto:
        abort(404)
    mime = v.foto_mime or "application/octet-stream"
    return Response(v.foto, mimetype=mime)


@app.route("/image/ot/<int:ot_id>")
@login_required
def ot_image(ot_id):
    o = OT.query.get_or_404(ot_id)
    if not o.foto:
        abort(404)
    mime = o.foto_mime or "application/octet-stream"
    return Response(o.foto, mimetype=mime)


# =========================
# CLIENTES (buscar/listar/crear/editar/delete)
# =========================
@app.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        if not nombre:
            flash("Nombre obligatorio.", "danger")
        else:
            c = Cliente()
            c.nombre = nombre
            c.telefono = telefono

            db.session.add(c)
            db.session.commit()

            flash("Cliente creado.", "success")
            return redirect(url_for("clientes"))

    q = request.args.get("q", "").strip()
    if q:
        lista = (db.session.query(Cliente).outerjoin(Vehiculo).filter(
            (Cliente.nombre.ilike(f"%{q}%"))
            | (Cliente.telefono.ilike(f"%{q}%"))
            | (Vehiculo.patente.ilike(f"%{q}%"))
            | (Vehiculo.modelo.ilike(f"%{q}%"))).distinct().all())
    else:
        lista = Cliente.query.order_by(Cliente.nombre).all()

    content = f"""
    <div class="d-flex justify-content-between mb-3">
      <h3>Clientes</h3>
      <a class="btn btn-success" href="{url_for('cliente_new')}">Nuevo cliente</a>
    </div>
    <form method="GET" class="d-flex mb-3">
      <input name="q" class="form-control me-2" placeholder="Buscar por nombre, teléfono, patente o modelo..." value="{q}">
      <button class="btn btn-secondary">Buscar</button>
      <a class="btn btn-outline-secondary ms-2" href="{url_for('clientes')}">Limpiar</a>
    </form>
    <table class="table table-striped datatable"><thead class="table-dark"><tr><th>ID</th><th>Nombre</th><th>Teléfono</th><th>Vehículos</th><th>Acciones</th></tr></thead><tbody>
    """
    for c in lista:
        vehs = "<ul class='mb-0'>" + "".join([
            f"<li><a href='{url_for('vehiculo_detail', vehiculo_id=v.id)}'>{v.patente} — {v.modelo}</a></li>"
            for v in c.vehiculos
        ]) + "</ul>" if c.vehiculos else "<i>Sin vehículos</i>"
        content += f"<tr><td>{c.id}</td><td><a href='{url_for('cliente_detail', cliente_id=c.id)}'>{c.nombre}</a></td><td>{c.telefono or ''}</td><td>{vehs}</td>"
        content += f"<td><a class='btn btn-sm btn-primary me-1' href='{url_for('cliente_edit', cliente_id=c.id)}'>Editar</a>"
        content += f"<a class='btn btn-sm btn-danger' href='{url_for('cliente_delete', cliente_id=c.id)}' onclick='return confirm(\"Eliminar cliente y sus datos?\")'>Eliminar</a></td></tr>"
    content += "</tbody></table>"
    return render(content)


@app.route("/clientes/new", methods=["GET", "POST"])
@login_required
def cliente_new():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        if not nombre:
            flash("Nombre obligatorio.", "danger")
        else:
            if not nombre:
                flash("El nombre es obligatorio.", "danger")
                return redirect(url_for("cliente_new"))

            c = Cliente()
            c.nombre = nombre
            c.telefono = telefono

            db.session.add(c)
            db.session.commit()

            flash("Cliente creado.", "success")
            return redirect(url_for("clientes"))
    content = f"""
    <h3>Crear Cliente</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3"><label class="form-label">Nombre</label><input name="nombre" class="form-control" required></div>
      <div class="mb-3"><label class="form-label">Teléfono</label><input name="telefono" class="form-control"></div>
      <div class="d-flex gap-2"><button class="btn btn-success">Crear</button><a class="btn btn-secondary" href="{url_for('clientes')}">Cancelar</a></div>
    </form>
    """
    return render(content)


@app.route("/clientes/<int:cliente_id>")
@login_required
def cliente_detail(cliente_id):
    c = Cliente.query.get_or_404(cliente_id)
    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Cliente: {c.nombre}</h3>
      <div>
        <a class="btn btn-sm btn-primary" href="{url_for('cliente_edit', cliente_id=c.id)}">Editar</a>
        <a class="btn btn-sm btn-danger" href="{url_for('cliente_delete', cliente_id=c.id)}" onclick="return confirm('Eliminar cliente?')">Eliminar</a>
        <a class="btn btn-sm btn-success" href="{url_for('vehiculo_new', cliente_id=c.id)}">Agregar vehículo</a>
      </div>
    </div>
    <div class="card p-3 mb-3"><p><strong>Teléfono:</strong> {c.telefono or '—'}</p></div>
    <h5>Vehículos</h5>
    <table class="table table-striped"><thead class="table-dark"><tr><th>Patente</th><th>Modelo</th><th>Foto</th><th>Acciones</th></tr></thead><tbody>
    """
    for v in c.vehiculos:
        foto_td = f"<img src='{url_for('vehiculo_image', veh_id=v.id)}' class='thumb'>" if v.foto else "—"
        content += f"<tr><td>{v.patente}</td><td>{v.modelo or ''}</td><td>{foto_td}</td><td><a class='btn btn-sm btn-primary me-1' href='{url_for('vehiculo_edit', vehiculo_id=v.id)}'>Editar</a>"
        content += f"<a class='btn btn-sm btn-danger' href='{url_for('vehiculo_delete', vehiculo_id=v.id)}' onclick='return confirm(\"Eliminar vehículo?\")'>Eliminar</a>"
        content += f" <a class='btn btn-sm btn-warning' href='{url_for('ot_new', vehiculo_id=v.id)}'>Crear OT</a></td></tr>"
    content += "</tbody></table>"
    return render(content)


@app.route("/clientes/<int:cliente_id>/edit", methods=["GET", "POST"])
@login_required
def cliente_edit(cliente_id):
    c = Cliente.query.get_or_404(cliente_id)
    if request.method == "POST":
        c.nombre = request.form.get("nombre", "").strip()
        c.telefono = request.form.get("telefono", "").strip()
        db.session.commit()
        flash("Cliente actualizado.", "success")
        return redirect(url_for("cliente_detail", cliente_id=c.id))
    content = f"""
    <h3>Editar Cliente</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3"><label class="form-label">Nombre</label><input name="nombre" value="{c.nombre}" class="form-control" required></div>
      <div class="mb-3"><label class="form-label">Teléfono</label><input name="telefono" value="{c.telefono or ''}" class="form-control"></div>
      <div class="d-flex gap-2"><button class="btn btn-primary">Guardar</button><a class="btn btn-secondary" href="{url_for('cliente_detail', cliente_id=c.id)}">Cancelar</a></div>
    </form>
    """
    return render(content)


@app.route("/clientes/<int:cliente_id>/delete")
def cliente_delete(cliente_id):
    c = Cliente.query.get_or_404(cliente_id)
    db.session.delete(c)
    db.session.commit()
    flash("Cliente eliminado.", "info")
    return redirect(url_for("clientes"))


# =========================
# VEHÍCULOS (listar/crear/editar/eliminar/detalle) + subida imagen en DB
# =========================
def allowed_image_mime(mime):
    return mime.startswith("image/")


@app.route("/vehiculos")
def vehiculos():
    q = request.args.get("q", "").strip()
    if q:
        lista = (db.session.query(Vehiculo).join(
            Cliente).filter((Vehiculo.patente.ilike(f"%{q}%"))
                            | (Vehiculo.modelo.ilike(f"%{q}%"))
                            | (Cliente.nombre.ilike(f"%{q}%"))).all())
    else:
        lista = Vehiculo.query.order_by(Vehiculo.id.desc()).all()

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Vehículos</h3>
      <div><a class="btn btn-success" href="{url_for('vehiculo_new')}">Nuevo vehículo</a></div>
    </div>
    <form method="GET" class="d-flex mb-3"><input name="q" class="form-control me-2" placeholder="Buscar por patente, modelo o dueño..." value="{q}"><button class="btn btn-secondary">Buscar</button></form>
    <table class="table table-striped datatable"><thead class="table-dark"><tr><th>ID</th><th>Patente</th><th>Modelo</th><th>Dueño</th><th>Foto</th><th>Acciones</th></tr></thead><tbody>
    """

    for v in lista:
        foto_td = f"<img src='{url_for('vehiculo_image', veh_id=v.id)}' class='thumb'>" if v.foto else "—"
        content += f"<tr><td>{v.id}</td><td><a href='{url_for('vehiculo_detail', vehiculo_id=v.id)}'>{v.patente}</a></td><td>{v.modelo or ''}</td><td><a href='{url_for('cliente_detail', cliente_id=v.cliente.id)}'>{v.cliente.nombre}</a></td><td>{foto_td}</td>"
        content += f"<td><a class='btn btn-sm btn-primary me-1' href='{url_for('vehiculo_edit', vehiculo_id=v.id)}'>Editar</a><a class='btn btn-sm btn-danger' href='{url_for('vehiculo_delete', vehiculo_id=v.id)}' onclick='return confirm(\"Eliminar vehículo?\")'>Eliminar</a></td></tr>"
    content += "</tbody></table>"
    return render(content)


@app.route("/vehiculos/new", methods=["GET", "POST"])
def vehiculo_new():
    cliente_id_prefill = request.args.get("cliente_id", "")
    clientes_all = Cliente.query.order_by(Cliente.nombre).all()

    if request.method == "POST":
        cliente_id_raw = request.form.get("cliente_id", "").strip()

        try:
            cliente_id = int(cliente_id_raw)
        except ValueError:
            flash("Cliente inválido.", "danger")
            return redirect(url_for("vehiculo_new"))

        patente = request.form.get("patente", "").strip()
        modelo = request.form.get("modelo", "").strip()

        if not patente:
            flash("Patente obligatoria.", "danger")
            return redirect(url_for("vehiculo_new"))

        foto_file = request.files.get("foto", None)
        foto_bytes = None
        foto_mime = None

        if foto_file is not None and foto_file.filename:
            foto_bytes = foto_file.read()
            foto_mime = foto_file.mimetype or None

            if not foto_mime or not allowed_image_mime(foto_mime):
                flash("Archivo de imagen inválido.", "danger")
                return redirect(url_for("vehiculo_new"))

        v = Vehiculo()
        v.patente = patente
        v.modelo = modelo
        v.cliente_id = cliente_id
        v.foto = foto_bytes
        v.foto_mime = foto_mime

        db.session.add(v)
        db.session.commit()
        flash("Vehículo creado.", "success")
        return redirect(url_for("vehiculos"))

    options = "".join([
        f"<option value='{c.id}' {'selected' if cliente_id_prefill and cliente_id_prefill.isdigit() and int(cliente_id_prefill) == c.id else ''}>{c.nombre}</option>"
        for c in clientes_all
    ])

    content = f"""
    <h3>Nuevo Vehículo</h3>
    <form method="POST" enctype="multipart/form-data" class="card p-3">
      <div class="mb-3"><label class="form-label">Cliente</label><select name="cliente_id" class="form-select" required><option value=''>-- seleccionar --</option>{options}</select></div>
      <div class="mb-3"><label class="form-label">Patente</label><input name="patente" class="form-control" required></div>
      <div class="mb-3"><label class="form-label">Modelo</label><input name="modelo" class="form-control"></div>
      <div class="mb-3"><label class="form-label">Foto (opcional)</label><input type="file" name="foto" accept="image/*" class="form-control"></div>
      <div class="d-flex gap-2"><button class="btn btn-success">Crear</button><a class="btn btn-secondary" href="{url_for('vehiculos')}">Cancelar</a></div>
    </form>
    """
    return render(content)


@app.route("/vehiculos/<int:vehiculo_id>")
def vehiculo_detail(vehiculo_id):
    v = Vehiculo.query.get_or_404(vehiculo_id)
    foto_html = f"<img src='{url_for('vehiculo_image', veh_id=v.id)}' class='thumb mb-3'>" if v.foto else ""
    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Vehículo: {v.patente}</h3>
      <div>
        <a class="btn btn-sm btn-primary" href="{url_for('vehiculo_edit', vehiculo_id=v.id)}">Editar</a>
        <a class="btn btn-sm btn-danger" href="{url_for('vehiculo_delete', vehiculo_id=v.id)}" onclick="return confirm('Eliminar vehículo?')">Eliminar</a>
        <a class="btn btn-sm btn-warning" href="{url_for('ot_new', vehiculo_id=v.id)}">Crear OT</a>
      </div>
    </div>
    <div class="card p-3 mb-3">{foto_html}<p><strong>Patente:</strong> {v.patente}</p><p><strong>Modelo:</strong> {v.modelo or '—'}</p><p><strong>Dueño:</strong> <a href="{url_for('cliente_detail', cliente_id=v.cliente.id)}">{v.cliente.nombre}</a></p></div>
    <h5>Servicios</h5><a class="btn btn-sm btn-success mb-2" href="{url_for('servicio_new', vehiculo_id=v.id)}">Nuevo servicio</a>
    <table class="table table-striped"><thead class="table-dark"><tr><th>Fecha</th><th>Descripción</th><th>Costo</th><th>Acciones</th></tr></thead><tbody>
    """
    for s in v.servicios:
        content += f"<tr><td>{s.fecha.strftime('%Y-%m-%d')}</td><td>{s.descripcion}</td><td>{s.costo or ''}</td><td><a class='btn btn-sm btn-danger' href='{url_for('servicio_delete', servicio_id=s.id)}' onclick='return confirm(\"Eliminar servicio?\")'>Eliminar</a></td></tr>"
    content += "</tbody></table>"
    return render(content)


@app.route("/vehiculos/<int:vehiculo_id>/edit", methods=["GET", "POST"])
def vehiculo_edit(vehiculo_id):
    v = Vehiculo.query.get_or_404(vehiculo_id)
    clientes_all = Cliente.query.order_by(Cliente.nombre).all()
    if request.method == "POST":
        try:
            cliente_id = int(request.form.get("cliente_id") or 0)
        except:
            flash("Cliente inválido.", "danger")
            return redirect(url_for("vehiculo_edit", vehiculo_id=v.id))
        v.patente = request.form.get("patente", "").strip()
        v.modelo = request.form.get("modelo", "").strip()
        # imagen opcional: si se envía, reemplaza
        foto_file = request.files.get("foto")
        if foto_file and foto_file.filename:
            foto_bytes = foto_file.read()
            foto_mime = foto_file.mimetype or None
            if not foto_mime or not allowed_image_mime(foto_mime):
                flash("Archivo de imagen inválido.", "danger")
                return redirect(url_for("vehiculo_edit", vehiculo_id=v.id))
            v.foto = foto_bytes
            v.foto_mime = foto_mime
        v.cliente_id = cliente_id
        db.session.commit()
        flash("Vehículo actualizado.", "success")
        return redirect(url_for("vehiculo_detail", vehiculo_id=v.id))
    options = "".join([
        f"<option value='{c.id}' {'selected' if c.id==v.cliente_id else ''}>{c.nombre}</option>"
        for c in clientes_all
    ])
    foto_preview = f"<div class='mb-2'><img src='{url_for('vehiculo_image', veh_id=v.id)}' class='thumb'></div>" if v.foto else ""
    content = f"""
    <h3>Editar Vehículo</h3>
    <form method="POST" enctype="multipart/form-data" class="card p-3">
      <div class="mb-3"><label class="form-label">Cliente</label><select name="cliente_id" class="form-select" required>{options}</select></div>
      <div class="mb-3"><label class="form-label">Patente</label><input name="patente" value="{v.patente}" class="form-control" required></div>
      <div class="mb-3"><label class="form-label">Modelo</label><input name="modelo" value="{v.modelo or ''}" class="form-control"></div>
      <div class="mb-3"><label class="form-label">Foto (subir para reemplazar)</label>{foto_preview}<input type="file" name="foto" accept="image/*" class="form-control"></div>
      <div class="d-flex gap-2"><button class="btn btn-primary">Guardar</button><a class="btn btn-secondary" href="{url_for('vehiculo_detail', vehiculo_id=v.id)}">Cancelar</a></div>
    </form>
    """
    return render(content)


@app.route("/vehiculos/<int:vehiculo_id>/delete")
def vehiculo_delete(vehiculo_id):
    v = Vehiculo.query.get_or_404(vehiculo_id)
    db.session.delete(v)
    db.session.commit()
    flash("Vehículo eliminado.", "info")
    return redirect(url_for("vehiculos"))


# =========================
# SERVICIOS
# =========================
@app.route("/servicios")
def servicios_list():
    lista = Servicio.query.order_by(Servicio.fecha.desc()).all()
    content = "<h3>Servicios</h3><a class='btn btn-sm btn-success mb-3' href='{0}'>Nuevo servicio</a>".format(
        url_for('servicio_new'))
    content += "<table class='table table-striped datatable'><thead class='table-dark'><tr><th>ID</th><th>Vehículo</th><th>Fecha</th><th>Descripción</th><th>Costo</th><th>Acciones</th></tr></thead><tbody>"
    for s in lista:
        content += f"<tr><td>{s.id}</td><td><a href='{url_for('vehiculo_detail', vehiculo_id=s.vehiculo.id)}'>{s.vehiculo.patente}</a></td><td>{s.fecha.strftime('%Y-%m-%d')}</td><td>{s.descripcion}</td><td>{s.costo or ''}</td>"
        content += (
            f"<td>"
            f"<a class='btn btn-sm btn-primary me-1' href='{url_for('servicio_detail', servicio_id=s.id)}'>Ver</a>"
            f"<a class='btn btn-sm btn-warning me-1' href='{url_for('servicio_edit', servicio_id=s.id)}'>Editar</a>"
            f"<a class='btn btn-sm btn-outline-secondary me-1' href='{url_for('servicio_pdf', servicio_id=s.id)}'>PDF</a>"
            f"<a class='btn btn-sm btn-danger' href='{url_for('servicio_delete', servicio_id=s.id)}' onclick='return confirm(\"Eliminar servicio?\")'>Eliminar</a>"
            f"</td></tr>")

    content += "</tbody></table>"
    return render(content)


@app.route("/vehiculos/<int:vehiculo_id>/servicios")
def servicios_for_vehiculo(vehiculo_id):
    v = Vehiculo.query.get_or_404(vehiculo_id)
    content = f"<h3>Servicios — {v.patente}</h3><a class='btn btn-sm btn-success mb-3' href='{url_for('servicio_new', vehiculo_id=v.id)}'>Nuevo servicio</a>"
    content += "<table class='table table-striped'><thead class='table-dark'><tr><th>Fecha</th><th>Descripción</th><th>Costo</th><th>Acciones</th></tr></thead><tbody>"
    for s in v.servicios:
        content += f"<tr><td>{s.fecha.strftime('%Y-%m-%d')}</td><td>{s.descripcion}</td><td>{s.costo or ''}</td><td><a class='btn btn-sm btn-danger' href='{url_for('servicio_delete', servicio_id=s.id)}' onclick='return confirm(\"Eliminar servicio?\")'>Eliminar</a></td></tr>"
    content += "</tbody></table>"
    return render(content)


@app.route("/servicios/new", methods=["GET", "POST"])
@app.route("/vehiculos/<int:vehiculo_id>/servicios/new",
           methods=["GET", "POST"])
def servicio_new(vehiculo_id=None):
    vehiculos_all = Vehiculo.query.order_by(Vehiculo.patente).all()
    if request.method == "POST":
        try:
            vehiculo_id_sel = int(request.form.get("vehiculo_id") or 0)
        except:
            flash("Vehículo inválido.", "danger")
            return redirect(request.url)
        descripcion = request.form.get("descripcion", "").strip()
        costo_raw = request.form.get("costo", "").strip()
        costo = float(costo_raw) if costo_raw else None
        s = Servicio()
        s.vehiculo_id = vehiculo_id_sel
        s.descripcion = descripcion
        s.costo = costo

        db.session.add(s)
        db.session.commit()
        db.session.add(s)
        db.session.commit()
        flash("Servicio registrado.", "success")
        return redirect(url_for("servicios_list"))
    options_veh = "".join([
        f"<option value='{v.id}' {'selected' if vehiculo_id and v.id==vehiculo_id else ''}>{v.patente} — {v.cliente.nombre}</option>"
        for v in vehiculos_all
    ])
    content = f"""
    <h3>Nuevo Servicio</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3"><label class="form-label">Vehículo</label><select name="vehiculo_id" class="form-select" required>{options_veh}</select></div>
      <div class="mb-3"><label class="form-label">Descripción</label><textarea name="descripcion" class="form-control" required></textarea></div>
      <div class="mb-3"><label class="form-label">Costo</label><input name="costo" class="form-control" placeholder="Valor numérico (opcional)"></div>
      <div class="d-flex gap-2"><button class="btn btn-success">Registrar</button><a class="btn btn-secondary" href="{url_for('servicios_list')}">Cancelar</a></div>
    </form>
    """
    return render(content)


@app.route("/servicios/<int:servicio_id>/edit", methods=["GET", "POST"])
def servicio_edit(servicio_id):
    s = Servicio.query.get_or_404(servicio_id)
    vehiculos_all = Vehiculo.query.order_by(Vehiculo.patente).all()

    if request.method == "POST":
        try:
            vehiculo_id_sel = int(request.form.get("vehiculo_id") or 0)
        except:
            flash("Vehículo inválido.", "danger")
            return redirect(request.url)

        s.vehiculo_id = vehiculo_id_sel
        s.descripcion = request.form.get("descripcion", "").strip()

        costo_raw = request.form.get("costo", "").strip()
        s.costo = float(costo_raw) if costo_raw else None

        db.session.commit()
        flash("Servicio actualizado correctamente.", "success")
        return redirect(url_for("servicio_detail", servicio_id=s.id))

    # opciones de vehículos en el select
    options_veh = "".join([
        f"<option value='{v.id}' {'selected' if v.id == s.vehiculo_id else ''}>{v.patente} — {v.cliente.nombre}</option>"
        for v in vehiculos_all
    ])

    content = f"""
    <h3>Editar Servicio Nº {s.id}</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Vehículo</label>
        <select name="vehiculo_id" class="form-select" required>
          {options_veh}
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Descripción</label>
        <textarea name="descripcion" class="form-control" required>{s.descripcion}</textarea>
      </div>

      <div class="mb-3">
        <label class="form-label">Costo</label>
        <input name="costo" class="form-control" value="{s.costo or ''}" placeholder="Valor numérico (opcional)">
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-primary">Guardar cambios</button>
        <a class="btn btn-secondary" href="{url_for('servicio_detail', servicio_id=s.id)}">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/servicios/<int:servicio_id>/pdf")
def servicio_pdf(servicio_id):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from io import BytesIO
    import requests

    s = Servicio.query.get_or_404(servicio_id)
    buffer = BytesIO()

    # Documento PDF
    doc = SimpleDocTemplate(buffer,
                            pagesize=A4,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=40,
                            bottomMargin=40)

    styles = getSampleStyleSheet()
    title = styles["Heading1"]
    normal = styles["BodyText"]

    story = []

    # ------------------------
    # LOGO DE LA EMPRESA
    # ------------------------
    logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoO9kvULPTw3uLlRBM0c8LI3EXronn_x6sDQ&s"
    logo_bytes = BytesIO(requests.get(logo_url).content)
    logo = Image(logo_bytes, width=120, height=120)
    story.append(logo)
    story.append(Spacer(1, 20))

    # ------------------------
    # TÍTULO
    # ------------------------
    story.append(Paragraph(f"<b>Informe de Servicio Nº {s.id}</b>", title))
    story.append(
        Paragraph(f"Fecha: {s.fecha.strftime('%Y-%m-%d %H:%M')}", normal))
    story.append(Spacer(1, 20))

    # ------------------------
    # DATOS DEL SERVICIO
    # ------------------------
    data = [
        ["Patente", s.vehiculo.patente],
        ["Modelo", s.vehiculo.modelo],  # ESTE CAMPO SÍ EXISTE
        ["Cliente", s.vehiculo.cliente.nombre],
        ["Descripción", s.descripcion],
        ["Costo", s.costo or "—"],
    ]

    table = Table(data, colWidths=[120, 320])
    table.setStyle(
        TableStyle([("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#e8e8e8")),
                    ("BACKGROUND", (0, 1), (0, -1), colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica")]))

    story.append(table)
    story.append(Spacer(1, 30))

    # Construcción del PDF
    doc.build(story)
    buffer.seek(0)

    filename = f"Servicio_{s.id}.pdf"
    return send_file(buffer,
                     as_attachment=True,
                     download_name=filename,
                     mimetype="application/pdf")


@app.route("/servicios/<int:servicio_id>")
def servicio_detail(servicio_id):
    s = Servicio.query.get_or_404(servicio_id)

    content = f"""
    <h3>Servicio Nº {s.id}</h3>
    <div class="card p-3 mb-3">
      <p><strong>Vehículo:</strong> <a href="{url_for('vehiculo_detail', vehiculo_id=s.vehiculo.id)}">{s.vehiculo.patente}</a></p>
      <p><strong>Cliente:</strong> <a href="{url_for('cliente_detail', cliente_id=s.vehiculo.cliente.id)}">{s.vehiculo.cliente.nombre}</a></p>
      <p><strong>Fecha:</strong> {s.fecha.strftime('%Y-%m-%d %H:%M')}</p>
      <p><strong>Descripción:</strong><br>{s.descripcion}</p>
      <p><strong>Costo:</strong> {s.costo or '—'}</p>
      <a class="btn btn-outline-secondary" href="{url_for('servicio_pdf', servicio_id=s.id)}">Descargar PDF</a>
    </div>
    """
    return render(content)


@app.route("/servicios/<int:servicio_id>/delete")
def servicio_delete(servicio_id):
    s = Servicio.query.get_or_404(servicio_id)
    db.session.delete(s)
    db.session.commit()
    flash("Servicio eliminado.", "info")
    return redirect(url_for("servicios_list"))


@app.route("/gastos_totales")
def gastos_totales():
    from sqlalchemy import func, extract

    # Suma total
    total_general = db.session.query(func.sum(GastoST.costo)).scalar() or 0

    # Suma por mes
    totales_mensuales = (db.session.query(
        extract("year", GastoST.fecha).label("anio"),
        extract("month", GastoST.fecha).label("mes"),
        func.sum(GastoST.costo).label("total")).group_by(
            "anio", "mes").order_by("anio", "mes").all())

    filas = ""
    for anio, mes, total in totales_mensuales:
        filas += f"<tr><td>{int(anio)}</td><td>{int(mes)}</td><td>$ {total:,.0f}</td></tr>"

    content = f"""
    <h3>Gastos Totales del Taller</h3>

    <div class="card p-3 mb-4">
        <h4>Total General Gastado:</h4>
        <h2 class="text-danger">$ {total_general:,.0f}</h2>
    </div>

    <h4>Gastos por Mes</h4>

    <table class="table table-striped datatable">
        <thead class="table-dark">
            <tr>
                <th>Año</th>
                <th>Mes</th>
                <th>Total Gastado</th>
            </tr>
        </thead>
        <tbody>
            {filas}
        </tbody>
    </table>
    """

    return render(content)


# =========================
# GASTOS ST (Gastos del Taller)
# =========================


@app.route("/gastos")
def gastos_list():
    lista = GastoST.query.order_by(GastoST.fecha.desc()).all()
    content = "<h3>Gastos del Taller (ST)</h3><a class='btn btn-sm btn-success mb-3' href='/gastos/new'>Nuevo gasto</a>"
    content += "<table class='table table-striped datatable'><thead class='table-dark'><tr><th>ID</th><th>Fecha</th><th>Descripción</th><th>Costo</th><th>Acciones</th></tr></thead><tbody>"

    for g in lista:
        content += f"""
        <tr>
            <td>{g.id}</td>
            <td>{g.fecha.strftime('%Y-%m-%d')}</td>
            <td>{g.descripcion}</td>
            <td>{g.costo or '—'}</td>
            <td>
                <a class='btn btn-sm btn-primary' href='/gastos/{g.id}'>Ver</a>
                <a class='btn btn-sm btn-danger' href='/gastos/{g.id}/delete' onclick='return confirm("Eliminar gasto?")'>Eliminar</a>
            </td>
        </tr>
        """

    content += "</tbody></table>"
    return render(content)


@app.route("/gastos/new", methods=["GET", "POST"])
def gasto_new():
    if request.method == "POST":
        descripcion = request.form.get("descripcion", "").strip()
        costo_raw = request.form.get("costo", "").strip()
        costo = float(costo_raw) if costo_raw else None

        g = GastoST()
        g.descripcion = descripcion
        g.costo = costo
        db.session.add(g)
        db.session.commit()

        flash("Gasto del Taller registrado.", "success")
        return redirect("/gastos")

    content = """
    <h3>Nuevo Gasto ST</h3>
    <form method="POST" class="card p-3">
      <div class='mb-3'>
        <label class='form-label'>Descripción</label>
        <textarea name='descripcion' class='form-control' required></textarea>
      </div>
      <div class='mb-3'>
        <label class='form-label'>Costo</label>
        <input name='costo' class='form-control' placeholder='Valor en CLP (opcional)'>
      </div>
      <button class='btn btn-success'>Guardar</button>
      <a href='/gastos' class='btn btn-secondary'>Cancelar</a>
    </form>
    """
    return render(content)


@app.route("/gastos/<int:gasto_id>")
def gasto_detail(gasto_id):
    g = GastoST.query.get_or_404(gasto_id)
    content = f"""
    <h3>Gasto ST Nº {g.id}</h3>
    <div class='card p-3'>
      <p><strong>Fecha:</strong> {g.fecha.strftime('%Y-%m-%d')}</p>
      <p><strong>Descripción:</strong><br>{g.descripcion}</p>
      <p><strong>Costo:</strong> {g.costo or '—'}</p>
      <a class='btn btn-danger' href='/gastos/{g.id}/delete' onclick='return confirm("Eliminar gasto?")'>Eliminar</a>
    </div>
    """
    return render(content)


@app.route("/gastos/<int:gasto_id>/delete")
def gasto_delete(gasto_id):
    g = GastoST.query.get_or_404(gasto_id)
    db.session.delete(g)
    db.session.commit()
    flash("Gasto eliminado.", "info")
    return redirect("/gastos")


# priotidades


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    titulo = db.Column(db.Text, nullable=False)
    
    detalle = db.Column(db.Text, nullable=True)

    estado = db.Column(
        db.String(30),
        default="Pendiente")  # Pendiente / En progreso / Hecho / Bloqueado
    prioridad = db.Column(db.String(20),
                          default="Media")  # Baja / Media / Alta / Urgente

    responsable = db.Column(db.String(80), nullable=True)
    vencimiento = db.Column(db.Date, nullable=True)


@app.route("/tareas")
@login_required
def tareas_list():
    q = request.args.get("q", "").strip()

    query = Tarea.query
    if q:
        query = query.filter((Tarea.titulo.ilike(f"%{q}%"))
                             | (Tarea.detalle.ilike(f"%{q}%"))
                             | (Tarea.responsable.ilike(f"%{q}%"))
                             | (Tarea.estado.ilike(f"%{q}%"))
                             | (Tarea.prioridad.ilike(f"%{q}%")))

    lista = query.order_by(Tarea.id.desc()).all()

    filas = ""
    for t in lista:
        venc = t.vencimiento.strftime("%Y-%m-%d") if t.vencimiento else "—"
        resp = t.responsable or "—"
        det = (t.detalle or "").replace("\n", "<br>")

        filas += f"""
        <tr>
          <td>{t.id}</td>
          <td><b>{t.titulo}</b><br><small class="text-muted">{det}</small></td>
          <td>{t.estado}</td>
          <td>{t.prioridad}</td>
          <td>{resp}</td>
          <td>{venc}</td>
          <td class="text-nowrap">
            <a class="btn btn-sm btn-warning" href="/tareas/{t.id}/edit">Editar</a>
            <a class="btn btn-sm btn-danger" href="/tareas/{t.id}/delete"
               onclick="return confirm('¿Eliminar tarea?')">Borrar</a>
          </td>
        </tr>
        """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Planilla de Tareas</h3>
      <a class="btn btn-success" href="/tareas/new">Nueva tarea</a>
    </div>

    <form method="GET" class="d-flex mb-3">
      <input name="q" class="form-control me-2" placeholder="Buscar..." value="{q}">
      <button class="btn btn-secondary">Buscar</button>
      <a class="btn btn-outline-secondary ms-2" href="/tareas">Limpiar</a>
    </form>

    <table class="table table-striped datatable">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Tarea</th>
          <th>Estado</th>
          <th>Prioridad</th>
          <th>Responsable</th>
          <th>Vence</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {filas}
      </tbody>
    </table>
    """
    return render(content)


@app.route("/tareas/new", methods=["GET", "POST"])
@login_required
def tareas_new():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        detalle = request.form.get("detalle", "").strip()
        estado = request.form.get("estado", "Pendiente").strip()
        prioridad = request.form.get("prioridad", "Media").strip()
        responsable = request.form.get("responsable", "").strip()
        venc_raw = request.form.get("vencimiento", "").strip()

        if not titulo:
            flash("El título es obligatorio.", "danger")
            return redirect("/tareas/new")

        vencimiento = None
        if venc_raw:
            try:
                vencimiento = datetime.strptime(venc_raw, "%Y-%m-%d").date()
            except:
                flash("Fecha de vencimiento inválida (usa YYYY-MM-DD).",
                      "danger")
                return redirect("/tareas/new")

        t = Tarea()
        t.titulo = titulo
        t.detalle = detalle or None
        t.estado = estado
        t.prioridad = prioridad
        t.responsable = responsable or None
        t.vencimiento = vencimiento

        db.session.add(t)
        db.session.commit()
        db.session.add(t)
        db.session.commit()
        flash("Tarea creada.", "success")
        return redirect("/tareas")

    content = """
    <h3>Nueva tarea</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Título</label>
        <input name="titulo" class="form-control" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Detalle</label>
        <textarea name="detalle" class="form-control" rows="4"></textarea>
      </div>

      <div class="row g-2">
        <div class="col-md-3 mb-3">
          <label class="form-label">Estado</label>
          <select name="estado" class="form-select">
            <option>Pendiente</option>
            <option>En progreso</option>
            <option>Bloqueado</option>
            <option>Hecho</option>
          </select>
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Prioridad</label>
          <select name="prioridad" class="form-select">
            <option>Baja</option>
            <option selected>Media</option>
            <option>Alta</option>
            <option>Urgente</option>
          </select>
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Responsable</label>
          <input name="responsable" class="form-control" placeholder="(opcional)">
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Vencimiento</label>
          <input type="date" name="vencimiento" class="form-control">
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-success">Guardar</button>
        <a class="btn btn-secondary" href="/tareas">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/tareas/<int:tarea_id>/edit", methods=["GET", "POST"])
@login_required
def tareas_edit(tarea_id):
    t = Tarea.query.get_or_404(tarea_id)

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        detalle = request.form.get("detalle", "").strip()
        estado = request.form.get("estado", "Pendiente").strip()
        prioridad = request.form.get("prioridad", "Media").strip()
        responsable = request.form.get("responsable", "").strip()
        venc_raw = request.form.get("vencimiento", "").strip()

        if not titulo:
            flash("El título es obligatorio.", "danger")
            return redirect(f"/tareas/{t.id}/edit")

        vencimiento = None
        if venc_raw:
            try:
                vencimiento = datetime.strptime(venc_raw, "%Y-%m-%d").date()
            except:
                flash("Fecha de vencimiento inválida (usa YYYY-MM-DD).",
                      "danger")
                return redirect(f"/tareas/{t.id}/edit")

        t.titulo = titulo
        t.detalle = detalle or None
        t.estado = estado
        t.prioridad = prioridad
        t.responsable = responsable or None
        t.vencimiento = vencimiento

        db.session.commit()
        flash("Tarea actualizada.", "success")
        return redirect("/tareas")

    venc_val = t.vencimiento.strftime("%Y-%m-%d") if t.vencimiento else ""

    def sel(v):
        return "selected" if v else ""

    content = f"""
    <h3>Editar tarea #{t.id}</h3>
    <form method="POST" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Título</label>
        <input name="titulo" class="form-control" value="{t.titulo}" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Detalle</label>
        <textarea name="detalle" class="form-control" rows="4">{t.detalle or ""}</textarea>
      </div>

      <div class="row g-2">
        <div class="col-md-3 mb-3">
          <label class="form-label">Estado</label>
          <select name="estado" class="form-select">
            <option {"selected" if t.estado=="Pendiente" else ""}>Pendiente</option>
            <option {"selected" if t.estado=="En progreso" else ""}>En progreso</option>
            <option {"selected" if t.estado=="Bloqueado" else ""}>Bloqueado</option>
            <option {"selected" if t.estado=="Hecho" else ""}>Hecho</option>
          </select>
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Prioridad</label>
          <select name="prioridad" class="form-select">
            <option {"selected" if t.prioridad=="Baja" else ""}>Baja</option>
            <option {"selected" if t.prioridad=="Media" else ""}>Media</option>
            <option {"selected" if t.prioridad=="Alta" else ""}>Alta</option>
            <option {"selected" if t.prioridad=="Urgente" else ""}>Urgente</option>
          </select>
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Responsable</label>
          <input name="responsable" class="form-control" value="{t.responsable or ""}">
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Vencimiento</label>
          <input type="date" name="vencimiento" class="form-control" value="{venc_val}">
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-primary">Guardar</button>
        <a class="btn btn-secondary" href="/tareas">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/tareas/<int:tarea_id>/delete")
@login_required
def tareas_delete(tarea_id):
    t = Tarea.query.get_or_404(tarea_id)
    db.session.delete(t)
    db.session.commit()
    flash("Tarea eliminada.", "info")
    return redirect("/tareas")


# =========================
# toma de horas
# =========================


class TomaHora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    fecha = db.Column(db.Date, nullable=False)  # día del trabajo
    responsable = db.Column(db.String(80), nullable=True)

    actividad = db.Column(db.String(200), nullable=False)
    detalle = db.Column(db.Text, nullable=True)

    horas = db.Column(db.Float, nullable=False, default=0)

    estado = db.Column(
        db.String(30),
        default="Pendiente")  # Pendiente / En progreso / Hecho / Pausado

    urgencia = db.Column(db.String(20),
                         default="Normal")  # Baja / Normal / Alta / Crítica
    rapidez = db.Column(db.String(30),
                        default="Hoy")  # Hoy / 24h / 48h / 72h / 1 semana


@app.route("/horas")
@login_required
def horas_list():
    q = request.args.get("q", "").strip()

    query = TomaHora.query
    if q:
        query = query.filter((TomaHora.actividad.ilike(f"%{q}%"))
                             | (TomaHora.detalle.ilike(f"%{q}%"))
                             | (TomaHora.responsable.ilike(f"%{q}%"))
                             | (TomaHora.estado.ilike(f"%{q}%"))
                             | (TomaHora.urgencia.ilike(f"%{q}%"))
                             | (TomaHora.rapidez.ilike(f"%{q}%")))

    lista = query.order_by(TomaHora.id.desc()).all()

    filas = ""
    for h in lista:
        fecha_txt = h.fecha.strftime("%Y-%m-%d") if h.fecha else "—"
        resp = h.responsable or "—"
        det = (h.detalle or "").replace("\n", "<br>")

        filas += f"""
        <tr>
          <td>{h.id}</td>
          <td>{fecha_txt}</td>
          <td>{resp}</td>
          <td><b>{h.actividad}</b><br><small class="text-muted">{det}</small></td>
          <td class="text-end">{h.horas:g}</td>
          <td>{h.estado}</td>
          <td>{h.urgencia}</td>
          <td>{h.rapidez}</td>
          <td class="text-nowrap">
            <a class="btn btn-sm btn-warning" href="/horas/{h.id}/edit">Editar</a>
            <a class="btn btn-sm btn-danger" href="/horas/{h.id}/delete"
               onclick="return confirm('¿Eliminar registro?')">Borrar</a>
          </td>
        </tr>
        """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Toma de Horas</h3>
      <a class="btn btn-success" href="/horas/new">Nuevo registro</a>
    </div>

    <form method="GET" class="d-flex mb-3">
      <input name="q" class="form-control me-2" placeholder="Buscar..." value="{q}">
      <button class="btn btn-secondary">Buscar</button>
      <a class="btn btn-outline-secondary ms-2" href="/horas">Limpiar</a>
    </form>

    <table class="table table-striped datatable">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Fecha</th>
          <th>Responsable</th>
          <th>vehiculo</th>
          <th>Horas</th>
          <th>Estado</th>
          <th>Urgencia</th>
          <th>Rapidez (SLA)</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {filas}
      </tbody>
    </table>
    """
    return render(content)


@app.route("/horas/new", methods=["GET", "POST"])
@login_required
def horas_new():
    if request.method == "POST":
        fecha_raw = request.form.get("fecha", "").strip()
        responsable = request.form.get("responsable", "").strip()
        actividad = request.form.get("vehiculo", "").strip()
        detalle = request.form.get("detalle", "").strip()

        horas_raw = request.form.get("horas", "").strip()
        estado = request.form.get("estado", "Pendiente").strip()
        urgencia = request.form.get("urgencia", "Normal").strip()
        rapidez = request.form.get("rapidez", "Hoy").strip()

        if not fecha_raw:
            flash("La fecha es obligatoria.", "danger")
            return redirect("/horas/new")

        try:
            fecha = datetime.strptime(fecha_raw, "%Y-%m-%d").date()
        except:
            flash("Fecha inválida (usa YYYY-MM-DD).", "danger")
            return redirect("/horas/new")

        if not actividad:
            flash("La actividad es obligatoria.", "danger")
            return redirect("/horas/new")

        # horas: aceptar 2,5 o 2.5
        horas_val = None
        if horas_raw:
            try:
                horas_val = float(horas_raw.replace(",", "."))
            except:
                flash("Horas inválidas (ej: 1.5 o 1,5).", "danger")
                return redirect("/horas/new")
        else:
            horas_val = 0

        h = TomaHora()
        h.fecha = fecha
        h.responsable = responsable or None
        h.actividad = actividad
        h.detalle = detalle or None
        h.horas = horas_val
        h.estado = estado
        h.urgencia = urgencia
        h.rapidez = rapidez

        db.session.add(h)
        db.session.commit()
        db.session.add(h)
        db.session.commit()
        flash("Registro creado.", "success")
        return redirect("/horas")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    content = f"""
    <h3>Nuevo registro de horas</h3>
    <form method="POST" class="card p-3">
      <div class="row g-2">
        <div class="col-md-3 mb-3">
          <label class="form-label">Fecha</label>
          <input type="date" name="fecha" class="form-control" value="{today}" required>
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Responsable</label>
          <input name="responsable" class="form-control" placeholder="(opcional)">
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Horas</label>
          <input name="horas" class="form-control" placeholder="Ej: 1.5 o 1,5" required>
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Estado</label>
          <select name="estado" class="form-select">
            <option>Pendiente</option>
            <option>En progreso</option>
            <option>Pausado</option>
            <option>Hecho</option>
          </select>
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">vehiculo</label>
        <input name="vehiculo" class="form-control" required>
      </div>

      <div class="mb-3">
        <label class="form-label">Detalle</label>
        <textarea name="detalle" class="form-control" rows="3"></textarea>
      </div>

      <div class="row g-2">
        <div class="col-md-6 mb-3">
          <label class="form-label">Urgencia</label>
          <select name="urgencia" class="form-select">
            <option>Baja</option>
            <option selected>Normal</option>
            <option>Alta</option>
            <option>Crítica</option>
          </select>
        </div>

        <div class="col-md-6 mb-3">
          <label class="form-label">Qué tan rápido debería ser (SLA)</label>
          <select name="rapidez" class="form-select">
            <option>Hoy</option>
            <option>24h</option>
            <option>48h</option>
            <option>72h</option>
            <option>1 semana</option>
          </select>
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-success">Guardar</button>
        <a class="btn btn-secondary" href="/horas">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/horas/<int:hora_id>/edit", methods=["GET", "POST"])
@login_required
def horas_edit(hora_id):
    h = TomaHora.query.get_or_404(hora_id)

    if request.method == "POST":
        fecha_raw = request.form.get("fecha", "").strip()
        responsable = request.form.get("responsable", "").strip()
        actividad = request.form.get("vehiculo", "").strip()
        detalle = request.form.get("detalle", "").strip()

        horas_raw = request.form.get("horas", "").strip()
        estado = request.form.get("estado", "Pendiente").strip()
        urgencia = request.form.get("urgencia", "Normal").strip()
        rapidez = request.form.get("rapidez", "Hoy").strip()

        try:
            fecha = datetime.strptime(fecha_raw, "%Y-%m-%d").date()
        except:
            flash("Fecha inválida (usa YYYY-MM-DD).", "danger")
            return redirect(f"/horas/{h.id}/edit")

        if not actividad:
            flash("La actividad es obligatoria.", "danger")
            return redirect(f"/horas/{h.id}/edit")

        try:
            horas_val = float(horas_raw.replace(",", "."))
        except:
            flash("Horas inválidas (ej: 1.5 o 1,5).", "danger")
            return redirect(f"/horas/{h.id}/edit")

        h.fecha = fecha
        h.responsable = responsable or None
        h.actividad = actividad
        h.detalle = detalle or None
        h.horas = horas_val
        h.estado = estado
        h.urgencia = urgencia
        h.rapidez = rapidez

        db.session.commit()
        flash("Registro actualizado.", "success")
        return redirect("/horas")

    fecha_val = h.fecha.strftime("%Y-%m-%d") if h.fecha else ""
    content = f"""
    <h3>Editar registro #{h.id}</h3>
    <form method="POST" class="card p-3">
      <div class="row g-2">
        <div class="col-md-3 mb-3">
          <label class="form-label">Fecha</label>
          <input type="date" name="fecha" class="form-control" value="{fecha_val}" required>
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Responsable</label>
          <input name="responsable" class="form-control" value="{h.responsable or ""}">
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Horas</label>
          <input name="horas" class="form-control" value="{h.horas:g}" required>
        </div>

        <div class="col-md-3 mb-3">
          <label class="form-label">Estado</label>
          <select name="estado" class="form-select">
            <option {"selected" if h.estado=="Pendiente" else ""}>Pendiente</option>
            <option {"selected" if h.estado=="En progreso" else ""}>En progreso</option>
            <option {"selected" if h.estado=="Pausado" else ""}>Pausado</option>
            <option {"selected" if h.estado=="Hecho" else ""}>Hecho</option>
          </select>
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">Vehiculo</label>
        <input name="vehiculo" class="form-control" value="{h.actividad}" required>

      </div>

      <div class="mb-3">
        <label class="form-label">Detalle</label>
        <textarea name="detalle" class="form-control" rows="3">{h.detalle or ""}</textarea>
      </div>

      <div class="row g-2">
        <div class="col-md-6 mb-3">
          <label class="form-label">Urgencia</label>
          <select name="urgencia" class="form-select">
            <option {"selected" if h.urgencia=="Baja" else ""}>Baja</option>
            <option {"selected" if h.urgencia=="Normal" else ""}>Normal</option>
            <option {"selected" if h.urgencia=="Alta" else ""}>Alta</option>
            <option {"selected" if h.urgencia=="Crítica" else ""}>Crítica</option>
          </select>
        </div>

        <div class="col-md-6 mb-3">
          <label class="form-label">Qué tan rápido debería ser (SLA)</label>
          <select name="rapidez" class="form-select">
            <option {"selected" if h.rapidez=="Hoy" else ""}>Hoy</option>
            <option {"selected" if h.rapidez=="24h" else ""}>24h</option>
            <option {"selected" if h.rapidez=="48h" else ""}>48h</option>
            <option {"selected" if h.rapidez=="72h" else ""}>72h</option>
            <option {"selected" if h.rapidez=="1 semana" else ""}>1 semana</option>
          </select>
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-primary">Guardar</button>
        <a class="btn btn-secondary" href="/horas">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/horas/<int:hora_id>/delete")
@login_required
def horas_delete(hora_id):
    h = TomaHora.query.get_or_404(hora_id)
    db.session.delete(h)
    db.session.commit()
    flash("Registro eliminado.", "info")
    return redirect("/horas")


# OTs (Orden de Trabajo) + imagen en OT
# =========================
def generar_numero_ot():
    hoy = datetime.utcnow().strftime("%Y%m%d")
    pref = f"OT-{hoy}-"
    existentes = OT.query.filter(OT.numero.like(f"{pref}%")).count()
    seq = existentes + 1
    return f"{pref}{seq:04d}"


@app.route("/ots")
def ots_list():
    lista = OT.query.order_by(OT.id).all()
    content = "<div class='d-flex justify-content-between mb-3'><h3>Ordenes de Trabajo (OT)</h3><a class='btn btn-success' href='{}'>Nueva OT</a></div>".format(
        url_for('ot_new'))
    content += "<table class='table table-striped datatable'><thead class='table-dark'><tr><th>Nº</th><th>Tipo</th><th>Vehículo</th><th>Cliente</th><th>Estado</th><th>Fecha</th><th>Foto</th><th>Acciones</th></tr></thead><tbody>"
    for ot in lista:
        foto_td = f"<img src='{url_for('ot_image', ot_id=ot.id)}' class='thumb'>" if ot.foto else "—"
        content += f"<tr><td>{ot.numero}</td><td>{ot.tipo_ot or 'externo'}</td><td><a href='{url_for('vehiculo_detail', vehiculo_id=ot.vehiculo.id)}'>{ot.vehiculo.patente}</a></td><td><a href='{url_for('cliente_detail', cliente_id=ot.vehiculo.cliente.id)}'>{ot.vehiculo.cliente.nombre}</a></td><td>{ot.estado}</td><td>{ot.fecha_creacion.strftime('%Y-%m-%d')}</td><td>{foto_td}</td>"

        # botón borrar
        content += (
            f"<td>"
            f"<a class='btn btn-sm btn-primary me-1' href='{url_for('ot_detail', ot_id=ot.id)}'>Ver</a>"
            f"<a class='btn btn-sm btn-warning me-1' href='{url_for('ot_edit', ot_id=ot.id)}'>Editar</a>"
            f"<a class='btn btn-sm btn-outline-secondary me-1' href='{url_for('ot_pdf', ot_id=ot.id)}'>PDF</a>"
            f"<a class='btn btn-sm btn-danger' href='{url_for('ot_delete', ot_id=ot.id)}' "
            f"onclick=\"return confirm('¿Eliminar OT? Esta acción no se puede deshacer.')\">Borrar</a>"
            f"</td></tr>")
    content += "</tbody></table>"
    return render(content)


@app.route("/ots/<int:ot_id>/edit", methods=["GET", "POST"])
@operador_required
def ot_edit(ot_id):
    ot = OT.query.get_or_404(ot_id)
    vehiculos_all = Vehiculo.query.order_by(Vehiculo.patente).all()

    if request.method == "POST":
        # Vehículo
        try:
            vehiculo_sel = int(request.form.get("vehiculo_id") or 0)
        except:
            flash("Vehículo inválido.", "danger")
            return redirect(request.url)

        # Campos
        descripcion = request.form.get("descripcion", "").strip()
        obs = request.form.get("observaciones", "").strip()
        estado = request.form.get("estado", "Abierta").strip()
        tipo_ot = request.form.get("tipo_ot", "externo").strip()
        costo_raw = request.form.get("costo", "").strip()
        costo = float(costo_raw) if costo_raw else None

        # Imagen opcional (si sube, reemplaza)
        foto_file = request.files.get("foto")
        if foto_file and foto_file.filename:
            foto_bytes = foto_file.read()
            foto_mime = foto_file.mimetype or None
            if not foto_mime or not allowed_image_mime(foto_mime):
                flash("Archivo de imagen inválido.", "danger")
                return redirect(request.url)
            ot.foto = foto_bytes
            ot.foto_mime = foto_mime

        # Guardar cambios
        ot.vehiculo_id = vehiculo_sel
        ot.descripcion_trabajo = descripcion
        ot.observaciones = obs or None
        ot.estado = estado
        ot.tipo_ot = tipo_ot
        ot.costo_estimado = costo

        db.session.commit()
        flash("OT actualizada correctamente.", "success")
        return redirect(url_for("ot_detail", ot_id=ot.id))

    # GET: armar formulario con datos actuales
    options = "".join([
        f"<option value='{v.id}' {'selected' if v.id == ot.vehiculo_id else ''}>"
        f"{v.patente} — {v.cliente.nombre}</option>" for v in vehiculos_all
    ])

    foto_preview = f"<div class='mb-2'><img src='{url_for('ot_image', ot_id=ot.id)}' class='thumb'></div>" if ot.foto else ""

    content = f"""
    <h3>Editar OT {ot.numero}</h3>
    <form method="POST" enctype="multipart/form-data" class="card p-3">
      <div class="mb-3">
        <label class="form-label">Vehículo</label>
        <select name="vehiculo_id" class="form-select" required>
          {options}
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">Tipo de OT</label>
        <select name="tipo_ot" class="form-select" required>
          <option value="externo" {"selected" if ot.tipo_ot=="externo" else ""}>Auto externo</option>
          <option value="propio" {"selected" if ot.tipo_ot=="propio" else ""}>Auto propio</option>
          <option value="venta" {"selected" if ot.tipo_ot=="venta" else ""}>Auto por venta</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Descripción del trabajo</label>
        <textarea name="descripcion" class="form-control" required>{ot.descripcion_trabajo or ""}</textarea>
      </div>

      <div class="row g-2">
        <div class="col-md-4 mb-3">
          <label class="form-label">Estado</label>
          <select name="estado" class="form-select">
            <option {"selected" if ot.estado=="Abierta" else ""}>Abierta</option>
            <option {"selected" if ot.estado=="En progreso" else ""}>En progreso</option>
            <option {"selected" if ot.estado=="Cerrada" else ""}>Cerrada</option>
          </select>
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Costo estimado</label>
          <input name="costo" class="form-control" value="{ot.costo_estimado or ""}">
        </div>

        <div class="col-md-4 mb-3">
          <label class="form-label">Foto (subir para reemplazar)</label>
          {foto_preview}
          <input type="file" name="foto" accept="image/*" class="form-control">
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label">Observaciones</label>
        <textarea name="observaciones" class="form-control">{ot.observaciones or ""}</textarea>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-primary">Guardar</button>
        <a class="btn btn-secondary" href="{url_for('ot_detail', ot_id=ot.id)}">Cancelar</a>
      </div>
    </form>
    """
    return render(content)


@app.route("/ots/new", methods=["GET", "POST"])
@app.route("/vehiculos/<int:vehiculo_id>/ots/new", methods=["GET", "POST"])
def ot_new(vehiculo_id=None):
    vehiculos_all = Vehiculo.query.order_by(Vehiculo.patente).all()
    if request.method == "POST":
        try:
            vehiculo_sel = int(request.form.get("vehiculo_id") or 0)
        except:
            flash("Vehículo inválido.", "danger")
            return redirect(request.url)
        descripcion = request.form.get("descripcion", "").strip()
        obs = request.form.get("observaciones", "").strip()
        costo_raw = request.form.get("costo", "").strip()
        costo = float(costo_raw) if costo_raw else None
        tipo_ot = request.form.get("tipo_ot", "externo").strip()

        # imagen opcional
        foto_file = request.files.get("foto")
        foto_bytes = None
        foto_mime = None
        if foto_file and foto_file.filename:
            foto_bytes = foto_file.read()
            foto_mime = foto_file.mimetype or None
            if not foto_mime or not allowed_image_mime(foto_mime):
                flash("Archivo de imagen inválido.", "danger")
                return redirect(request.url)

        numero = generar_numero_ot()
        ot = OT()
        ot.numero = numero
        ot.vehiculo_id = vehiculo_sel
        ot.descripcion_trabajo = descripcion
        ot.observaciones = obs
        ot.costo_estimado = costo
        ot.tipo_ot = tipo_ot
        ot.foto = foto_bytes
        ot.foto_mime = foto_mime

        db.session.add(ot)
        db.session.commit()
        flash(f"OT {numero} creada.", "success")
        return redirect(url_for("ots_list"))

    options = "".join([
        f"<option value='{v.id}' {'selected' if vehiculo_id and v.id==vehiculo_id else ''}>{v.patente} — {v.cliente.nombre}</option>"
        for v in vehiculos_all
    ])
    content = f"""
    <h3>Crear OT</h3>
    <form method="POST" enctype="multipart/form-data" class="card p-3">
      <div class="mb-3"><label class="form-label">Vehículo</label><select name="vehiculo_id" class="form-select" required>{options}</select></div>
      <div class="mb-3">
        <label class="form-label">Tipo de OT</label>
        <select name="tipo_ot" class="form-select" required>
          <option value="externo" selected>Auto externo</option>
          <option value="propio">Auto propio</option>
          <option value="venta">Auto por venta</option>
        </select>
      </div>
      <div class="mb-3"><label class="form-label">Descripción del trabajo</label><textarea name="descripcion" class="form-control" required></textarea></div>
      <div class="mb-3"><label class="form-label">Costo estimado</label><input name="costo" class="form-control" placeholder="Número (opcional)"></div>
      <div class="mb-3"><label class="form-label">Observaciones</label><textarea name="observaciones" class="form-control"></textarea></div>
      <div class="mb-3"><label class="form-label">Foto (opcional)</label><input type="file" name="foto" accept="image/*" class="form-control"></div>
      <div class="d-flex gap-2"><button class="btn btn-success">Crear OT</button><a class="btn btn-secondary" href="{url_for('ots_list')}">Cancelar</a></div>
    </form>
    """
    return render(content)


@app.route("/ots/<int:ot_id>")
def ot_detail(ot_id):
    ot = OT.query.get_or_404(ot_id)

    # ================================================
    # SECCIÓN NUEVA — TABLA DE REPUESTOS USADOS
    # ================================================
    rep_rows = ""
    for u in ot.repuestos_usados:
        rep_rows += f"""
        <tr>
            <td>{u.repuesto.nombre}</td>
            <td>{u.cantidad}</td>
        </tr>
        """

    repuestos_html = f"""
    <hr>
    <h4>Repuestos utilizados</h4>
    <table class="table table-striped">
        <thead class="table-dark">
            <tr>
                <th>Repuesto</th>
                <th>Cantidad</th>
            </tr>
        </thead>
        <tbody>
            {rep_rows}
        </tbody>
    </table>

    <a class="btn btn-sm btn-primary" href="/ot/{ot.id}/repuestos/add">Agregar repuesto</a>
    """
    # ================================================
    # FIN SECCIÓN NUEVA
    # ================================================

    foto_html = f"<img src='{url_for('ot_image', ot_id=ot.id)}' class='thumb mb-3'>" if ot.foto else ""

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>OT {ot.numero}</h3>
      <div>
        <a class="btn btn-sm btn-outline-secondary" href="{url_for('ot_pdf', ot_id=ot.id)}">Descargar PDF</a>
      </div>
    </div>

    <div class="card p-3 mb-3">{foto_html}
      <p><strong>Vehículo:</strong> <a href="{url_for('vehiculo_detail', vehiculo_id=ot.vehiculo.id)}">{ot.vehiculo.patente}</a></p>
      <p><strong>Cliente:</strong> <a href="{url_for('cliente_detail', cliente_id=ot.vehiculo.cliente.id)}">{ot.vehiculo.cliente.nombre}</a></p>
      <p><strong>Estado:</strong> {ot.estado}</p>
      <p><strong>Tipo OT:</strong> {ot.tipo_ot or 'externo'}</p>
      <p><strong>Fecha:</strong> {ot.fecha_creacion.strftime('%Y-%m-%d %H:%M')}</p>
      <p><strong>Descripción:</strong><br>{ot.descripcion_trabajo}</p>
      <p><strong>Observaciones:</strong><br>{ot.observaciones or '—'}</p>
      <p><strong>Costo estimado:</strong> {ot.costo_estimado or '—'}</p>
    </div>

    <!-- AQUI INSERTAMOS LA TABLA DE REPUESTOS -->
    {repuestos_html}
    """

    return render(content)


#  NUEVA RUTA PARA ELIMINAR OTs
@app.route("/ots/<int:ot_id>/delete")
def ot_delete(ot_id):
    ot = OT.query.get_or_404(ot_id)
    db.session.delete(ot)
    db.session.commit()
    flash("OT eliminada correctamente.", "success")
    return redirect(url_for("ots_list"))


@app.route("/ots/<int:ot_id>/pdf")
def ot_pdf(ot_id):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from io import BytesIO
    import urllib.request

    ot = OT.query.get_or_404(ot_id)

    # Crear número correlativo con ceros (0001, 0023, etc.)
    numero_correlativo = str(ot.id).zfill(4)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=A4,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=40,
                            bottomMargin=40)

    styles = getSampleStyleSheet()
    title = styles["Heading1"]
    title.fontSize = 16
    title.leading = 20

    subtitle = styles["Heading2"]
    subtitle.fontSize = 12
    subtitle.leading = 14

    normal = styles["BodyText"]
    normal.fontSize = 10
    normal.leading = 12

    story = []

    # -------------------------------
    # CARGAR IMAGEN DEL LOGO DESDE URL
    # -------------------------------
    logo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoO9kvULPTw3uLlRBM0c8LI3EXronn_x6sDQ&s"

    logo_buffer = BytesIO()
    logo_buffer.write(urllib.request.urlopen(logo_url).read())
    logo_buffer.seek(0)

    logo = Image(logo_buffer, width=100, height=100)
    logo.hAlign = "LEFT"

    story.append(logo)
    story.append(Spacer(1, 10))

    # Línea dorada
    story.append(Paragraph("<font color='#DAA520'><hr/></font>", normal))
    story.append(Spacer(1, 10))

    # -------------------------------
    # TÍTULO
    # -------------------------------
    story.append(
        Paragraph(f"<b>Orden de Trabajo Nº {numero_correlativo}</b>", title))
    story.append(
        Paragraph(
            f"Fecha de creación: {ot.fecha_creacion.strftime('%Y-%m-%d %H:%M')}",
            normal))
    story.append(Spacer(1, 12))

    # Línea separadora dorada
    story.append(Spacer(1, 6))
    story.append(Paragraph("<font color='#DAA520'><hr/></font>", normal))
    story.append(Spacer(1, 12))

    # -------------------------------
    # TABLA: CLIENTE Y VEHÍCULO
    # -------------------------------
    data = [
        ["Cliente", ot.vehiculo.cliente.nombre],
        ["Teléfono", ot.vehiculo.cliente.telefono or "—"],
        ["Vehículo", f"{ot.vehiculo.patente} — {ot.vehiculo.modelo or '—'}"],
    ]

    table = Table(data, colWidths=[100, 340])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))

    story.append(Paragraph("Datos del Cliente y Vehículo", subtitle))
    story.append(table)
    story.append(Spacer(1, 15))

    # -------------------------------
    # TRABAJO SOLICITADO
    # -------------------------------
    story.append(Paragraph("Trabajo solicitado", subtitle))

    trabajo_text = ot.descripcion_trabajo.replace("\n", "<br/>")
    story.append(Paragraph(f"<para>{trabajo_text}</para>", normal))
    story.append(Spacer(1, 12))

    # -------------------------------
    # OBSERVACIONES
    # -------------------------------
    if ot.observaciones:
        story.append(Paragraph("Observaciones", subtitle))
        obs_text = ot.observaciones.replace("\n", "<br/>")
        story.append(Paragraph(f"<para>{obs_text}</para>", normal))
        story.append(Spacer(1, 12))

    # -------------------------------
    # COSTO Y ESTADO
    # -------------------------------
    story.append(Paragraph("Información de Trabajo", subtitle))

    costo_txt = str(int(float(
        ot.costo_estimado))) if ot.costo_estimado is not None else "—"

    data2 = [
        ["Tipo OT", ot.tipo_ot or "externo"],
        ["Costo", costo_txt],
        ["Estado", ot.estado],
    ]

    table2 = Table(data2, colWidths=[120, 320])
    table2.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))

    story.append(table2)
    story.append(Spacer(1, 30))

    # -------------------------------
    # FIRMAS
    # -------------------------------
    story.append(Spacer(1, 20))
    story.append(Paragraph("______________________________", normal))
    story.append(Paragraph("Firma cliente", normal))
    story.append(Spacer(1, 20))

    story.append(Paragraph("______________________________", normal))
    story.append(Paragraph("Firma taller", normal))

    # Construir PDF
    doc.build(story)

    buffer.seek(0)
    filename = f"OT_{numero_correlativo}.pdf"
    return send_file(buffer,
                     as_attachment=True,
                     download_name=filename,
                     mimetype="application/pdf")


# =========================
# INICIALIZACIÓN / RUN
# =========================


def sync_postgres_sequences():
    """Tras restaurar un dump, las secuencias pueden quedar desfasadas."""
    if db.engine.dialect.name != "postgresql":
        return
    pairs = [
        ("cliente_id_seq", "cliente"),
        ("cotizacion_id_seq", "cotizacion"),
        ("gasto_st_id_seq", "gasto_st"),
        ("ot_id_seq", "ot"),
        ("repuesto_id_seq", "repuesto"),
        ("repuesto_usado_id_seq", "repuesto_usado"),
        ("servicio_id_seq", "servicio"),
        ("tarea_id_seq", "tarea"),
        ("toma_hora_id_seq", "toma_hora"),
        ("usuario_id_seq", "usuario"),
        ("vehiculo_id_seq", "vehiculo"),
    ]
    for seq, table in pairs:
        try:
            mx = db.session.execute(
                text(f"SELECT MAX(id) FROM public.{table}")
            ).scalar()
            if mx is not None:
                db.session.execute(
                    text(f"SELECT setval('public.{seq}', :mx, true)"),
                    {"mx": int(mx)},
                )
        except Exception as ex:
            print(f"Aviso: no se pudo sincronizar {seq}: {ex}")
    db.session.commit()


if __name__ == "__main__":
    _port = int(os.environ.get("PORT", "5000"))
    _debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    with app.app_context():
        db.create_all()
        crear_usuarios_default()
        ensure_columns()
        sync_postgres_sequences()
    app.run(host="0.0.0.0", port=_port, debug=_debug)
