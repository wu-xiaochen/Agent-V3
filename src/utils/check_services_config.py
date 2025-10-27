#!/usr/bin/env python3
"""
详细检查services_config的结构
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.config_loader import config_loader

def check_services_config():
    """检查services_config的结构"""
    print("正在检查services_config的结构...")
    
    try:
        # 1. 获取services配置
        print("\n1. 获取services配置...")
        services_config = config_loader.get_services_config()
        print(f"services_config类型: {type(services_config)}")
        print(f"services_config键: {list(services_config.keys())}")
        
        # 2. 检查是否有'services'键
        print("\n2. 检查是否有'services'键...")
        if 'services' in services_config:
            print("找到'services'键")
            services = services_config['services']
            print(f"services类型: {type(services)}")
            print(f"services键: {list(services.keys())}")
            
            # 3. 检查'llm'键
            print("\n3. 检查'llm'键...")
            if 'llm' in services:
                print("找到'llm'键")
                llm = services['llm']
                print(f"llm类型: {type(llm)}")
                print(f"llm键: {list(llm.keys())}")
                
                # 4. 检查'provider'键
                print("\n4. 检查'provider'键...")
                if 'provider' in llm:
                    provider = llm['provider']
                    print(f"Provider: {provider}")
                else:
                    print("未找到'provider'键")
            else:
                print("未找到'llm'键")
        else:
            print("未找到'services'键")
        
        # 5. 直接检查llm_config
        print("\n5. 直接检查llm_config...")
        llm_config = services_config.get("llm", {})
        print(f"llm_config类型: {type(llm_config)}")
        print(f"llm_config键: {list(llm_config.keys())}")
        
        return True
        
    except Exception as e:
        print(f"检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_services_config()
    sys.exit(0 if success else 1)