from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.nutriai_models import db, User, DietPlan
from src.services.gemini_service import gemini_service
from datetime import datetime

diet_plans_bp = Blueprint('diet_plans', __name__)

@diet_plans_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_diet_plan():
    """Gera um novo plano alimentar usando IA"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.user_type != 'user':
            return jsonify({'error': 'Apenas usuários podem gerar planos'}), 403
        
        data = request.get_json()
        
        # Dados para a IA
        user_data = {
            'name': user.name,
            'age': user.age,
            'weight': user.weight,
            'height': user.height,
            'goal': data.get('goal', user.goal),
            'budget_per_meal': data.get('budget_per_meal', user.budget_per_meal),
            'dietary_restrictions': data.get('dietary_restrictions', user.dietary_restrictions)
        }
        
        # Gera plano com IA
        ai_plan = gemini_service.generate_diet_plan(user_data)
        
        # Salva no banco
        diet_plan = DietPlan(
            user_id=user_id,
            goal=user_data['goal'],
            budget_per_meal=user_data['budget_per_meal'],
            dietary_restrictions=user_data['dietary_restrictions'],
            status='pending'
        )
        diet_plan.set_ai_plan(ai_plan)
        
        db.session.add(diet_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plano gerado com sucesso',
            'diet_plan': diet_plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@diet_plans_bp.route('/my-plans', methods=['GET'])
@jwt_required()
def get_my_plans():
    """Retorna planos do usuário atual"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.user_type == 'user':
            # Usuário vê seus próprios planos
            plans = DietPlan.query.filter_by(user_id=user_id).order_by(DietPlan.created_at.desc()).all()
        elif user.user_type == 'nutritionist':
            # Nutricionista vê planos pendentes para validar
            plans = DietPlan.query.filter_by(status='pending').order_by(DietPlan.created_at.desc()).all()
        else:
            return jsonify({'error': 'Tipo de usuário inválido'}), 403
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diet_plans_bp.route('/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_plan_details(plan_id):
    """Retorna detalhes de um plano específico"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        plan = DietPlan.query.get(plan_id)
        
        if not plan:
            return jsonify({'error': 'Plano não encontrado'}), 404
        
        # Verifica permissões
        if user.user_type == 'user' and plan.user_id != user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        elif user.user_type == 'nutritionist' and plan.status != 'pending':
            # Nutricionista só pode ver planos pendentes ou que ele validou
            if plan.nutritionist_id != user_id:
                return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify({'plan': plan.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diet_plans_bp.route('/<int:plan_id>/validate', methods=['POST'])
@jwt_required()
def validate_plan(plan_id):
    """Valida um plano (aprovar ou rejeitar)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.user_type != 'nutritionist':
            return jsonify({'error': 'Apenas nutricionistas podem validar planos'}), 403
        
        plan = DietPlan.query.get(plan_id)
        
        if not plan:
            return jsonify({'error': 'Plano não encontrado'}), 404
        
        if plan.status != 'pending':
            return jsonify({'error': 'Plano já foi validado'}), 400
        
        data = request.get_json()
        action = data.get('action')  # 'approve' ou 'reject'
        feedback = data.get('feedback', '')
        
        if action not in ['approve', 'reject']:
            return jsonify({'error': 'Ação deve ser approve ou reject'}), 400
        
        # Atualiza plano
        plan.status = 'approved' if action == 'approve' else 'rejected'
        plan.nutritionist_id = user_id
        plan.nutritionist_feedback = feedback
        plan.validated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Plano {"aprovado" if action == "approve" else "rejeitado"} com sucesso',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@diet_plans_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_plans():
    """Retorna planos pendentes para nutricionistas"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.user_type != 'nutritionist':
            return jsonify({'error': 'Apenas nutricionistas podem acessar'}), 403
        
        plans = DietPlan.query.filter_by(status='pending').order_by(DietPlan.created_at.desc()).all()
        
        return jsonify({
            'pending_plans': [plan.to_dict() for plan in plans],
            'count': len(plans)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diet_plans_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_nutritionist_stats():
    """Retorna estatísticas para nutricionistas"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.user_type != 'nutritionist':
            return jsonify({'error': 'Apenas nutricionistas podem acessar'}), 403
        
        # Estatísticas
        total_validated = DietPlan.query.filter_by(nutritionist_id=user_id).count()
        approved = DietPlan.query.filter_by(nutritionist_id=user_id, status='approved').count()
        rejected = DietPlan.query.filter_by(nutritionist_id=user_id, status='rejected').count()
        pending = DietPlan.query.filter_by(status='pending').count()
        
        # Pacientes únicos
        unique_patients = db.session.query(DietPlan.user_id).filter_by(nutritionist_id=user_id).distinct().count()
        
        # Taxa de aprovação
        approval_rate = (approved / total_validated * 100) if total_validated > 0 else 0
        
        return jsonify({
            'stats': {
                'total_validated': total_validated,
                'approved': approved,
                'rejected': rejected,
                'pending': pending,
                'unique_patients': unique_patients,
                'approval_rate': round(approval_rate, 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

