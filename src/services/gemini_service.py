import google.generativeai as genai
import os
import json
from typing import Dict, Any

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key and self.api_key != 'your_gemini_api_key_here':
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            print("⚠️ GEMINI_API_KEY não configurada. Usando modo simulado.")
    
    def generate_diet_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera um plano alimentar personalizado usando Gemini AI
        """
        if not self.model:
            return self._generate_mock_plan(user_data)
        
        try:
            prompt = self._create_diet_prompt(user_data)
            response = self.model.generate_content(prompt)
            
            # Processa a resposta da IA
            plan = self._parse_ai_response(response.text, user_data)
            return plan
            
        except Exception as e:
            print(f"Erro ao gerar plano com Gemini: {e}")
            return self._generate_mock_plan(user_data)
    
    def _create_diet_prompt(self, user_data: Dict[str, Any]) -> str:
        """
        Cria o prompt para o Gemini baseado nos dados do usuário
        """
        prompt = f"""
        Você é um nutricionista especialista. Crie um plano alimentar personalizado com as seguintes especificações:

        DADOS DO USUÁRIO:
        - Nome: {user_data.get('name', 'Usuário')}
        - Idade: {user_data.get('age', 'Não informado')} anos
        - Peso: {user_data.get('weight', 'Não informado')} kg
        - Altura: {user_data.get('height', 'Não informado')} cm
        - Objetivo: {user_data.get('goal', 'Melhorar saúde')}
        - Orçamento por refeição: R$ {user_data.get('budget_per_meal', 25.00)}
        - Restrições alimentares: {user_data.get('dietary_restrictions', 'Nenhuma')}

        INSTRUÇÕES:
        1. Crie um plano para 1 dia com 4 refeições: café da manhã, almoço, jantar e lanche
        2. Respeite rigorosamente o orçamento por refeição
        3. Considere as restrições alimentares
        4. Inclua preços estimados dos alimentos (valores brasileiros realistas)
        5. Calcule calorias e macronutrientes aproximados
        6. Seja específico com quantidades e preparos

        FORMATO DE RESPOSTA (JSON):
        {{
            "breakfast": {{
                "description": "Descrição detalhada da refeição",
                "foods": ["alimento 1", "alimento 2"],
                "preparation": "Como preparar",
                "estimated_cost": 0.00,
                "calories": 0,
                "macros": {{"protein": 0, "carbs": 0, "fat": 0}}
            }},
            "lunch": {{
                "description": "Descrição detalhada da refeição",
                "foods": ["alimento 1", "alimento 2"],
                "preparation": "Como preparar",
                "estimated_cost": 0.00,
                "calories": 0,
                "macros": {{"protein": 0, "carbs": 0, "fat": 0}}
            }},
            "dinner": {{
                "description": "Descrição detalhada da refeição",
                "foods": ["alimento 1", "alimento 2"],
                "preparation": "Como preparar",
                "estimated_cost": 0.00,
                "calories": 0,
                "macros": {{"protein": 0, "carbs": 0, "fat": 0}}
            }},
            "snack": {{
                "description": "Descrição detalhada do lanche",
                "foods": ["alimento 1", "alimento 2"],
                "preparation": "Como preparar",
                "estimated_cost": 0.00,
                "calories": 0,
                "macros": {{"protein": 0, "carbs": 0, "fat": 0}}
            }},
            "total_cost": 0.00,
            "total_calories": 0,
            "total_macros": {{"protein": 0, "carbs": 0, "fat": 0}},
            "nutritionist_notes": "Observações importantes sobre o plano"
        }}

        Responda APENAS com o JSON, sem texto adicional.
        """
        return prompt
    
    def _parse_ai_response(self, response_text: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa a resposta da IA e garante que está no formato correto
        """
        try:
            # Remove possíveis marcadores de código
            clean_response = response_text.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            
            plan = json.loads(clean_response.strip())
            
            # Valida se tem os campos obrigatórios
            required_meals = ['breakfast', 'lunch', 'dinner', 'snack']
            for meal in required_meals:
                if meal not in plan:
                    raise ValueError(f"Refeição {meal} não encontrada")
            
            return plan
            
        except Exception as e:
            print(f"Erro ao processar resposta da IA: {e}")
            return self._generate_mock_plan(user_data)
    
    def _generate_mock_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera um plano simulado quando a IA não está disponível
        """
        budget = user_data.get('budget_per_meal', 25.00)
        goal = user_data.get('goal', 'Melhorar saúde')
        
        # Plano baseado no objetivo
        if 'perder peso' in goal.lower():
            return {
                "breakfast": {
                    "description": "Smoothie verde com proteína",
                    "foods": ["Espinafre (50g)", "Banana (1 unidade)", "Whey protein (30g)", "Água de coco (200ml)"],
                    "preparation": "Bater tudo no liquidificador até ficar homogêneo",
                    "estimated_cost": min(budget * 0.8, 20.00),
                    "calories": 280,
                    "macros": {"protein": 25, "carbs": 35, "fat": 3}
                },
                "lunch": {
                    "description": "Salmão grelhado com quinoa e vegetais",
                    "foods": ["Salmão (120g)", "Quinoa cozida (80g)", "Brócolis (100g)", "Cenoura (50g)"],
                    "preparation": "Grelhar o salmão, cozinhar quinoa e refogar vegetais",
                    "estimated_cost": budget,
                    "calories": 450,
                    "macros": {"protein": 35, "carbs": 40, "fat": 15}
                },
                "dinner": {
                    "description": "Frango grelhado com batata doce",
                    "foods": ["Peito de frango (100g)", "Batata doce assada (150g)", "Salada verde (100g)"],
                    "preparation": "Grelhar frango, assar batata doce, temperar salada",
                    "estimated_cost": min(budget * 0.9, 22.00),
                    "calories": 380,
                    "macros": {"protein": 30, "carbs": 45, "fat": 8}
                },
                "snack": {
                    "description": "Mix de castanhas e frutas",
                    "foods": ["Castanha do Pará (15g)", "Amêndoas (10g)", "Maçã (1 unidade)"],
                    "preparation": "Consumir as castanhas com a maçã",
                    "estimated_cost": min(budget * 0.6, 15.00),
                    "calories": 200,
                    "macros": {"protein": 6, "carbs": 25, "fat": 12}
                },
                "total_cost": budget * 3.2,
                "total_calories": 1310,
                "total_macros": {"protein": 96, "carbs": 145, "fat": 38},
                "nutritionist_notes": "Plano focado em perda de peso com déficit calórico controlado. Rico em proteínas para preservar massa muscular."
            }
        else:
            return {
                "breakfast": {
                    "description": "Ovos mexidos com aveia e frutas",
                    "foods": ["Ovos (2 unidades)", "Aveia (40g)", "Banana (1 unidade)", "Leite (200ml)"],
                    "preparation": "Mexer ovos, preparar mingau de aveia com leite e banana",
                    "estimated_cost": min(budget * 0.7, 18.00),
                    "calories": 420,
                    "macros": {"protein": 22, "carbs": 45, "fat": 15}
                },
                "lunch": {
                    "description": "Peito de frango com arroz integral",
                    "foods": ["Peito de frango (150g)", "Arroz integral (100g)", "Feijão (80g)", "Salada mista (100g)"],
                    "preparation": "Grelhar frango, cozinhar arroz e feijão, preparar salada",
                    "estimated_cost": budget,
                    "calories": 520,
                    "macros": {"protein": 40, "carbs": 55, "fat": 12}
                },
                "dinner": {
                    "description": "Carne magra com legumes",
                    "foods": ["Carne magra (120g)", "Batata (150g)", "Abobrinha (100g)", "Tomate (80g)"],
                    "preparation": "Grelhar carne, cozinhar batata, refogar legumes",
                    "estimated_cost": min(budget * 1.1, 28.00),
                    "calories": 480,
                    "macros": {"protein": 35, "carbs": 40, "fat": 18}
                },
                "snack": {
                    "description": "Iogurte com granola",
                    "foods": ["Iogurte natural (150g)", "Granola (30g)", "Mel (1 colher)"],
                    "preparation": "Misturar iogurte com granola e mel",
                    "estimated_cost": min(budget * 0.8, 20.00),
                    "calories": 280,
                    "macros": {"protein": 12, "carbs": 35, "fat": 8}
                },
                "total_cost": budget * 3.6,
                "total_calories": 1700,
                "total_macros": {"protein": 109, "carbs": 175, "fat": 53},
                "nutritionist_notes": "Plano equilibrado para manutenção ou ganho de peso saudável. Boa distribuição de macronutrientes."
            }

# Instância global do serviço
gemini_service = GeminiService()

