"""
API接口模块

提供REST API和WebSocket接口的实现。
"""

try:
    from .rest_api import RestAPI
except ImportError:
    RestAPI = None

try:
    from .websocket_api import WebSocketAPI
except ImportError:
    WebSocketAPI = None

__all__ = [
    "RestAPI",
    "WebSocketAPI"
]