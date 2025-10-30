/**
 * 工具列表API - 用于CrewAI工具选择
 */

import { apiClient } from "../api-client"

// ==================== 类型定义 ====================

export interface ToolInfo {
  name: string
  display_name: string
  type: "builtin" | "mcp" | "api"
  enabled: boolean
  description: string
  parameters?: Record<string, any>
  config?: Record<string, any>
  module?: string
}

export interface ToolListResponse {
  success: boolean
  tools: ToolInfo[]
  total: number
  groups?: Record<string, string[]>
  enabled_count?: number
  message?: string
}

export interface ToolGroupResponse {
  success: boolean
  group_name: string
  tools: ToolInfo[]
  total: number
  message?: string
}

// ==================== API函数 ====================

/**
 * 获取所有可用工具列表（用于CrewAI工具选择）
 * 
 * 返回所有工具,包括启用的和禁用的,以便在Agent配置中选择
 */
export async function getAvailableTools(): Promise<ToolListResponse> {
  try {
    const response = await apiClient.get<ToolListResponse>("/api/tools/available")
    return response.data
  } catch (error: any) {
    console.error("获取工具列表失败:", error)
    return {
      success: false,
      tools: [],
      total: 0,
      message: error.response?.data?.message || error.message || "获取工具列表失败"
    }
  }
}

/**
 * 仅获取启用的工具列表
 */
export async function getEnabledTools(): Promise<ToolListResponse> {
  try {
    const response = await apiClient.get<ToolListResponse>("/api/tools/enabled")
    return response.data
  } catch (error: any) {
    console.error("获取启用工具列表失败:", error)
    return {
      success: false,
      tools: [],
      total: 0,
      message: error.response?.data?.message || error.message || "获取启用工具列表失败"
    }
  }
}

/**
 * 获取指定工具组的工具列表
 */
export async function getToolsByGroup(groupName: string): Promise<ToolGroupResponse> {
  try {
    const response = await apiClient.get<ToolGroupResponse>(`/api/tools/groups/${groupName}`)
    return response.data
  } catch (error: any) {
    console.error(`获取工具组 ${groupName} 失败:`, error)
    return {
      success: false,
      group_name: groupName,
      tools: [],
      total: 0,
      message: error.response?.data?.message || error.message || `获取工具组 ${groupName} 失败`
    }
  }
}

/**
 * 获取单个工具的详细信息
 */
export async function getToolDetails(toolName: string): Promise<ToolInfo | null> {
  try {
    const response = await getAvailableTools()
    if (response.success) {
      const tool = response.tools.find(t => t.name === toolName)
      return tool || null
    }
    return null
  } catch (error) {
    console.error(`获取工具 ${toolName} 详情失败:`, error)
    return null
  }
}

// ==================== 工具分类辅助函数 ====================

/**
 * 按类型分组工具
 */
export function groupToolsByType(tools: ToolInfo[]): Record<string, ToolInfo[]> {
  const grouped: Record<string, ToolInfo[]> = {
    builtin: [],
    mcp: [],
    api: []
  }
  
  for (const tool of tools) {
    const type = tool.type || "builtin"
    if (!grouped[type]) {
      grouped[type] = []
    }
    grouped[type].push(tool)
  }
  
  return grouped
}

/**
 * 过滤启用的工具
 */
export function filterEnabledTools(tools: ToolInfo[]): ToolInfo[] {
  return tools.filter(tool => tool.enabled)
}

/**
 * 搜索工具
 */
export function searchTools(tools: ToolInfo[], query: string): ToolInfo[] {
  if (!query) return tools
  
  const lowerQuery = query.toLowerCase()
  return tools.filter(tool => 
    tool.name.toLowerCase().includes(lowerQuery) ||
    tool.display_name.toLowerCase().includes(lowerQuery) ||
    tool.description.toLowerCase().includes(lowerQuery)
  )
}

// ==================== API对象 ====================

export const toolsListApi = {
  getAvailable: getAvailableTools,
  getEnabled: getEnabledTools,
  getByGroup: getToolsByGroup,
  getDetails: getToolDetails,
  groupByType: groupToolsByType,
  filterEnabled: filterEnabledTools,
  search: searchTools
}

export default toolsListApi
