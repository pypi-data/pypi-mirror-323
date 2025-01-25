def get_server_contant():
   return '''from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from config.logging import log_errors
from routes.api import router
import traceback

app = FastAPI()
app.include_router(router=router)


@app.middleware("http")
async def log_request_errors(request: Request, call_next):
    return await log_errors(request=request, call_next=call_next)'''


def get_manage_contant():
    return '''from fpcli import app

if __name__ == "__main__":
    app()'''


def get_database_contant():
    return '''from pydantic import BaseSettings, Field
from typing import Optional

class DatabaseSettings(BaseSettings):
    # Default Database Connection
    default: str = Field("mysql", env="DB_CONNECTION")

    # SQLite Configuration
    sqlite_url: Optional[str] = Field(None, env="DATABASE_URL")
    sqlite_database: str = Field("./database.sqlite", env="DB_DATABASE")
    sqlite_foreign_keys: bool = Field(True, env="DB_FOREIGN_KEYS")

    # MySQL Configuration
    mysql_url: Optional[str] = Field(None, env="DATABASE_URL")
    mysql_host: str = Field("127.0.0.1", env="DB_HOST")
    mysql_port: int = Field(3306, env="DB_PORT")
    mysql_database: str = Field("forge", env="DB_DATABASE")
    mysql_username: str = Field("forge", env="DB_USERNAME")
    mysql_password: str = Field("", env="DB_PASSWORD")
    mysql_charset: str = "utf8mb4"
    mysql_collation: str = "utf8mb4_unicode_ci"
    mysql_ssl_ca: Optional[str] = Field(None, env="MYSQL_ATTR_SSL_CA")

    # PostgreSQL Configuration
    pgsql_url: Optional[str] = Field(None, env="DATABASE_URL")
    pgsql_host: str = Field("127.0.0.1", env="DB_HOST")
    pgsql_port: int = Field(5432, env="DB_PORT")
    pgsql_database: str = Field("forge", env="DB_DATABASE")
    pgsql_username: str = Field("forge", env="DB_USERNAME")
    pgsql_password: str = Field("", env="DB_PASSWORD")
    pgsql_charset: str = "utf8"
    pgsql_sslmode: str = Field("prefer", env="DB_SSLMODE")

    # SQL Server Configuration
    sqlsrv_url: Optional[str] = Field(None, env="DATABASE_URL")
    sqlsrv_host: str = Field("localhost", env="DB_HOST")
    sqlsrv_port: int = Field(1433, env="DB_PORT")
    sqlsrv_database: str = Field("forge", env="DB_DATABASE")
    sqlsrv_username: str = Field("forge", env="DB_USERNAME")
    sqlsrv_password: str = Field("", env="DB_PASSWORD")
    sqlsrv_charset: str = "utf8"

    # Redis Configuration
    redis_client: str = Field("redis", env="REDIS_CLIENT")
    redis_cluster: str = Field("redis", env="REDIS_CLUSTER")
    redis_prefix: str = Field("fastapi_database", env="REDIS_PREFIX")
    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_default_db: int = Field(0, env="REDIS_DB")
    redis_cache_db: int = Field(1, env="REDIS_CACHE_DB")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Load settings
settings = DatabaseSettings()

# Example usage:
if __name__ == "__main__":
    print("Default Database:", settings.default)
    print("MySQL Host:", settings.mysql_host)
    print("Redis Host:", settings.redis_host)
'''

def get_loging_contant():
    return'''# Logging Configuration
import logging
import os
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import  Request,HTTPException 

import traceback


def setup_logger(
    logger_name="app",
    log_folder="storage/logs",
    log_file="app.log",
    log_level=logging.DEBUG,
):
    """
    Sets up a logger with both file and console handlers.

    Args:
        logger_name (str): The name of the logger.
        log_folder (str): The folder where the log file will be stored.
        log_file (str): The name of the log file.
        log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Ensure the storage folder exists
    os.makedirs(log_folder, exist_ok=True)
    log_file_path = os.path.join(log_folder, log_file)

    # Create a file handler and set the level
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(log_level)

    # Create a console handler and set the level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

error_logger=setup_logger(logger_name="error",log_file="error.log")
async def log_errors(request:Request, call_next):
    """
    Middleware to log syntax errors and request data for unhandled exceptions.
    """
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_ex:
        # Log HTTP Exceptions separately
        error_logger.error(
            f"HTTPException: {http_ex.detail}"
            f"Path: {request.url.path}"
            f"Method: {request.method}"
            f"Headers: {dict(request.headers)}"
        )
        raise
    except Exception as ex:
        # Capture and log full stack trace for unhandled exceptions
        error_logger.error(
            f"Unhandled Exception:"
            f"Path: {request.url.path}"
            f"Method: {request.method}"
            f"Headers: {dict(request.headers)}"
            f"Body: {await request.body()}"
            f"Error: {str(ex)}"
            f"Traceback:{traceback.format_exc()}"
        )
        return JSONResponse(
            status_code=500,
            content={"message": "An internal server error occurred."},
        )'''


def get_welcome_controller_contant():
    return ''' 
#Welcome Controller   
from fastapi import Request

class WelcomeController:

    async def index(self):
        """
        Get all the data.

        Returns:
            str: A message indicating that all data is being fetched.
        """
        return {"message":"Welcome to FastApi with Fpcli interface" }'''

def get_urls_contant():
    return '''from fastapi import APIRouter
from .controllers.welcome_controller import WelcomeController


app_router = APIRouter()

app_router.add_api_route("/", WelcomeController().index, methods=["GET"] )
 '''

def get_api_contant():
    return '''from fastapi import APIRouter
from app.http.v1.urls import app_router

router = APIRouter()

router.include_router(router=app_router) '''

def get_console_content():
    return '''from fpcli import app
@app.command()
def test():
    print("test fucntion is running")
'''

def get_helper_utilities_content():
    return '''async def response(data, message: str, success: bool = True):
    return {"data": data, "message": message, "success": success}'''

def get_gitignore_contant():
    return'''__pycache__/
uv.lock
storage/logs
mongodb_data
.vscode
.ruff_cache
.env
env
venv
.venv
.env
envs
virtualenv
python_env
pyenv
.virtualenv
myenv
project_env
dev_env
test_env
local_env
python3_env
backend_env
flask_env
django_env
fast_env
web_env
api_env
sandbox_env
tool_env
lib_env
dependencies_env
'''

def get_env_file_content():
  return  '''# FastAPI settings
APP_NAME=FastAPIApp
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost

# Logging settings (You can configure logging in FastAPI as needed)
LOG_CHANNEL=stack
LOG_LEVEL=debug'''

def get_database_env_content():
  return  {"mysql":'''
           
# Mysql Database connection settings 
DB_CONNECTION=mysql
DB_PORT=3306'''+comman_database_file_content(),

'postgresql': '''

# Postgress Database connection settings 
DB_CONNECTION=postgress
DB_PORT=5432'''+comman_database_file_content(),

'sqlite':'''

# SQLite database settings
DB_CONNECTION=sqlite
DB_PATH=./sqlite_database.db''',

'mongodb':'''

# Mongodb Database connection settings 
DB_CONNECTION=mongodb
DB_PORT=27017'''+comman_database_file_content()


}
    

def comman_database_file_content():
   return '''DB_HOST=127.0.0.1
DB_DATABASE=fastapi_db
DB_USERNAME=root
DB_PASSWORD='''




