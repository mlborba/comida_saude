import os
import sys

# Adiciona o diretório atual ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.main import app
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    # Fallback simples
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return {"message": "NutriAI Backend - Import Error", "error": str(e)}
    
    @app.route('/api/status')
    def status():
        return {"status": "error", "message": "Import failed", "error": str(e)}

if __name__ == "__main__":
    app.run()

