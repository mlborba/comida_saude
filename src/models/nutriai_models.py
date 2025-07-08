from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'user' ou 'nutritionist'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos específicos do usuário
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    goal = db.Column(db.Text)
    budget_per_meal = db.Column(db.Float)
    dietary_restrictions = db.Column(db.Text)
    
    # Campos específicos do nutricionista
    crn_number = db.Column(db.String(20))  # Número do CRN
    specialization = db.Column(db.String(100))
    
    # Relacionamentos
    diet_plans = db.relationship('DietPlan', backref='user', lazy=True, foreign_keys='DietPlan.user_id')
    validated_plans = db.relationship('DietPlan', backref='nutritionist', lazy=True, foreign_keys='DietPlan.nutritionist_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'user_type': self.user_type,
            'age': self.age,
            'weight': self.weight,
            'height': self.height,
            'goal': self.goal,
            'budget_per_meal': self.budget_per_meal,
            'dietary_restrictions': self.dietary_restrictions,
            'crn_number': self.crn_number,
            'specialization': self.specialization,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DietPlan(db.Model):
    __tablename__ = 'diet_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nutritionist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Dados do plano
    goal = db.Column(db.Text, nullable=False)
    budget_per_meal = db.Column(db.Float, nullable=False)
    dietary_restrictions = db.Column(db.Text)
    
    # Plano gerado pela IA (JSON)
    ai_plan = db.Column(db.Text, nullable=False)  # JSON string
    
    # Status e validação
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    nutritionist_feedback = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated_at = db.Column(db.DateTime)
    
    def get_ai_plan(self):
        """Retorna o plano da IA como dicionário"""
        try:
            return json.loads(self.ai_plan)
        except:
            return {}
    
    def set_ai_plan(self, plan_dict):
        """Define o plano da IA a partir de um dicionário"""
        self.ai_plan = json.dumps(plan_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nutritionist_id': self.nutritionist_id,
            'goal': self.goal,
            'budget_per_meal': self.budget_per_meal,
            'dietary_restrictions': self.dietary_restrictions,
            'ai_plan': self.get_ai_plan(),
            'status': self.status,
            'nutritionist_feedback': self.nutritionist_feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'user_name': self.user.name if self.user else None,
            'nutritionist_name': self.nutritionist.name if self.nutritionist else None
        }

class FoodPrice(db.Model):
    __tablename__ = 'food_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, g, unidade, etc
    supermarket = db.Column(db.String(50))
    location = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'food_name': self.food_name,
            'price_per_unit': self.price_per_unit,
            'unit': self.unit,
            'supermarket': self.supermarket,
            'location': self.location,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)  # 'smart', 'plus'
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired
    price = db.Column(db.Float, nullable=False)
    
    # Datas
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    user = db.relationship('User', backref='subscriptions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'status': self.status,
            'price': self.price,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

