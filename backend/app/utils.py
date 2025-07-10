import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建控制台处理器
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(ch)