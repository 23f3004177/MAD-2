from flask import Flask, jsonify, request
from models import db, User, Patient
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.doctor import doctor_bp
from routes.patient import patient_bp
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from extensions import cache, mail
from celery import Celery, Task

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ----------------------
    # CONFIG
    # ----------------------
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # change in production
    from celery.schedules import crontab
    app.config.update(
        CELERY=dict(
            broker_url="redis://localhost:6379/1",
            result_backend="redis://localhost:6379/2",
            timezone="UTC",
            enable_utc=True,
            broker_connection_retry_on_startup=True,
            imports=("jobs",),
            beat_schedule={
                "daily-reminders": {
                    "task": "jobs.send_daily_reminders",
                    "schedule": crontab(hour=8, minute=0), # morning everyday
                },
                "monthly-report": {
                    "task": "jobs.send_monthly_activity_report",
                    "schedule": crontab(day_of_month="1", hour=9, minute=0), # 1st day of month
                }
            }
        ),
        MAIL_SERVER='localhost',
        MAIL_PORT=1025,
        MAIL_USE_TLS=False,
        MAIL_USERNAME=None,
        MAIL_PASSWORD=None,
        MAIL_DEFAULT_SENDER='noreply@trimed.com'
    )

    # ----------------------
    # INIT EXTENSIONS
    # ----------------------
    db.init_app(app)
    jwt = JWTManager(app)
    mail.init_app(app)
    
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    cache.init_app(app)
    
    # Init celery
    celery_app = celery_init_app(app)

    # ----------------------
    # REGISTER BLUEPRINTS
    # ----------------------
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp, url_prefix='/patient')

    # ----------------------
    # HEALTH CHECK
    # ----------------------
    @app.route('/')
    def home():
        return jsonify({"msg": "HMS API Running 🚀"})

    # ----------------------
    # DB INIT + DEFAULT DATA
    # ----------------------
    with app.app_context():
        db.create_all()

        # create default admin
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin@admin.com',
                password='admin123',
                role='admin',
                name='Admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created")

    @app.errorhandler(422)
    def handle_error(err):
        headers = request.headers
        import sys
        print("422 ERROR DETECTED!", file=sys.stderr)
        print("Headers:", headers, file=sys.stderr)
        print("Error Description:", err.description, file=sys.stderr)
        return jsonify({"msg": str(err.description)}), 422

    return app


# ----------------------
# AUTO CREATE PATIENT PROFILE AFTER REGISTER
# ----------------------
from sqlalchemy import event

@event.listens_for(User, 'after_insert')
def create_patient_profile(mapper, connection, target):
    """
    Automatically create Patient profile when a patient user is created
    """
    if target.role == 'patient':
        connection.execute(
            Patient.__table__.insert().values(user_id=target.id)
        )


# ----------------------
# RUN APP
# ----------------------
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)