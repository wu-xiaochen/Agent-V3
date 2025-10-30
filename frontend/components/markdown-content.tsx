"use client"

import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useAppStore } from '@/lib/store'

interface MarkdownContentProps {
  content: string
  className?: string
}

/**
 * 增强的Markdown渲染组件
 * 
 * 特性:
 * - 代码块语法高亮
 * - GitHub风格的表格
 * - 增强的列表样式
 * - 链接样式优化
 * - 暗色主题支持
 */
export function MarkdownContent({ content, className = '' }: MarkdownContentProps) {
  const darkMode = useAppStore(state => state.darkMode)
  
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // 代码块 - 支持语法高亮
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            const language = match ? match[1] : ''
            
            return !inline && match ? (
              <SyntaxHighlighter
                style={darkMode ? oneDark : vscDarkPlus}
                language={language}
                PreTag="div"
                className="rounded-lg my-4 text-sm"
                customStyle={{
                  margin: '1rem 0',
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                }}
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code 
                className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-primary"
                {...props}
              >
                {children}
              </code>
            )
          },
          
          // 表格容器 - 支持横向滚动
          table({ children }) {
            return (
              <div className="overflow-x-auto my-4 rounded-lg border border-border">
                <table className="min-w-full divide-y divide-border">
                  {children}
                </table>
              </div>
            )
          },
          
          // 表头
          thead({ children }) {
            return (
              <thead className="bg-muted/50">
                {children}
              </thead>
            )
          },
          
          // 表头单元格
          th({ children }) {
            return (
              <th className="px-4 py-3 text-left text-xs font-semibold text-foreground uppercase tracking-wider">
                {children}
              </th>
            )
          },
          
          // 表格行
          tr({ children }) {
            return (
              <tr className="hover:bg-muted/30 transition-colors">
                {children}
              </tr>
            )
          },
          
          // 表格单元格
          td({ children }) {
            return (
              <td className="px-4 py-3 text-sm text-foreground border-t border-border">
                {children}
              </td>
            )
          },
          
          // 无序列表
          ul({ children }) {
            return (
              <ul className="my-4 pl-6 space-y-2 list-disc marker:text-primary">
                {children}
              </ul>
            )
          },
          
          // 有序列表
          ol({ children }) {
            return (
              <ol className="my-4 pl-6 space-y-2 list-decimal marker:text-primary marker:font-semibold">
                {children}
              </ol>
            )
          },
          
          // 列表项
          li({ children }) {
            return (
              <li className="text-foreground">
                {children}
              </li>
            )
          },
          
          // 链接
          a({ children, href }) {
            return (
              <a 
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
              >
                {children}
              </a>
            )
          },
          
          // 标题
          h1({ children }) {
            return (
              <h1 className="text-3xl font-bold my-4 text-foreground border-b border-border pb-2">
                {children}
              </h1>
            )
          },
          
          h2({ children }) {
            return (
              <h2 className="text-2xl font-semibold my-4 text-foreground border-b border-border pb-2">
                {children}
              </h2>
            )
          },
          
          h3({ children }) {
            return (
              <h3 className="text-xl font-semibold my-3 text-foreground">
                {children}
              </h3>
            )
          },
          
          h4({ children }) {
            return (
              <h4 className="text-lg font-semibold my-3 text-foreground">
                {children}
              </h4>
            )
          },
          
          h5({ children }) {
            return (
              <h5 className="text-base font-semibold my-2 text-foreground">
                {children}
              </h5>
            )
          },
          
          h6({ children }) {
            return (
              <h6 className="text-sm font-semibold my-2 text-foreground">
                {children}
              </h6>
            )
          },
          
          // 段落
          p({ children }) {
            return (
              <p className="my-3 text-foreground leading-7">
                {children}
              </p>
            )
          },
          
          // 引用块
          blockquote({ children }) {
            return (
              <blockquote className="my-4 pl-4 border-l-4 border-primary/50 bg-muted/30 py-2 pr-4 italic">
                {children}
              </blockquote>
            )
          },
          
          // 水平分割线
          hr() {
            return (
              <hr className="my-6 border-border" />
            )
          },
          
          // 图片
          img({ src, alt }) {
            return (
              <img 
                src={src} 
                alt={alt || ''}
                className="max-w-full h-auto rounded-lg my-4 shadow-md"
              />
            )
          },
          
          // 删除线
          del({ children }) {
            return (
              <del className="text-muted-foreground">
                {children}
              </del>
            )
          },
          
          // 粗体
          strong({ children }) {
            return (
              <strong className="font-bold text-foreground">
                {children}
              </strong>
            )
          },
          
          // 斜体
          em({ children }) {
            return (
              <em className="italic text-foreground">
                {children}
              </em>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

