from flask import Blueprint, request, jsonify
import numpy as np
from app.services import system_state
from app.services.danger_zone import (
    DANGER_ZONE, SAFETY_DISTANCE, LOITERING_THRESHOLD,
    save_danger_zone_config
)
from app.utils import logger  # 添加日志记录器

# 创建配置蓝图 - 更新为使用新的蓝图命名约定
bp = Blueprint('config', __name__, url_prefix='/api/config')

# 危险区域编辑模式标志
edit_mode = False

@bp.route("/", methods=["GET"])
def get_config():
    """获取配置信息端点
    ---
    tags:
      - 配置管理
    responses:
      200:
        description: 返回当前系统配置.
        schema:
          type: object
          properties:
            danger_zone:
              type: array
              items:
                type: array
                items:
                  type: integer
              description: 危险区域的多边形顶点坐标.
            safety_distance:
              type: integer
              description: 安全距离阈值.
            loitering_threshold:
              type: number
              description: 停留时间警报阈值.
    """
    # 添加日志记录
    logger.info("获取系统配置信息")
    
    try:
        # 将numpy数组转换为列表
        danger_zone_list = DANGER_ZONE.tolist()
    except AttributeError:
        # 如果DANGER_ZONE已经是列表
        danger_zone_list = DANGER_ZONE
        
    return jsonify({
        "danger_zone": danger_zone_list,
        "safety_distance": SAFETY_DISTANCE,
        "loitering_threshold": LOITERING_THRESHOLD
    })

@bp.route("/danger_zone", methods=["POST"])
def update_danger_zone():
    """更新危险区域坐标端点
    ---
    tags:
      - 配置管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            danger_zone:
              type: array
              items:
                type: array
                items:
                  type: integer
              description: "危险区域的新坐标点列表. e.g., [[100, 100], [200, 100], [200, 200], [100, 200]]"
    responses:
      200:
        description: 危险区域更新成功.
      400:
        description: 无效的坐标数据.
    """
    global DANGER_ZONE
    data = request.json
    new_zone = data.get('danger_zone')
    
    # 添加日志记录
    logger.info(f"更新危险区域配置: {new_zone}")
    
    if new_zone and len(new_zone) >= 3:  # 确保至少有3个点形成多边形
        try:
            # 转换为numpy数组
            DANGER_ZONE = np.array(new_zone, np.int32)
            
            # 保存到配置文件
            if save_danger_zone_config(DANGER_ZONE, SAFETY_DISTANCE, LOITERING_THRESHOLD):
                return jsonify({
                    "status": "success", 
                    "message": "危险区域更新并保存成功",
                    "danger_zone": DANGER_ZONE.tolist()
                })
            else:
                return jsonify({
                    "status": "warning", 
                    "message": "危险区域更新但保存到文件失败",
                    "danger_zone": DANGER_ZONE.tolist()
                })
        except Exception as e:
            logger.error(f"更新危险区域时出错: {str(e)}")
            return jsonify({
                "status": "error", 
                "message": f"处理危险区域时出错: {str(e)}"
            }), 500
    else:
        logger.warning("无效的危险区域坐标数据")
        return jsonify({
            "status": "error", 
            "message": "无效的危险区域坐标数据，至少需要3个点"
        }), 400

@bp.route("/thresholds", methods=["POST"])
def update_thresholds():
    """更新安全距离和停留时间阈值端点
    ---
    tags:
      - 配置管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            safety_distance:
              type: integer
              description: 新的安全距离.
            loitering_threshold:
              type: number
              description: 新的停留阈值.
    responses:
      200:
        description: 阈值更新成功.
      400:
        description: 无效的输入值.
    """
    global SAFETY_DISTANCE, LOITERING_THRESHOLD
    data = request.json
    
    # 添加日志记录
    logger.info(f"更新阈值配置: {data}")
    
    safety_distance = data.get('safety_distance')
    loitering_threshold = data.get('loitering_threshold')
    
    updated = False
    
    if safety_distance is not None:
        try:
            SAFETY_DISTANCE = int(safety_distance)
            updated = True
        except ValueError:
            logger.error("安全距离值无效")
            return jsonify({
                "status": "error", 
                "message": "安全距离值无效"
            }), 400
            
    if loitering_threshold is not None:
        try:
            LOITERING_THRESHOLD = float(loitering_threshold)
            updated = True
        except ValueError:
            logger.error("停留时间阈值无效")
            return jsonify({
                "status": "error", 
                "message": "停留时间阈值无效"
            }), 400
    
    if updated:
        # 保存到配置文件
        try:
            save_danger_zone_config(DANGER_ZONE, SAFETY_DISTANCE, LOITERING_THRESHOLD)
            return jsonify({
                "status": "success", 
                "message": "阈值更新并保存成功",
                "safety_distance": SAFETY_DISTANCE,
                "loitering_threshold": LOITERING_THRESHOLD
            })
        except Exception as e:
            logger.error(f"保存阈值配置时出错: {str(e)}")
            return jsonify({
                "status": "warning", 
                "message": "阈值更新但保存到文件失败",
                "safety_distance": SAFETY_DISTANCE,
                "loitering_threshold": LOITERING_THRESHOLD
            })
    else:
        logger.warning("未提供有效的阈值更新数据")
        return jsonify({
            "status": "info", 
            "message": "未提供有效的阈值更新数据"
        })

@bp.route("/edit_mode", methods=["POST"])
def toggle_edit_mode():
    """切换危险区域编辑模式端点
    ---
    tags:
      - 配置管理
    description: >
      开启或关闭危险区域的编辑模式。
      开启后，实时视频流 (`/api/video_feed`) 可能会叠加可编辑的UI元素。
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            edit_mode:
              type: boolean
              description: true为开启编辑模式, false为关闭.
    responses:
      200:
        description: 成功切换模式.
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            edit_mode:
              type: boolean
    """
    global edit_mode
    data = request.json
    new_mode = data.get('edit_mode', False)
    
    # 添加日志记录
    logger.info(f"切换编辑模式: {edit_mode} -> {new_mode}")
    
    edit_mode = new_mode
    return jsonify({
        "status": "success", 
        "edit_mode": edit_mode
    })

@bp.route("/detection_mode", methods=["GET", "POST"])
def detection_mode():
    """获取或设置检测模式"""
    if request.method == "POST":
        data = request.json
        mode = data.get('mode')
        
        # 添加日志记录
        logger.info(f"设置检测模式: {mode}")
        
        if mode in ['object_detection', 'face_only']:
            system_state.DETECTION_MODE = mode
            logger.info(f"检测模式已切换为: {system_state.DETECTION_MODE}")
            return jsonify({
                "status": "success", 
                "message": f"检测模式已设置为 {mode}",
                "detection_mode": mode
            })
        
        logger.error(f"无效的检测模式: {mode}")
        return jsonify({
            "status": "error", 
            "message": "无效的检测模式"
        }), 400
    
    # GET请求
    logger.info("获取当前检测模式")
    return jsonify({
        "status": "success",
        "detection_mode": system_state.DETECTION_MODE
    })