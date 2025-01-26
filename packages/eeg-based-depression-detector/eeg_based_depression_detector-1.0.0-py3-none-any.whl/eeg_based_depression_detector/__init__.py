# depression_detector/__init__.py

"""
eeg抑郁症检测工具包
通过脑电信号图神经网络分析实现抑郁症分类
"""

from .predictor import DepressionDetector  # 导出核心类

# 定义包版本
__version__ = "1.0.0"

# 定义公共接口
__all__ = [
    'DepressionDetector',  # 主接口
    '__version__'          # 版本信息
]

# 初始化检查（可选）
try:
    # 验证依赖是否加载
    import numpy as np
    import networkx as nx
except ImportError as e:
    raise RuntimeError("依赖库加载失败，请检查安装环境") from e

# 包加载提示（调试用）
print(f"Depression Detector {__version__} 初始化成功")