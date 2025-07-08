import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app

# Para Vercel
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

