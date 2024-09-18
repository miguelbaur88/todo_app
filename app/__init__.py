import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# Datenbank initialisieren
db = SQLAlchemy()

# Login-Manager initialisieren
login_manager = LoginManager()
login_manager.login_view = 'login'

# CSRF-Schutz aktivieren
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Definiere das Basisverzeichnis
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Konfiguriere die SQLite-Datenbank
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')
    app.config['SECRET_KEY'] = 'geheimeschluessel'

    # Initialisiere Datenbank, Login-Manager und CSRF-Schutz mit der App
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Importiere das User-Modell hier, nachdem die App initialisiert wurde
    from app.models import User

    # Definiere die user_loader-Funktion
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Importiere die Routen und konfiguriere sie
    from app.routes import configure_routes
    configure_routes(app)

    # Datenbanktabellen erstellen (nur beim ersten Start)
    with app.app_context():
        db.create_all()

    return app
