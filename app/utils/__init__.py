"""Utility functions for the application."""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Tuple

import psycopg2
import redis
from flask import jsonify, current_app
from psycopg2.extensions import connection as PgConnection

def get_db_connection() -> PgConnection:
    """Get a database connection."""
    try:
        conn = psycopg2.connect(
            dbname=current_app.config.get('POSTGRES_DB'),
            user=current_app.config.get('POSTGRES_USER'),
            password=current_app.config.get('POSTGRES_PASSWORD'),
            host=current_app.config.get('POSTGRES_HOST', 'db'),
            port=current_app.config.get('POSTGRES_PORT', 5432)
        )
        return conn
    except Exception as e:
        current_app.logger.error(f"Database connection error: {str(e)}")
        raise

def get_redis_connection() -> redis.Redis:
    """Get a Redis connection."""
    try:
        return redis.Redis(
            host=current_app.config.get('REDIS_HOST', 'redis'),
            port=current_app.config.get('REDIS_PORT', 6379),
            password=current_app.config.get('REDIS_PASSWORD', ''),
            db=0,
            decode_responses=True
        )
    except Exception as e:
        current_app.logger.error(f"Redis connection error: {str(e)}")
        raise

def check_database_health() -> Tuple[bool, str]:
    """Check if the database is healthy."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            if result and result[0] == 1:
                return True, "Database is healthy"
        return False, "Database query failed"
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()

def check_redis_health() -> Tuple[bool, str]:
    """Check if Redis is healthy."""
    try:
        r = get_redis_connection()
        return r.ping(), "Redis is healthy"
    except Exception as e:
        return False, f"Redis error: {str(e)}"

def check_health() -> Dict[str, Any]:
    """Check the health of all services."""
    services = {
        'database': check_database_health(),
        'redis': check_redis_health(),
    }
    
    status = 'healthy'
    for service, (healthy, _) in services.items():
        if not healthy:
            status = 'unhealthy'
            break
    
    return {
        'status': status,
        'services': {
            service: {
                'status': 'healthy' if healthy else 'unhealthy',
                'message': message
            } for service, (healthy, message) in services.items()
        }
    }

def setup_logging(app):
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Set the log level
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # Configure the root logger
    app.logger.handlers.clear()
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(log_level)
    
    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    console_handler.setLevel(log_level)
    
    # Add handlers to the application's logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Set SQLAlchemy logging
    if app.config.get('SQLALCHEMY_ECHO'):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Disable logging for some noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.logger.info('Logging configured successfully')
