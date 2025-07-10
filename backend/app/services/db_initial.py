import mysql.connector
from app.config import Config
from app import db
from app.models import User

def init_database():
    """初始化数据库和表结构"""
    try:
        # 创建数据库连接
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} DEFAULT CHARSET {Config.MYSQL_CHARSET}")
        cursor.execute(f"USE {Config.MYSQL_DB}")
        
        # 创建车站信息表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            station_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '车站ID(UUID)',
            station_name VARCHAR(100) NOT NULL COMMENT '车站名称',
            city VARCHAR(50) NOT NULL COMMENT '所在城市',
            address TEXT COMMENT '详细地址',
            contact_number VARCHAR(20) COMMENT '车站联系电话'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建车站位置表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            location_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '位置ID(UUID)',
            location_name VARCHAR(100) NOT NULL COMMENT '位置名称',
            location_type VARCHAR(50) NOT NULL COMMENT '位置类型(entrance/security_check/waiting_hall/platform)',
            station_id VARCHAR(36) NOT NULL COMMENT '所属车站ID',
            floor_number INT COMMENT '楼层号',
            coordinates VARCHAR(100) COMMENT '坐标信息(GPS或室内坐标)',
            FOREIGN KEY (station_id) REFERENCES stations(station_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建摄像头设备表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            camera_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '摄像头ID(UUID)',
            location_id VARCHAR(36) NOT NULL COMMENT '安装位置ID',
            camera_type VARCHAR(50) NOT NULL COMMENT '摄像头类型(face_recognition/behavior_monitoring)',
            model_number VARCHAR(50) COMMENT '设备型号',
            ip_address VARCHAR(50) COMMENT 'IP地址',
            installation_date DATE COMMENT '安装日期',
            last_maintenance_date DATE COMMENT '最后维护日期',
            status VARCHAR(20) DEFAULT 'active' COMMENT '设备状态(active/inactive/maintenance)',
            FOREIGN KEY (location_id) REFERENCES locations(location_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建乘客表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            passenger_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '乘客唯一标识符(UUID)',
            id_card_number VARCHAR(18) UNIQUE COMMENT '身份证号码',
            name VARCHAR(50) NOT NULL COMMENT '乘客姓名',
            gender CHAR(1) COMMENT '性别(M-男, F-女)',
            birth_date DATE COMMENT '出生日期',
            phone_number VARCHAR(20) COMMENT '联系电话',
            registered_face_feature JSON COMMENT '人脸特征向量(JSON格式)',
            registration_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
            blacklist_flag BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否在黑名单中',
            blacklist_reason TEXT COMMENT '加入黑名单的原因',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # 创建危险行为分类表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dangerous_behaviors (
            behavior_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '行为类型ID(UUID)',
            behavior_name VARCHAR(100) NOT NULL COMMENT '行为名称',
            description TEXT COMMENT '行为详细描述',
            default_risk_level VARCHAR(20) NOT NULL COMMENT '默认风险等级(low/medium/high)',
            model_version VARCHAR(50) COMMENT '检测模型版本'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建安保人员表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_staff (
            staff_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '安保人员ID(UUID)',
            name VARCHAR(50) NOT NULL COMMENT '姓名',
            badge_number VARCHAR(20) UNIQUE NOT NULL COMMENT '工牌编号',
            department VARCHAR(50) COMMENT '所属部门',
            contact_number VARCHAR(20) COMMENT '联系电话',
            shift_schedule TEXT COMMENT '班次安排(JSON格式)',
            access_level INT DEFAULT 1 COMMENT '系统访问权限级别(1-普通,2-主管,3-管理员)'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建人脸识别记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_recognition_logs (
            recognition_id VARCHAR(36) PRIMARY KEY COMMENT '识别记录ID(UUID)',
            passenger_id VARCHAR(36) COMMENT '匹配到的乘客ID',
            camera_id VARCHAR(36) NOT NULL COMMENT '摄像头ID',
            recognition_time DATETIME NOT NULL COMMENT '识别时间',
            confidence_score FLOAT COMMENT '识别置信度(0-1)',
            matched_face_feature BLOB COMMENT '识别时提取的人脸特征',
            location_id VARCHAR(36) NOT NULL COMMENT '识别位置ID',
            image_path VARCHAR(255) COMMENT '抓拍图像存储路径',
            FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
            FOREIGN KEY (location_id) REFERENCES locations(location_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建行为检测记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS behavior_detection_logs (
            detection_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '行为检测ID(UUID)',
            passenger_id VARCHAR(36) COMMENT '关联乘客ID',
            camera_id VARCHAR(36) NOT NULL COMMENT '摄像头ID',
            detection_time DATETIME NOT NULL COMMENT '检测时间',
            behavior_type VARCHAR(50) NOT NULL COMMENT '检测到的行为类型',
            confidence_score FLOAT COMMENT '检测置信度(0-1)',
            risk_level VARCHAR(20) COMMENT '风险等级(low/medium/high)',
            location_id VARCHAR(36) NOT NULL COMMENT '检测位置ID',
            video_clip_path VARCHAR(255) COMMENT '视频片段存储路径',
            status VARCHAR(20) DEFAULT 'pending' COMMENT '处理状态(pending/reviewed/confirmed/false_alarm)',
            handled_by VARCHAR(36) COMMENT '处理人员ID',
            handled_time DATETIME COMMENT '处理时间',
            notes TEXT COMMENT '处理备注',
            FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
            FOREIGN KEY (camera_id) REFERENCES cameras(camera_id),
            FOREIGN KEY (location_id) REFERENCES locations(location_id),
            FOREIGN KEY (handled_by) REFERENCES security_staff(staff_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 创建报警记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '报警ID(UUID)',
            detection_id VARCHAR(36) COMMENT '关联的行为检测ID',
            alert_time DATETIME NOT NULL COMMENT '报警时间',
            alert_type VARCHAR(50) NOT NULL COMMENT '报警类型(blacklist_match/high_risk_behavior)',
            severity VARCHAR(20) NOT NULL COMMENT '严重程度(critical/high/medium/low)',
            status VARCHAR(20) DEFAULT 'unprocessed' COMMENT '处理状态(unprocessed/processing/resolved)',
            assigned_to VARCHAR(36) COMMENT '分配给的安全人员ID',
            resolution TEXT COMMENT '处理结果描述',
            resolved_time DATETIME COMMENT '解决时间',
            FOREIGN KEY (detection_id) REFERENCES behavior_detection_logs(detection_id),
            FOREIGN KEY (assigned_to) REFERENCES security_staff(staff_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)


       
        # 创建系统日志表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            log_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '日志ID(UUID)',
            log_time DATETIME NOT NULL COMMENT '日志时间',
            log_level VARCHAR(20) NOT NULL COMMENT '日志级别(INFO/WARNING/ERROR/CRITICAL)',
            module VARCHAR(50) NOT NULL COMMENT '模块名称',
            message TEXT NOT NULL COMMENT '日志消息',
            details TEXT COMMENT '详细内容',
            user_id VARCHAR(36) COMMENT '操作用户ID'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    
        # 新增用户表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '用户唯一标识符(UUID)',
            username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
            password VARCHAR(100) NOT NULL COMMENT '密码哈希',
            email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            last_login TIMESTAMP NULL COMMENT '最后登录时间',
            is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '账户是否激活'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        

        print("✅ 数据库表创建成功!")
        # 创建初始管理员用户（如果不存在）
        if not User.query.filter_by(username='admin').first():
            admin = User(
                user_id=str(uuid.uuid4()),
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@example.com'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ 管理员用户创建成功")

        return True
        
    except mysql.connector.Error as err:
        print(f"❌ 数据库初始化失败: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()