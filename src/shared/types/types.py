"""
共享类型定义
"""
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator, TypeVar, Generic, Tuple
from enum import Enum

# 基础类型别名
JSONDict = Dict[str, Any]
JSONList = List[Dict[str, Any]]
MessageDict = Dict[str, Union[str, Dict[str, Any]]]

# 泛型类型变量
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# 回调函数类型
MessageCallback = Callable[[str], None]
StreamCallback = Callable[[AsyncGenerator[str, None]], None]
ErrorCallback = Callable[[Exception], None]

# 配置类型
ConfigDict = Dict[str, Any]
EnvironmentConfig = Dict[str, Any]
ServiceConfig = Dict[str, Any]

# 状态类型
StateType = str
StateTransition = Dict[str, StateType]

# LLM相关类型
LLMProvider = str
LLMModel = str
LLMParams = Dict[str, Any]
PromptTemplate = str
PromptVariables = Dict[str, Any]

# 会话相关类型
SessionID = str
UserID = str
ConversationID = str
Timestamp = str
AgentID = str
TaskID = str
MessageID = str

# 智能体相关类型
AgentConfig = Dict[str, Any]

# 任务相关类型
TaskStatus = str
TaskResult = Dict[str, Any]

# 工具相关类型
ToolName = str
ToolParams = Dict[str, Any]
ToolResult = Any

# API相关类型
Endpoint = str
HTTPMethod = str
Headers = Dict[str, str]
QueryParams = Dict[str, str]
RequestBody = Dict[str, Any]
ResponseBody = Dict[str, Any]

# 验证相关类型
ValidationRule = Callable[[Any], bool]
ValidationError = str
ValidationResult = Tuple[bool, List[ValidationError]]

# 缓存相关类型
CacheKey = str
CacheValue = Any
CacheTTL = int

# 日志相关类型
LogLevel = str
LogMessage = str
LogContext = Dict[str, Any]

# 事件相关类型
EventType = str
EventPayload = Dict[str, Any]
EventHandler = Callable[[EventType, EventPayload], None]

# 数据库相关类型
TableName = str
RecordID = str
Record = Dict[str, Any]
QueryFilter = Dict[str, Any]

# 文件相关类型
FilePath = str
FileName = str
FileContent = bytes
FileMetadata = Dict[str, Any]

# 网络相关类型
URL = str
IPAddress = str
Port = int
Protocol = str

# 安全相关类型
Token = str
SecretKey = str
Permission = str
Role = str

# 监控相关类型
MetricName = str
MetricValue = Union[int, float, str]
MetricTags = Dict[str, str]
AlertLevel = str

# 测试相关类型
TestCaseID = str
TestResult = Dict[str, Any]
TestSuite = List[TestCaseID]