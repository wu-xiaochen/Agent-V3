#!/bin/bash

# 设置必要的环境变量
export SILICONFLOW_API_KEY="sk-zueyelhrtzsngjdnqfnwfbsboockestuzwwhujpqrjmjmxyy"
export PINECONE_API_KEY="dummy-key"
export PINECONE_ENVIRONMENT="dummy-env"

# 运行项目
python main.py --provider siliconflow --interactive