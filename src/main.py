import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa modelos e rotas
from src.models.nutriai_models import db
from src.routes.auth import auth_bp
from src.routes.diet_plans import diet_plans_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações de produção
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nutriai_flask_secret_key_2025')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'nutriai_super_secret_key_2025')

# CORS para produção
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173')
CORS(app, origins=cors_origins.split(','))

# JWT
jwt = JWTManager(app)

# Banco de dados - prioriza Neon
database_url = os.getenv('NEON_DATABASE_URL')
if database_url and database_url != 'your_neon_database_url_here':
    # Produção com Neon
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print("✅ Conectado ao banco Neon")
else:
    # Desenvolvimento com SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    print("⚠️ Usando SQLite local. Configure NEON_DATABASE_URL para produção.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa banco
db.init_app(app)

# Registra blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(diet_plans_bp, url_prefix='/api/diet-plans')

# Cria tabelas e dados iniciais
with app.app_context():
    db.create_all()
    
    # Cria usuários de exemplo apenas em desenvolvimento
    if not database_url or database_url == 'your_neon_database_url_here':
        from src.models.nutriai_models import User
        
        # Usuário exemplo
        if not User.query.filter_by(email='ana@email.com').first():
            user = User(
                email='ana@email.com',
                name='Ana Silva',
                user_type='user',
                age=34,
                weight=70.0,
                height=165.0,
                goal='Perder peso e controlar hipertensão',
                budget_per_meal=25.00,
                dietary_restrictions='Sem lactose'
            )
            user.set_password('123456')
            db.session.add(user)
        
        # Nutricionista exemplo
        if not User.query.filter_by(email='maria@nutricionista.com').first():
            nutritionist = User(
                email='maria@nutricionista.com',
                name='Dr. Maria Oliveira',
                user_type='nutritionist',
                crn_number='CRN-3 12345',
                specialization='Nutrição Clínica'
            )
            nutritionist.set_password('123456')
            db.session.add(nutritionist)
        
        try:
            db.session.commit()
        except:
            db.session.rollback()

# Rota para servir frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return {
                "message": "NutriAI Backend funcionando!",
                "status": "online",
                "frontend": "Coloque os arquivos do React na pasta static/",
                "api_docs": "/api/status"
            }, 200

# Rota de status da API
@app.route('/api/status')
def api_status():
    gemini_key = os.getenv('GEMINI_API_KEY')
    neon_url = os.getenv('NEON_DATABASE_URL')
    
    return {
        'status': 'online',
        'message': 'NutriAI API funcionando',
        'version': '1.0.0',
        'environment': os.getenv('FLASK_ENV', 'development'),
        'database': 'Neon' if (neon_url and neon_url != 'your_neon_database_url_here') else 'SQLite',
        'gemini_configured': bool(gemini_key and gemini_key != 'your_gemini_api_key_here'),
        'endpoints': {
            'auth': '/api/auth/login',
            'register': '/api/auth/register',
            'generate_plan': '/api/diet-plans/generate',
            'my_plans': '/api/diet-plans/my-plans'
        }
    }

# Para Vercel
app.wsgi_app = app.wsgi_app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') != 'production')

