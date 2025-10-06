import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from .logger_config import logger, logger_config


load_dotenv()


app = Flask(__name__, template_folder='templates', static_folder='static')


app.config.update(
    PORT=int(os.getenv('PORT', 5001)),
    DEBUG=os.getenv('DEBUG', 'false').lower() == 'true',
    SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key')
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/log/<level>', methods=['POST'])
def log_level(level):
    try:
        data = request.get_json() or {}
        message = data.get('message', f"{level.upper()} level log")

        logger_config.log_with_timestamp(level, message)

        return jsonify({"message": f"Записан {level.upper()} лог"})

    except Exception as e:
        logger.error(f"Ошибка при записи лога {level}: {str(e)}")
        return jsonify({"error": "Ошибка при записи лога"}), 500


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "The app is working fine"
    })


if __name__ == '__main__':
    print("Запуск приложения")
    print(f"Логи сохраняются в: {logger_config.log_dir}/app.log")
    print("Откройте http://localhost:5001 в браузере")
    logger.info("Приложение запущено")
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
