from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, cors


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})

    # Registrar blueprints
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.clients import clients_bp
    from app.routes.case_files import case_files_bp
    from app.routes.alerts import alerts_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(case_files_bp)
    app.register_blueprint(alerts_bp)

    # Registrar comandos CLI
    from app.seed.demo import seed_demo_command
    app.cli.add_command(seed_demo_command)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app