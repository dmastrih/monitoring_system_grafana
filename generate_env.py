import secrets
import string


def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_secret_key(length=32):
    return secrets.token_urlsafe(length)


def main():
    minio_password = generate_password(16)
    postgres_password = generate_password(16)
    secret_key = generate_secret_key(32)

    env_content = f"""
# Конфигурация приложения logs_app
LOGS_APP_PORT=5001
LOGS_APP_DEBUG=false
LOGS_APP_SECRET_KEY={secret_key}
LOGS_APP_LOG_LEVEL=INFO
LOGS_APP_LOG_DIR=logs

# Конфигурация приложения alert_api
ALERT_API_PORT=5002
ALERT_API_DEBUG=false
ALERT_API_SECRET_KEY={secret_key}
ALERT_API_LOG_LEVEL=INFO
ALERT_API_LOG_DIR=logs

# Конфигурация MinIO (БЕЗОПАСНЫЕ ПАРОЛИ)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD={minio_password}

# Конфигурация PostgreSQL
POSTGRES_DB=alertsdb
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD={postgres_password}

# Общие настройки
SECRET_KEY={secret_key}
DEBUG=false
LOG_LEVEL=INFO
"""

    with open('.env', 'w') as f:
        f.write(env_content)


if __name__ == "__main__":
    main()
