from flask import Flask
from flask_sqlalchemy import SQLAlchemy #
from flask_cors import CORS
from flasgger import Swagger
from .config import Config  #
import os


db = SQLAlchemy()

def create_app():
    # 解决 "OMP: Error #15" 警告
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    app = Flask(__name__)

     # 应用配置
    app.config.from_object(Config)#
    
    CORS(app)  # 启用跨域支持
    swagger = Swagger(app) # 初始化 Flasgger
    
    db.init_app(app) #

    # 定义上传目录路径
    UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    print(f"上传目录: {UPLOADS_DIR}")
    
    # 注册蓝图
    from app.routes.api import api_bp
    from app.routes.video import video_bp
    from app.routes.config import config_bp
    from app.routes.face import face_bp
    from app.routes.main import main_bp  # 添加这行
    from .routes.auth import auth_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp)  # 添加这行
    app.register_blueprint(api_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(face_bp)
    
    return app 