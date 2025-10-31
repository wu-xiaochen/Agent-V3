#!/bin/bash

# Agent-V3 文档清理脚本
# 清理重复和过时的进度报告文档

echo "🧹 开始清理无用文档..."
echo "=================================="

cd /Users/xiaochenwu/Desktop/Agent-V3

# 创建文档归档目录
mkdir -p docs/archive/cleanup-$(date +%Y%m%d)

# 移动重复的进度报告到归档目录
echo "📦 归档重复的进度报告..."

# 需要保留的核心文档
KEEP_FILES=(
    "README.md"
    "BETA_MAIN_TASKS.md"
    "COLLABORATION_TASKS.md"
    "USER_EXPERIENCE_TEST_PLAN.md"
    "E2E_TEST_PLAN.md"
    "E2E_TEST_REPORT.md"
    "BETA_TEST_REPORT.md"
    "TESTING_SUMMARY.md"
    "GITHUB_SYNC_PLAN.md"
    "OPTIMIZATION_RECOMMENDATIONS.md"
    "CREWAI_JSON_PARSE_ISSUE_ANALYSIS.md"
    "CHANGELOG.md"
)

# 归档重复的进度报告
ARCHIVE_FILES=(
    "BETA_SESSION_SUMMARY.md"
    "BETA_DEVELOPMENT_STATUS.md"
    "BETA_PROGRESS_SUMMARY.md"
    "BETA_DEV_STATUS.md"
    "COLLABORATION_SESSION_SUMMARY.md"
    "FINAL_SESSION_SUMMARY.md"
    "FINAL_SESSION_REPORT.md"
    "SESSION_FINAL_SUMMARY.md"
    "BETA_PROGRESS_REPORT.md"
    "COMPLETION_REPORT.md"
    "BETA_COLLABORATION_PROGRESS.md"
    "BETA_DEV_PROGRESS.md"
    "BETA_TEST_PROGRESS_UPDATE.md"
    "BETA_TEST_UPDATE_2.md"
    "CONTINUED_PROGRESS.md"
    "CONTINUOUS_PROGRESS_SUMMARY.md"
    "SESSION_PROGRESS.md"
    "SESSION_ACCOMPLISHMENTS.md"
    "WORK_SESSION_SUMMARY.md"
    "MAIN_TASK_PROGRESS.md"
    "NEXT_STEPS.md"
    "MASTER_TASK_LIST.md"
    "COMPREHENSIVE_TASK_LIST.md"
    "OPTIMIZATION_IMPLEMENTATION_REPORT.md"
    "E2E_TEST_FIX_SUMMARY.md"
)

ARCHIVE_DIR="docs/archive/cleanup-$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"

for file in "${ARCHIVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  📄 归档: $file"
        mv "$file" "$ARCHIVE_DIR/"
    fi
done

echo ""
echo "✅ 文档清理完成"
echo "📁 已归档到: $ARCHIVE_DIR"
echo "=================================="

