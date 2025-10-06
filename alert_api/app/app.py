import os
import json
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from .alert_config import logger, alert_config


load_dotenv()

app = Flask(__name__)

app.config.update(
    PORT=int(os.getenv('ALERT_PORT', 5002)),
    DEBUG=os.getenv('DEBUG', 'false').lower() == 'true',
    SECRET_KEY=os.getenv('SECRET_KEY', 'alert-secret-key')
)


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "alertsdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")


def get_db_connection():
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {str(e)}")
        return None


def create_table():
    try:
        conn = get_db_connection()
        if not conn:
            return False

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS grafana_alerts (
                    id SERIAL PRIMARY KEY,
                    alert_name TEXT,
                    severity TEXT,
                    service TEXT,
                    state TEXT,
                    summary TEXT,
                    description TEXT,
                    message TEXT,
                    alert_type TEXT DEFAULT 'grafana',
                    status TEXT DEFAULT 'active',
                    metadata JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
        logger.info("Таблица grafana_alerts была создана/проверена")
        return True
    except Exception as e:
        logger.error(f"Ошибка создания таблицы: {str(e)}")
        return False


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Alert API is working fine"
    })


@app.route('/webhook/alert', methods=['POST'])
def webhook_alert():
    try:
        data = request.get_json()
        logger.info("Получен алерт")

        alerts = data.get("alerts", [])
        alerts_to_save = []

        for alert in alerts:
            labels = alert.get("labels", {})
            severity = labels.get("severity", "warning")
            state = alert.get("state", "unknown")
            alert_name = labels.get("alertname", "Unknown Alert")
            service = labels.get("service", "unknown")
            summary = alert.get("annotations", {}).get("summary", "")
            description = alert.get("annotations", {}).get("description", "")
            message = summary or description or "No message"

            alert_data = (
                alert_name,
                severity,
                service,
                state,
                summary,
                description,
                message,
                "grafana",
                "active",
                json.dumps({
                    "source": "grafana_webhook",
                    "labels": labels,
                    "annotations": alert.get("annotations", {}),
                    "startsAt": alert.get("startsAt"),
                    "endsAt": alert.get("endsAt")
                })
            )

            alerts_to_save.append(alert_data)

            alert_config.log_alert(severity, f"{alert_name}: {message}", "grafana")

        if alerts_to_save:
            conn = get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        execute_values(cur,
                            """
                            INSERT INTO grafana_alerts 
                            (alert_name, severity, service, state, summary, description, message, alert_type, status, metadata)
                            VALUES %s
                            """,
                            alerts_to_save
                        )
                    logger.info(f"Сохранено {len(alerts_to_save)} алертов в PostgreSQL")
                except Exception as e:
                    logger.error(f"Ошибка сохранения в БД: {str(e)}")
                    return jsonify({"error": "Ошибка сохранения в БД"}), 500
            else:
                logger.error("БД недоступна")
                return jsonify({"error": "База данных недоступна"}), 503

        return jsonify({
            "status": "received",
            "count": len(alerts_to_save)
        }), 200

    except Exception as e:
        logger.error(f"Ошибка при обработке алерта: {str(e)}")
        return jsonify({"error": "Ошибка обработки webhook"}), 500


if __name__ == '__main__':

    if create_table():
        print("Таблица grafana_alerts была создана/проверена")
    else:
        print("Ошибка при создании таблицы")

    logger.info("Alert API запущен")
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
