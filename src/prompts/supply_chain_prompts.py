# 供应链智能体状态管理配置

# 多轮对话状态管理
CONVERSATION_STATES = {
    "INITIAL": "初始状态，等待用户输入需求",
    "PLANNING": "业务流程规划阶段，生成和调整流程规划",
    "CONFIRMATION": "流程确认阶段，与用户确认最终流程",
    "CREWAI_GENERATION": "CrewAI配置生成阶段，生成团队配置",
    "GUIDANCE": "用户引导阶段，提供操作指导",
    "COMPLETED": "任务完成状态"
}

# 状态转换规则
STATE_TRANSITIONS = {
    "INITIAL": ["PLANNING"],
    "PLANNING": ["PLANNING", "CONFIRMATION"],
    "CONFIRMATION": ["PLANNING", "CREWAI_GENERATION"],
    "CREWAI_GENERATION": ["GUIDANCE", "COMPLETED"],
    "GUIDANCE": ["GUIDANCE", "COMPLETED"],
    "COMPLETED": ["INITIAL"]
}