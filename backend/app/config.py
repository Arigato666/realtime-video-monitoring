import os

# 获取项目根目录的绝对路径
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    
   
#以下
    # MySQL 数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'Really0733251'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'realtime_monitoring'
    MYSQL_CHARSET = os.environ.get('MYSQL_CHARSET') or 'utf8mb4'
    
    # 构建 SQLAlchemy URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset={MYSQL_CHARSET}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 危险区域配置（这些将被路由配置覆盖）
    DANGER_ZONE = []
    SAFETY_DISTANCE = 1.0
    LOITERING_THRESHOLD = 10