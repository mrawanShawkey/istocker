from pathlib import Path
import sys

ROOT_DIR = Path().resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from api.app import create_app

flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', debug=True)