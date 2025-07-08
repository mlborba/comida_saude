from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.nutriai_models import db, User
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        data = request.get_json()
        
        # Validação básica
        required_fields = ['email', 'password', 'name', 'user_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verifica se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Cria novo usuário
        user = User(
            email=data['email'],
            name=data['name'],
            user_type=data['user_type']
        )
        user.set_password(data['password'])
        
        # Campos específicos do usuário
        if data['user_type'] == 'user':
            user.age = data.get('age')
            user.weight = data.get('weight')
            user.height = data.get('height')
            user.goal = data.get('goal')
            user.budget_per_meal = data.get('budget_per_meal', 25.00)
            user.dietary_restrictions = data.get('dietary_restrictions')
        
        # Campos específicos do nutricionista
        elif data['user_type'] == 'nutritionist':
            user.crn_number = data.get('crn_number')
            user.specialization = data.get('specialization')
        
        db.session.add(user)
        db.session.commit()
        
        # Cria token de acesso
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Faz login do usuário"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Busca usuário
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        # Cria token de acesso
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Retorna dados do usuário atual"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Atualiza perfil do usuário"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualiza campos básicos
        if 'name' in data:
            user.name = data['name']
        
        # Atualiza campos específicos do usuário
        if user.user_type == 'user':
            if 'age' in data:
                user.age = data['age']
            if 'weight' in data:
                user.weight = data['weight']
            if 'height' in data:
                user.height = data['height']
            if 'goal' in data:
                user.goal = data['goal']
            if 'budget_per_meal' in data:
                user.budget_per_meal = data['budget_per_meal']
            if 'dietary_restrictions' in data:
                user.dietary_restrictions = data['dietary_restrictions']
        
        # Atualiza campos específicos do nutricionista
        elif user.user_type == 'nutritionist':
            if 'crn_number' in data:
                user.crn_number = data['crn_number']
            if 'specialization' in data:
                user.specialization = data['specialization']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

