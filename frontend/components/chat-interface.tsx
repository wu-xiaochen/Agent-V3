"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, Paperclip, Loader2, ChevronDown, ChevronUp, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAppStore } from "@/lib/store"
import { MessageBubble } from "./message-bubble"
import { Card } from "@/components/ui/card"
import { CrewDrawer } from "./crewai/crew-drawer"

// 🆕 类似V0的思维链展示组件
function ThinkingStatus({ 
  stage, 
  toolCalls 
}: { 
  stage: string | null
  toolCalls: any[] 
}) {
  const [isExpanded, setIsExpanded] = useState(false)  // 默认折叠

  // 如果没有任何内容，不显示
  if (!stage && toolCalls.length === 0) return null

  // 判断是否还在思考中
  const isThinking = stage && !["complete", null].includes(stage)
  const hasCompletedTools = toolCalls.some(call => call.status === "success" || call.status === "error")
  
  // 🆕 计算总执行时间
  const totalTime = toolCalls.reduce((sum, call) => sum + (call.execution_time || 0), 0)

  return (
    <div className="my-3 space-y-1.5">
      {/* 🆕 思考阶段指示器 - 类似V0 */}
      {isThinking && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          <span>Thought for {Math.ceil(totalTime)}s</span>
        </div>
      )}
      
      {/* 🆕 工具调用步骤 - V0简洁风格，逐条实时显示 */}
      {toolCalls
        .filter(call => call.type === 'action') // 只显示action类型（工具调用）
        .map((call, index) => {
          const isRunning = call.status === "running"
          const isSuccess = call.status === "success" || call.status === "complete"
          const isError = call.status === "error"
          
          // V0风格的工具描述
          const getStepDescription = () => {
            const toolName = call.tool
            if (toolName === "time") return "Checked current time"
            if (toolName === "search") return "Searched information"
            if (toolName === "calculator") return "Calculated result"
            if (toolName === "generate_document") return "Generated document"
            if (toolName === "crewai_generator") return "Built intelligent agent team"
            return `Used ${toolName}`
          }
          
          return (
            <div 
              key={`tool-${call.step}-${index}`}
              className="flex items-center gap-2 text-sm cursor-pointer hover:bg-muted/50 px-2 py-1 rounded transition-colors"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isRunning && <Loader2 className="h-3.5 w-3.5 animate-spin text-orange-500" />}
              {isSuccess && <span className="text-xs">🔧</span>}
              {isError && <span className="text-xs text-red-500">⚠️</span>}
              <span className="text-muted-foreground flex-1">
                {getStepDescription()}
              </span>
              {!isRunning && (
                <button className="text-muted-foreground hover:text-foreground">
                  <span className="text-xs">•••</span>
                </button>
              )}
            </div>
          )
        })}
      
      {/* 🆕 完成状态 - 显示总执行时间 */}
      {!isThinking && toolCalls.length > 0 && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className="text-xs">⚡</span>
          <span>Worked for {totalTime.toFixed(1)}s</span>
        </div>
      )}
      
      {/* 🆕 展开详情 - 点击步骤时显示 */}
      {isExpanded && toolCalls.length > 0 && (
        <Card className="p-3 mt-2 bg-muted/30 space-y-3">
          {toolCalls.map((call, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="flex items-center justify-center w-5 h-5 rounded-full bg-primary/10 text-primary text-xs font-bold">
                  {index + 1}
                </div>
                <span className="font-medium text-sm">{call.tool}</span>
                {call.execution_time && (
                  <span className="text-xs text-muted-foreground ml-auto">
                    {call.execution_time.toFixed(2)}s
                  </span>
                )}
              </div>
              
              {call.input && (
                <div className="ml-7 text-xs">
                  <p className="text-muted-foreground mb-1">Input:</p>
                  <div className="bg-background px-2 py-1 rounded font-mono">
                    {typeof call.input === 'object' ? JSON.stringify(call.input, null, 2) : call.input}
                  </div>
                </div>
              )}
              
              {(call.output || call.error) && (
                <div className="ml-7 text-xs">
                  <p className="text-muted-foreground mb-1">
                    {call.error ? "Error:" : "Output:"}
                  </p>
                  <div className={`px-2 py-1 rounded ${
                    call.error ? "bg-red-50 text-red-900" : "bg-background"
                  }`}>
                    {call.error || call.output}
                  </div>
                </div>
              )}
            </div>
          ))}
        </Card>
      )}
    </div>
  )
}

export function ChatInterface() {
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  // 🆕 改为按会话存储思维状态
  const [sessionThinkingStates, setSessionThinkingStates] = useState<Record<string, {
    isThinking: boolean
    thinkingChain: any[]
  }>>({})
  
  // 当前会话的思维状态
  const currentThinkingState = sessionThinkingStates[currentSession] || { isThinking: false, thinkingChain: [] }
  const isThinking = currentThinkingState.isThinking
  const thinkingChain = currentThinkingState.thinkingChain
  const [messageThinkingChains, setMessageThinkingChains] = useState<Record<string, any[]>>({})  // 🆕 每条消息的思维链
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle')  // 🆕 保存状态
  
  // 🆕 辅助函数：更新当前会话的思维状态
  const updateSessionThinking = (updates: { isThinking?: boolean; thinkingChain?: any[] }) => {
    setSessionThinkingStates(prev => ({
      ...prev,
      [currentSession]: {
        isThinking: updates.isThinking ?? prev[currentSession]?.isThinking ?? false,
        thinkingChain: updates.thinkingChain ?? prev[currentSession]?.thinkingChain ?? []
      }
    }))
  }
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { messages, addMessage, currentSession, crewDrawerOpen, setCrewDrawerOpen } = useAppStore()
  
  // 🆕 CrewAI画布状态（pendingCrewConfig保留为局部状态）
  const [pendingCrewConfig, setPendingCrewConfig] = useState<any | null>(null)

  // 🆕 组件挂载时初始化默认session
  useEffect(() => {
    // 确保默认session存在
    if (currentSession) {
      const sessionKey = `session_${currentSession}`
      const existingSession = localStorage.getItem(sessionKey)
      
      if (!existingSession) {
        const defaultSessionData = {
          sessionId: currentSession,
          messages: [],
          timestamp: new Date().toISOString()
        }
        localStorage.setItem(sessionKey, JSON.stringify(defaultSessionData))
        console.log(`💾 [初始化] 创建默认session: ${currentSession}`)
      } else {
        console.log(`✅ [初始化] session已存在: ${currentSession}`)
      }
    }
  }, []) // 只在组件挂载时执行一次

  // 🆕 监听会话切换，清理状态并加载该会话的思维链历史
  useEffect(() => {
    console.log("🔄 Session changed to:", currentSession)
    
    // 切换会话时清理UI状态，但不中断请求（让后台继续）
    setIsLoading(false)
    // 🆕 不清理thinking状态，保留在session中
    // updateSessionThinking({ isThinking: false, thinkingChain: [] })
    setUploadedFiles([])
    
    // ⚠️ 不再中断请求，让AI在后台继续生成
    // if (abortController) {
    //   console.log("🛑 Aborting ongoing request due to session change")
    //   abortController.abort()
    //   setAbortController(null)
    // }
    console.log("✅ 会话切换：保留后台请求，让AI继续生成")
    
    // 🆕 加载该会话的思维链历史
    if (currentSession) {
      const savedChains = localStorage.getItem(`thinking_chains_${currentSession}`)
      if (savedChains) {
        try {
          const parsedChains = JSON.parse(savedChains)
          setMessageThinkingChains(parsedChains)
          console.log(`📥 加载思维链历史: ${Object.keys(parsedChains).length} 条消息`)
        } catch (e) {
          console.error("加载思维链历史失败:", e)
          setMessageThinkingChains({})
        }
      } else {
        setMessageThinkingChains({})
      }
    }
  }, [currentSession])

  // ✅ 真正修复：直接操作Radix UI的Viewport元素
  useEffect(() => {
    const scrollToBottom = () => {
      if (!scrollAreaRef.current) return
      
      // 找到Radix UI创建的viewport元素
      const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      
      if (viewport) {
        // 直接设置scrollTop到最大值，确保滚动到底部
        viewport.scrollTop = viewport.scrollHeight
        
        // 调试日志
        console.log('📜 Scrolling:', {
          scrollHeight: viewport.scrollHeight,
          scrollTop: viewport.scrollTop,
          clientHeight: viewport.clientHeight
        })
      }
    }
    
    // 使用setTimeout延迟确保DOM完全渲染
    const timer = setTimeout(scrollToBottom, 100)
    return () => clearTimeout(timer)
  }, [messages, thinkingChain, isThinking])

  const handleStop = () => {
    if (abortController) {
      console.log("🛑 Stopping AI execution...")
      abortController.abort()
      setAbortController(null)
      setIsLoading(false)
      updateSessionThinking({ isThinking: false, thinkingChain: [] })
      
      const stopMessage = {
        id: `msg-${Date.now()}-stop`,
        role: "assistant" as const,
        content: "⚠️ 任务已被用户停止",
        timestamp: new Date(),
      }
      addMessage(stopMessage)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) {
      console.log("⚠️ 跳过发送:", { isEmpty: !input.trim(), isLoading })
      return
    }
    
    console.log("🚀 [handleSend] 开始发送消息:", input.substring(0, 50))

    // ✅ 修复：构建包含文档附件的消息
    const attachments = uploadedFiles
      .filter(f => f.status === 'success')
      .map(f => ({
        id: f.id,
        name: f.file.name,
        type: f.type,
        url: f.url || '',
        size: f.file.size,
        parsed_content: f.parsed
      }))

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: "user" as const,
      content: input,
      timestamp: new Date(),
      files: attachments.length > 0 ? attachments : undefined
    }

    const messageContent = input
    const requestSessionId = currentSession || "default"
    const currentMessageId = userMessage.id  // 🆕 保存当前消息ID
    
    // 然后更新UI状态（先更新state，因为messages来自state）
    addMessage(userMessage)
    
    // 🆕 立即保存到localStorage（使用更新后的messages）
    // ⚠️ 注意：这里必须用[...messages, userMessage]，不能依赖state更新
    const updatedMessages = [...messages, userMessage]
    const sessionData = {
      sessionId: requestSessionId,
      messages: updatedMessages,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem(`session_${requestSessionId}`, JSON.stringify(sessionData))
    console.log(`💾💾💾 [重要] 用户输入后立即保存会话到localStorage:`, {
      sessionId: requestSessionId,
      messagesCount: updatedMessages.length,
      lastMessage: messageContent.substring(0, 30)
    })
    
    // 🆕 显示保存状态
    setSaveStatus('saving')
    setTimeout(() => {
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)  // 2秒后隐藏
    }, 300)
    
    setInput("")
    setIsLoading(true)
    updateSessionThinking({ isThinking: true, thinkingChain: [] })
    
    // ✅ 清空已上传的文件（发送后）
    setUploadedFiles([])

    // 创建新的 AbortController
    const controller = new AbortController()
    setAbortController(controller)

    // 🆕 启动思维链轮询
    let pollInterval: NodeJS.Timeout | null = null
    let pollCount = 0
    const MAX_POLLS = 240 // 最多轮询2分钟 (每500ms一次)
    
    try {
      const { api } = await import("@/lib/api")
      
      // 🆕 开始轮询思维链历史（150ms超快速轮询，真正逐条实时显示）
      // ⚠️ 不清空历史，让后端自动覆盖，这样轮询能立即看到数据
      let lastChainLength = 0 // 记录上次的链长度，实现增量更新
      
      pollInterval = setInterval(async () => {
        try {
          pollCount++
          const chainData = await api.thinking.getThinkingChain(requestSessionId)
          
          if (chainData.success && chainData.thinking_chain.length > 0) {
            // 🆕 只有当链长度变化时才更新（避免无意义的重新渲染）
            if (chainData.thinking_chain.length !== lastChainLength) {
              console.log(`🔄 轮询 #${pollCount}: 新增 ${chainData.thinking_chain.length - lastChainLength} 个步骤`)
              lastChainLength = chainData.thinking_chain.length
              
              // 🆕 检测crew生成完成（observation包含结果）
              const crewObservation = chainData.thinking_chain.find(
                step => step.type === 'observation' && 
                        step.step > 0 && 
                        step.content && 
                        (typeof step.content === 'string' && 
                         (step.content.includes('action') || step.content.includes('crew_config') || step.content.includes('agents')))
              )
              
              if (crewObservation && !crewDrawerOpen) {
                console.log("🎨 检测到crew生成完成，解析配置并打开画布")
                console.log("📦 observation内容:", crewObservation.content)
                
                try {
                  let crewConfig = null
                  
                  // 尝试多种解析方式
                  if (typeof crewObservation.content === 'string') {
                    // 先清理可能的非法字符
                    let cleanContent = crewObservation.content.trim()
                    
                    // 跳过明显不是JSON的内容
                    if (!cleanContent.startsWith('{') && !cleanContent.startsWith('[')) {
                      console.warn("⚠️ observation内容不是JSON格式:", cleanContent.substring(0, 100))
                      return
                    }
                    
                    try {
                      const parsed = JSON.parse(cleanContent)
                      console.log("✅ JSON解析成功:", parsed)
                      
                      // 尝试多个可能的字段
                      crewConfig = parsed.crew_config || parsed.config || parsed
                    } catch (parseError) {
                      console.error("❌ JSON解析失败:", parseError)
                      console.log("尝试解析的内容:", cleanContent.substring(0, 200))
                      return
                    }
                  } else if (typeof crewObservation.content === 'object') {
                    console.log("✅ observation是对象，直接提取")
                    crewConfig = crewObservation.content.crew_config || crewObservation.content
                  }
                  
                  // 验证crew_config是否有效
                  if (crewConfig && (crewConfig.agents || crewConfig.tasks)) {
                    console.log("✅ 成功提取crew配置:", {
                      id: crewConfig.id,
                      name: crewConfig.name,
                      agentsCount: crewConfig.agents?.length || 0,
                      tasksCount: crewConfig.tasks?.length || 0
                    })
                    setPendingCrewConfig(crewConfig)
                    setCrewDrawerOpen(true)
                  } else {
                    console.warn("⚠️ crew配置无效或不完整:", crewConfig)
                  }
                } catch (e) {
                  console.error("❌ 处理observation时发生错误:", e)
                  console.log("完整的observation:", crewObservation)
                }
              }
              
              // 🆕 转换为工具调用格式（只显示action类型）
              const toolSteps = chainData.thinking_chain
                .filter(step => step.type === 'action' || step.type === 'observation')
                .reduce((acc: any[], step) => {
                  if (step.type === 'action') {
                    // 查找是否已存在
                    const existing = acc.find(t => t.tool === step.tool && t.step === step.step)
                    if (!existing) {
                      acc.push({
                        type: 'action',
                        tool: step.tool,
                        step: step.step,
                        status: step.status || 'running',
                        input: step.tool_input,
                        timestamp: step.timestamp
                      })
                    }
                  } else if (step.type === 'observation') {
                    // 更新对应的工具状态
                    const tool = acc.find(t => t.step === step.step)
                    if (tool) {
                      tool.status = step.status || 'success'
                      tool.output = step.content
                      tool.error = step.error
                      tool.execution_time = step.execution_time
                    }
                  }
                  return acc
                }, [])
              
              console.log(`🔧 工具步骤: ${toolSteps.length} 个`)
              updateSessionThinking({ thinkingChain: toolSteps })
            }
            
            // 检查是否已完成
            const hasChainEnd = chainData.thinking_chain.some(step => step.type === 'chain_end')
            if (hasChainEnd && pollInterval) {
              console.log("✅ 思维链已完成，停止轮询")
              clearInterval(pollInterval)
              pollInterval = null
            }
          }
          
          // 达到最大轮询次数时停止
          if (pollCount >= MAX_POLLS) {
            console.warn("⚠️  达到最大轮询次数，停止轮询")
            if (pollInterval) {
              clearInterval(pollInterval)
              pollInterval = null
            }
          }
        } catch (pollError) {
          console.error("轮询思维链失败:", pollError)
        }
      }, 150)  // ← 150ms超快速轮询
      
      // ✅ 修复：调用API时携带附件信息
      console.log("🚀 Sending message:", {
        session: currentSession,
        message: messageContent,
        attachments: attachments.length
      })
      
      const response = await api.chat.sendMessage(
        currentSession || "default",
        messageContent,
        {
          provider: "siliconflow",
          memory: true,
          attachments: attachments  // ✅ 传递附件给后端
        }
      )

      console.log("📥 Response received:", response)

      // 🆕 检查会话是否已切换
      if (currentSession !== requestSessionId) {
        console.log("⚠️  会话已切换，忽略此响应", {
          request: requestSessionId,
          current: currentSession
        })
        return
      }

      if (response.success) {
        const responseText = response.response
        
        // 🆕 等待最后一次轮询完成（延迟1秒）
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 🆕 再获取一次最终的思维链数据
        let finalToolSteps: any[] = []
        try {
          const finalChainData = await api.thinking.getThinkingChain(requestSessionId)
          if (finalChainData.success && finalChainData.thinking_chain.length > 0) {
            finalToolSteps = finalChainData.thinking_chain
              .filter(step => step.type === 'action' || step.type === 'observation')
              .reduce((acc: any[], step) => {
                if (step.type === 'action') {
                  const existingTool = acc.find(t => t.tool === step.tool && t.step === step.step)
                  if (!existingTool) {
                    acc.push({
                      tool: step.tool,
                      step: step.step,
                      status: step.status || 'running',
                      input: step.tool_input,
                      timestamp: step.timestamp
                    })
                  }
                } else if (step.type === 'observation') {
                  const tool = acc.find(t => t.step === step.step)
                  if (tool) {
                    tool.status = step.status || 'success'
                    tool.output = step.content
                    tool.error = step.error
                    tool.execution_time = step.execution_time
                  }
                }
                return acc
              }, [])
            
            updateSessionThinking({ thinkingChain: finalToolSteps })
            console.log("🔍 最终思维链数据:", finalToolSteps)
          }
        } catch (err) {
          console.error("获取最终思维链失败:", err)
        }
        
        // 🆕 停止thinking状态
        updateSessionThinking({ isThinking: false })
        
        // 🆕 立即保存当前消息的思维链（使用finalToolSteps，不依赖state）
        console.log("💾 准备保存思维链:", {
          messageId: currentMessageId,
          chainLength: finalToolSteps.length,
          chain: finalToolSteps
        })
        
        if (finalToolSteps.length > 0) {
          console.log("💾 准备保存思维链到state和localStorage:", {
            messageId: currentMessageId,
            stepsCount: finalToolSteps.length,
            steps: finalToolSteps
          })
          
          // 保存到state
          setMessageThinkingChains(prev => {
            const updated = {
              ...prev,
              [currentMessageId]: finalToolSteps
            }
            console.log("📝 更新messageThinkingChains state:", Object.keys(updated).length, "条消息")
            return updated
          })
          
          // 🆕 同时保存到localStorage
          const savedChains = localStorage.getItem(`thinking_chains_${currentSession}`) || '{}'
          const parsedChains = JSON.parse(savedChains)
          parsedChains[currentMessageId] = finalToolSteps
          localStorage.setItem(`thinking_chains_${currentSession}`, JSON.stringify(parsedChains))
          console.log(`✅ 保存思维链记录成功: ${currentMessageId} - ${finalToolSteps.length} 个步骤`)
          console.log("📦 localStorage内容:", parsedChains)
        } else {
          console.warn("⚠️ 思维链为空，不保存", {
            messageId: currentMessageId,
            thinkingChainLength: thinkingChain.length
          })
        }
        
        const aiMessage = {
          id: `msg-${Date.now()}-ai`,
          role: "assistant" as const,
          content: responseText,
          timestamp: new Date(),
          metadata: response.metadata  // 🆕 保存metadata
        }
        addMessage(aiMessage)
        
        // 🆕 检查是否需要自动打开CrewAI画布
        console.log("🔍 检查metadata:", {
          hasMetadata: !!response.metadata,
          action: response.metadata?.action,
          fullMetadata: response.metadata
        })
        
        if (response.metadata && response.metadata.action === "open_canvas") {
          console.log("🎨 检测到CrewAI生成，准备自动打开画布", response.metadata)
          console.log("📦 Crew配置:", response.metadata.crew_config)
          
          // 保存待加载的Crew配置
          setPendingCrewConfig(response.metadata.crew_config)
          console.log("✅ pendingCrewConfig已设置")
          
          // 延迟打开画布（让用户看到消息后再打开）
          setTimeout(() => {
            console.log("🚀 延迟执行：打开CrewAI画布")
            setCrewDrawerOpen(true)
          }, 1500)
        } else {
          console.log("⚠️ 未检测到open_canvas action")
        }
      } else {
        updateSessionThinking({ isThinking: false })
        const errorMessage = {
          id: `msg-${Date.now()}-error`,
          role: "assistant" as const,
          content: "抱歉，处理您的请求时出错了。请稍后重试。",
          timestamp: new Date(),
        }
        addMessage(errorMessage)
      }
    } catch (error: any) {
      console.error("❌ 发送消息失败:", error)
      console.error("Error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      
      updateSessionThinking({ isThinking: false })
      setToolCalls([])
      
      const errorMessage = {
        id: `msg-${Date.now()}-error`,
        role: "assistant" as const,
        content: `❌ 无法连接到服务器。\n错误详情: ${error.message}\n请确保后端服务正在运行 (http://localhost:8000)`,
        timestamp: new Date(),
      }
      addMessage(errorMessage)
    } finally {
      // 🆕 清理轮询
      if (pollInterval) {
        clearInterval(pollInterval)
      }
      
      setIsLoading(false)
      setAbortController(null)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex-1 flex flex-col h-screen">
      <div className="border-b border-border p-4 bg-card flex-shrink-0 flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <div>
              <h2 className="text-lg font-semibold text-card-foreground">Chat Assistant</h2>
              <p className="text-sm text-muted-foreground">Ask me anything about your AI agents</p>
            </div>
            {/* 🆕 保存状态指示器 */}
            {saveStatus !== 'idle' && (
              <div className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full transition-all ${
                saveStatus === 'saving' 
                  ? 'bg-blue-500/10 text-blue-600' 
                  : 'bg-green-500/10 text-green-600'
              }`}>
                {saveStatus === 'saving' ? (
                  <>
                    <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Saved</span>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <CrewDrawer 
            open={crewDrawerOpen} 
            onOpenChange={setCrewDrawerOpen}
            initialCrewConfig={pendingCrewConfig}
          />
        </div>
      </div>

      <ScrollArea className="flex-1 p-4 overflow-hidden" ref={scrollAreaRef}>
        <div className="w-full max-w-5xl mx-auto space-y-4 px-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center">
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-foreground">Welcome to AI Agent Hub</h3>
                <p className="text-muted-foreground">Start a conversation to interact with your AI agents</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => {
                // 🆕 获取该消息对应的思维链
                const messageChain = message.role === "user" ? (
                  // 如果是最后一条用户消息且正在思考，使用当前的thinkingChain
                  (index === messages.length - 1 && isThinking) ? thinkingChain :
                  // 否则从历史记录中获取
                  (messageThinkingChains[message.id] || [])
                ) : []
                
                const hasChain = messageChain.length > 0
                const shouldShowThinking = message.role === "user" && index === messages.length - 1 && isThinking
                
                // 🔍 调试日志（只在有变化时打印）
                if (message.role === "user" && (hasChain || shouldShowThinking)) {
                  console.log(`📝 [渲染] 消息 ${message.id}:`, {
                    content: message.content.substring(0, 30),
                    isLastMessage: index === messages.length - 1,
                    isThinking,
                    hasChain,
                    shouldShowThinking,
                    messageChainLength: messageChain.length,
                    messageChain: messageChain,
                    allChainKeys: Object.keys(messageThinkingChains)
                  })
                }
                
                return (
                  <div key={message.id}>
                    {/* 用户或AI消息 */}
                    <MessageBubble message={message} />
                    
                    {/* 🆕 在用户消息后显示该消息对应的思维链 */}
                    {message.role === "user" && (hasChain || shouldShowThinking) && (
                      <div className="flex gap-3 mb-4">
                        {/* AI头像 */}
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-sm">🤖</span>
                          </div>
                        </div>
                        
                        {/* 思维链内容 */}
                        <div className="flex-1">
                          <ThinkingStatus 
                            stage={shouldShowThinking ? "thinking" : null} 
                            toolCalls={messageChain} 
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </>
          )}
          
          {/* ✅ 滚动锚点 - 确保自动滚动到最底部 */}
          <div ref={messagesEndRef} className="h-1" />
        </div>
      </ScrollArea>

      <div className="border-t border-border p-4 bg-card flex-shrink-0">
        <div className="w-full max-w-5xl mx-auto space-y-2 px-4">
          {/* 文件附件预览 - 类似 Cursor 的简洁设计 */}
          {uploadedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 pb-2">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  className="inline-flex items-center gap-2 px-2.5 py-1.5 bg-muted rounded-md text-sm"
                >
                  {file.type === 'image' && file.preview ? (
                    <img src={file.preview} alt="" className="w-5 h-5 rounded object-cover" />
                  ) : (
                    <Paperclip className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
                  <span className="text-xs font-medium truncate max-w-[150px]">{file.file.name}</span>
                  {file.status === 'uploading' && <Loader2 className="h-3 w-3 animate-spin" />}
                  {file.status === 'success' && <span className="text-green-500 text-xs">✓</span>}
                  {file.status === 'error' && <span className="text-red-500 text-xs">✗</span>}
                  <button
                    onClick={() => {
                      const newFiles = uploadedFiles.filter(f => f.id !== file.id)
                      setUploadedFiles(newFiles)
                    }}
                    className="hover:bg-background rounded p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
          
          <div className="flex items-end gap-2">
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              multiple
              accept="image/*,.pdf,.doc,.docx,.txt,.md"
              onChange={async (e) => {
                const files = Array.from(e.target.files || [])
                if (files.length === 0) return

                // 添加到待上传列表
                const newFiles = files.map(file => ({
                  id: `file-${Date.now()}-${Math.random()}`,
                  file,
                  type: file.type.startsWith('image/') ? 'image' as const : 'document' as const,
                  status: 'uploading' as const,
                  preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
                }))
                
                setUploadedFiles(prev => [...prev, ...newFiles])

                // 上传文件
                try {
                  const { api } = await import("@/lib/api")
                  
                  for (const uploadFile of newFiles) {
                    try {
                      const result = await api.files.uploadFile(uploadFile.file, {
                        fileType: uploadFile.type
                      })

                      if (result.success) {
                        setUploadedFiles(prev =>
                          prev.map(f =>
                            f.id === uploadFile.id
                              ? { 
                                  ...f, 
                                  status: 'success' as const, 
                                  url: result.download_url,
                                  parsed: result.parsed_content,
                                  filename: result.filename  // 🆕 保存文件名
                                }
                              : f
                          )
                        )
                        
                        // 🆕 不再自动显示解析结果，等待用户发送消息时再使用
                        console.log(`✅ 文件上传成功: ${result.filename}`)
                      } else {
                        throw new Error(result.error || 'Upload failed')
                      }
                    } catch (error) {
                      console.error("文件上传失败:", error)
                      setUploadedFiles(prev =>
                        prev.map(f =>
                          f.id === uploadFile.id ? { ...f, status: 'error' as const } : f
                        )
                      )
                    }
                  }
                } finally {
                  if (fileInputRef.current) {
                    fileInputRef.current.value = ""
                  }
                }
              }}
            />
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => fileInputRef.current?.click()} 
              className="shrink-0"
              title="上传文件"
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="min-h-[44px] max-h-[120px] resize-none"
              rows={1}
            />
            {isLoading ? (
              <Button
                onClick={handleStop}
                className="shrink-0 bg-destructive text-destructive-foreground hover:bg-destructive/90"
                size="icon"
                title="停止执行"
              >
                <X className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={handleSend}
                disabled={!input.trim()}
                className="shrink-0 bg-primary text-primary-foreground hover:bg-primary/90"
                size="icon"
                title="发送消息"
              >
                <Send className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

