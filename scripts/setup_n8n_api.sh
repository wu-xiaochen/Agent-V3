#!/bin/bash
# N8N API 设置脚本
# 帮助用户配置 N8N API Key

set -e

echo "════════════════════════════════════════════════════════════"
echo "  N8N API 设置向导"
echo "════════════════════════════════════════════════════════════"
echo ""

# 检查 n8n 是否运行
echo "1. 检查 n8n 服务状态..."
if docker ps | grep -q n8n; then
    echo "   ✅ n8n 容器正在运行"
else
    echo "   ❌ n8n 容器未运行"
    echo ""
    echo "请先启动 n8n:"
    echo "  docker start n8n"
    exit 1
fi

echo ""

# 检查 n8n API 是否可访问
echo "2. 检查 n8n API..."
if curl -s http://localhost:5678/rest/settings > /dev/null; then
    echo "   ✅ n8n API 可访问"
else
    echo "   ❌ n8n API 无法访问"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  如何获取 API Key"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "请按照以下步骤操作:"
echo ""
echo "方法 1: 通过 n8n Web 界面（推荐）"
echo "  1. 打开浏览器访问: http://localhost:5678"
echo "  2. 登录 n8n"
echo "  3. 点击右上角的用户图标"
echo "  4. 选择 'Settings'"
echo "  5. 进入 'API Keys' 页面"
echo "  6. 点击 'Create API Key'"
echo "  7. 给密钥命名（如 'Agent-V3'）"
echo "  8. 复制生成的 API Key"
echo ""
echo "方法 2: 使用命令行"
echo "  运行: docker exec -it n8n n8n user:create-api-key <your-email>"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# 询问用户是否已有 API Key
read -p "您是否已经获取了 API Key? (y/n): " has_key

if [ "$has_key" != "y" ]; then
    echo ""
    echo "请先获取 API Key，然后重新运行此脚本"
    exit 0
fi

echo ""
read -p "请输入您的 API Key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ API Key 不能为空"
    exit 1
fi

echo ""
echo "3. 验证 API Key..."

# 测试 API Key
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "X-N8N-API-KEY: $api_key" \
    http://localhost:5678/api/v1/workflows)

if [ "$response" = "200" ]; then
    echo "   ✅ API Key 有效!"
else
    echo "   ❌ API Key 无效 (HTTP $response)"
    echo ""
    echo "请检查:"
    echo "  1. API Key 是否正确复制"
    echo "  2. 是否有正确的权限"
    echo "  3. API Key 是否已激活"
    exit 1
fi

echo ""
echo "4. 更新配置文件..."

# 更新 tools_config.json
config_file="config/tools/tools_config.json"

if [ -f "$config_file" ]; then
    # 创建备份
    cp "$config_file" "${config_file}.backup"
    echo "   ✅ 已备份配置文件"
    
    # 使用 Python 更新配置
    python3 << EOF
import json

with open('$config_file', 'r') as f:
    config = json.load(f)

# 查找 n8n_mcp_generator 配置
for tool in config.get('tools', []):
    if tool.get('name') == 'n8n_mcp_generator':
        if 'env' not in tool:
            tool['env'] = {}
        tool['env']['N8N_API_KEY'] = '$api_key'
        tool['env']['N8N_API_URL'] = 'http://localhost:5678'
        break

with open('$config_file', 'w') as f:
    json.dump(config, f, indent=2)

print('   ✅ 配置文件已更新')
EOF

else
    echo "   ❌ 配置文件不存在: $config_file"
    exit 1
fi

echo ""
echo "5. 测试完整集成..."

python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from src.agents.shared.n8n_api_tools import N8NAPIClient

try:
    client = N8NAPIClient()
    workflows = client.list_workflows()
    print(f'   ✅ 集成测试成功!')
    print(f'   📊 当前工作流数量: {len(workflows)}')
    
    if workflows:
        print(f'\n   前3个工作流:')
        for w in workflows[:3]:
            status = '🟢 激活' if w.get('active') else '⚪ 未激活'
            print(f'      {status} {w.get("name")} (ID: {w.get("id")})')
except Exception as e:
    print(f'   ❌ 测试失败: {e}')
    sys.exit(1)
EOF

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  🎉 设置完成!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "您现在可以:"
echo ""
echo "1. 使用 Agent 创建工作流:"
echo "   python main.py --query \"在n8n上创建一个定时任务\""
echo ""
echo "2. 列出所有工作流:"
echo "   python main.py --query \"列出我的n8n工作流\""
echo ""
echo "3. 查看完整文档:"
echo "   cat docs/N8N_API_SETUP.md"
echo ""
echo "4. 在 n8n Web 界面查看:"
echo "   http://localhost:5678"
echo ""
echo "备份文件位置: ${config_file}.backup"
echo ""

