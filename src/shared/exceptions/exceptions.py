"""
共享异常定义
"""


class BaseException(Exception):
    """基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AgentException(BaseException):
    """智能体基础异常"""
    pass


class DatabaseError(BaseException):
    """数据库错误"""
    pass


class TaskError(BaseException):
    """任务错误"""
    pass


class SessionError(BaseException):
    """会话错误"""
    pass


class MessageError(BaseException):
    """消息错误"""
    pass


class CacheError(BaseException):
    """缓存错误"""
    pass


class ExternalServiceError(BaseException):
    """外部服务错误"""
    pass


class VectorStoreError(BaseException):
    """向量存储错误"""
    pass


class StateTransitionError(AgentException):
    """状态转换错误"""
    pass


class ConfigurationError(AgentException):
    """配置错误"""
    pass


class ServiceUnavailableError(AgentException):
    """服务不可用错误"""
    pass


class ValidationError(AgentException):
    """验证错误"""
    pass


class StorageError(AgentException):
    """存储错误"""
    pass


class LLMServiceError(AgentException):
    """LLM服务错误"""
    pass


class CrewAIServiceError(AgentException):
    """CrewAI服务错误"""
    pass


class BusinessPlanError(AgentException):
    """业务计划错误"""
    pass


class SessionNotFoundError(AgentException):
    """会话未找到错误"""
    pass


class PermissionDeniedError(AgentException):
    """权限拒绝错误"""
    pass


class RateLimitExceededError(AgentException):
    """速率限制错误"""
    pass