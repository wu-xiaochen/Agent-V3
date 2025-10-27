"""
供应链专业工具模块
为供应链智能体提供专业工具
"""

from typing import Dict, Any, List, Optional, Union
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from src.config.config_loader import config_loader


class DataAnalyzerTool(BaseTool):
    """数据分析工具"""
    name: str = "data_analyzer"
    description: str = "用于分析供应链数据，包括销售数据、库存数据、订单数据等，支持统计分析、趋势分析和异常检测"
    
    def _run(self, data: str, analysis_type: str = "summary") -> str:
        """
        执行数据分析
        
        Args:
            data: 数据，可以是JSON格式的数据或数据描述
            analysis_type: 分析类型，包括summary(摘要)、trend(趋势)、anomaly(异常检测)
            
        Returns:
            分析结果
        """
        try:
            # 尝试解析JSON数据
            try:
                data_dict = json.loads(data)
            except:
                # 如果不是JSON，则作为数据描述处理
                return self._analyze_description(data, analysis_type)
            
            # 根据分析类型执行不同的分析
            if analysis_type == "summary":
                return self._summary_analysis(data_dict)
            elif analysis_type == "trend":
                return self._trend_analysis(data_dict)
            elif analysis_type == "anomaly":
                return self._anomaly_detection(data_dict)
            else:
                return f"不支持的分析类型: {analysis_type}"
        except Exception as e:
            return f"数据分析出错: {str(e)}"
    
    def _analyze_description(self, description: str, analysis_type: str) -> str:
        """分析数据描述"""
        if analysis_type == "summary":
            return f"基于您提供的数据描述: {description}\n\n建议分析方向:\n1. 数据完整性检查\n2. 关键指标计算\n3. 数据分布分析\n4. 相关性分析"
        elif analysis_type == "trend":
            return f"基于您提供的数据描述: {description}\n\n趋势分析建议:\n1. 时间序列分析\n2. 季节性模式识别\n3. 长期趋势预测\n4. 周期性波动分析"
        elif analysis_type == "anomaly":
            return f"基于您提供的数据描述: {description}\n\n异常检测建议:\n1. 统计异常值检测\n2. 模式识别异常\n3. 时间点异常检测\n4. 异常原因分析"
        else:
            return f"不支持的分析类型: {analysis_type}"
    
    def _summary_analysis(self, data: Dict[str, Any]) -> str:
        """摘要分析"""
        result = "数据摘要分析:\n\n"
        
        # 基本统计信息
        if "values" in data and isinstance(data["values"], list):
            values = data["values"]
            if values:
                result += f"数据点数量: {len(values)}\n"
                result += f"最大值: {max(values)}\n"
                result += f"最小值: {min(values)}\n"
                result += f"平均值: {sum(values) / len(values):.2f}\n"
                
                # 计算标准差
                if len(values) > 1:
                    mean = sum(values) / len(values)
                    variance = sum((x - mean) ** 2 for x in values) / len(values)
                    std_dev = math.sqrt(variance)
                    result += f"标准差: {std_dev:.2f}\n"
        
        # 数据分布
        if "categories" in data and isinstance(data["categories"], dict):
            result += "\n分类数据分布:\n"
            for category, count in data["categories"].items():
                result += f"- {category}: {count}\n"
        
        # 时间范围
        if "time_range" in data:
            time_range = data["time_range"]
            result += f"\n时间范围: {time_range.get('start', '未知')} 到 {time_range.get('end', '未知')}\n"
        
        return result
    
    def _trend_analysis(self, data: Dict[str, Any]) -> str:
        """趋势分析"""
        result = "趋势分析结果:\n\n"
        
        if "time_series" in data and isinstance(data["time_series"], list):
            time_series = data["time_series"]
            if len(time_series) >= 2:
                # 简单线性趋势分析
                values = [point.get("value", 0) for point in time_series]
                n = len(values)
                
                # 计算线性趋势
                x = list(range(n))
                sum_x = sum(x)
                sum_y = sum(values)
                sum_xy = sum(x[i] * values[i] for i in range(n))
                sum_x2 = sum(x[i] ** 2 for i in range(n))
                
                # 计算斜率和截距
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
                intercept = (sum_y - slope * sum_x) / n
                
                result += f"线性趋势: y = {slope:.4f}x + {intercept:.4f}\n"
                
                if slope > 0:
                    result += "趋势: 上升趋势\n"
                elif slope < 0:
                    result += "趋势: 下降趋势\n"
                else:
                    result += "趋势: 平稳\n"
                
                # 计算变化率
                if len(values) >= 2:
                    change_rate = (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0
                    result += f"整体变化率: {change_rate:.2f}%\n"
        
        return result
    
    def _anomaly_detection(self, data: Dict[str, Any]) -> str:
        """异常检测"""
        result = "异常检测结果:\n\n"
        
        if "values" in data and isinstance(data["values"], list):
            values = data["values"]
            if len(values) >= 3:
                # 使用IQR方法检测异常值
                sorted_values = sorted(values)
                n = len(sorted_values)
                
                # 计算四分位数
                q1_index = n // 4
                q3_index = 3 * n // 4
                q1 = sorted_values[q1_index]
                q3 = sorted_values[q3_index]
                iqr = q3 - q1
                
                # 异常值阈值
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # 检测异常值
                anomalies = []
                for i, value in enumerate(values):
                    if value < lower_bound or value > upper_bound:
                        anomalies.append((i, value))
                
                result += f"数据点数量: {len(values)}\n"
                result += f"Q1 (25%分位数): {q1}\n"
                result += f"Q3 (75%分位数): {q3}\n"
                result += f"IQR (四分位距): {iqr}\n"
                result += f"异常值阈值: [{lower_bound:.2f}, {upper_bound:.2f}]\n"
                result += f"检测到 {len(anomalies)} 个异常值\n"
                
                if anomalies:
                    result += "\n异常值详情:\n"
                    for index, value in anomalies:
                        result += f"- 位置 {index}: {value}\n"
        
        return result
    
    async def _arun(self, data: str, analysis_type: str = "summary") -> str:
        """异步执行数据分析"""
        return self._run(data, analysis_type)


class ForecastingModelTool(BaseTool):
    """预测模型工具"""
    name: str = "forecasting_model"
    description: str = "用于供应链需求预测、销售预测、库存预测等，支持多种预测模型和时间序列分析"
    
    def _run(self, data: str, forecast_period: int = 5, model_type: str = "linear") -> str:
        """
        执行预测分析
        
        Args:
            data: 历史数据，可以是JSON格式的时间序列数据
            forecast_period: 预测期数
            model_type: 预测模型类型，包括linear(线性)、exponential(指数)、seasonal(季节性)
            
        Returns:
            预测结果
        """
        try:
            # 尝试解析JSON数据
            try:
                data_dict = json.loads(data)
            except:
                return "无法解析数据，请提供JSON格式的时间序列数据"
            
            # 检查是否包含时间序列数据
            if "time_series" not in data_dict:
                return "数据中缺少时间序列信息，请提供包含time_series字段的数据"
            
            time_series = data_dict["time_series"]
            if not isinstance(time_series, list) or len(time_series) < 3:
                return "时间序列数据不足，至少需要3个数据点进行预测"
            
            # 提取数值
            values = [point.get("value", 0) for point in time_series]
            
            # 根据模型类型执行预测
            if model_type == "linear":
                return self._linear_forecast(values, forecast_period)
            elif model_type == "exponential":
                return self._exponential_forecast(values, forecast_period)
            elif model_type == "seasonal":
                return self._seasonal_forecast(values, forecast_period, time_series)
            else:
                return f"不支持的预测模型类型: {model_type}"
        except Exception as e:
            return f"预测分析出错: {str(e)}"
    
    def _linear_forecast(self, values: List[float], forecast_period: int) -> str:
        """线性预测"""
        n = len(values)
        x = list(range(n))
        
        # 计算线性回归
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        # 计算斜率和截距
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # 生成预测
        forecast = []
        for i in range(forecast_period):
            x_future = n + i
            y_future = slope * x_future + intercept
            forecast.append(y_future)
        
        # 计算预测准确度
        predicted = [slope * i + intercept for i in range(n)]
        mse = sum((values[i] - predicted[i]) ** 2 for i in range(n)) / n
        rmse = math.sqrt(mse)
        
        # 格式化结果
        result = "线性预测结果:\n\n"
        result += f"预测模型: y = {slope:.4f}x + {intercept:.4f}\n"
        result += f"模型拟合度(RMSE): {rmse:.4f}\n\n"
        result += "未来预测值:\n"
        for i, value in enumerate(forecast):
            result += f"第{i+1}期: {value:.2f}\n"
        
        return result
    
    def _exponential_forecast(self, values: List[float], forecast_period: int) -> str:
        """指数平滑预测"""
        # 简单指数平滑
        alpha = 0.3  # 平滑参数
        
        # 初始化
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[i-1])
        
        # 生成预测
        forecast = [smoothed[-1]] * forecast_period
        
        # 计算预测准确度
        mse = sum((values[i] - smoothed[i]) ** 2 for i in range(len(values))) / len(values)
        rmse = math.sqrt(mse)
        
        # 格式化结果
        result = "指数平滑预测结果:\n\n"
        result += f"平滑参数(alpha): {alpha}\n"
        result += f"模型拟合度(RMSE): {rmse:.4f}\n\n"
        result += "未来预测值:\n"
        for i, value in enumerate(forecast):
            result += f"第{i+1}期: {value:.2f}\n"
        
        return result
    
    def _seasonal_forecast(self, values: List[float], forecast_period: int, time_series: List[Dict]) -> str:
        """季节性预测"""
        # 简单季节性预测，假设周期为12（月度数据）
        period = 12
        
        if len(values) < period * 2:
            return "季节性预测需要至少2个完整周期的数据（24个数据点）"
        
        # 计算季节性指数
        seasonal_indices = []
        for i in range(period):
            period_values = [values[j] for j in range(i, len(values), period)]
            avg_value = sum(period_values) / len(period_values)
            overall_avg = sum(values) / len(values)
            seasonal_index = avg_value / overall_avg
            seasonal_indices.append(seasonal_index)
        
        # 计算趋势
        n = len(values)
        x = list(range(n))
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # 生成预测
        forecast = []
        for i in range(forecast_period):
            x_future = n + i
            trend_value = slope * x_future + intercept
            seasonal_index = seasonal_indices[i % period]
            forecast_value = trend_value * seasonal_index
            forecast.append(forecast_value)
        
        # 格式化结果
        result = "季节性预测结果:\n\n"
        result += f"预测周期: {period}\n"
        result += f"趋势模型: y = {slope:.4f}x + {intercept:.4f}\n\n"
        result += "季节性指数:\n"
        months = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
        for i, index in enumerate(seasonal_indices):
            result += f"{months[i]}: {index:.4f}\n"
        
        result += "\n未来预测值:\n"
        for i, value in enumerate(forecast):
            result += f"第{i+1}期: {value:.2f}\n"
        
        return result
    
    async def _arun(self, data: str, forecast_period: int = 5, model_type: str = "linear") -> str:
        """异步执行预测分析"""
        return self._run(data, forecast_period, model_type)


class OptimizationEngineTool(BaseTool):
    """优化引擎工具"""
    name: str = "optimization_engine"
    description: str = "用于供应链优化问题，包括库存优化、路径优化、资源分配等，支持线性规划和启发式算法"
    
    def _run(self, problem: str, optimization_type: str = "inventory") -> str:
        """
        执行优化分析
        
        Args:
            problem: 优化问题描述，可以是JSON格式的数据
            optimization_type: 优化类型，包括inventory(库存)、routing(路径)、resource(资源分配)
            
        Returns:
            优化结果
        """
        try:
            # 尝试解析JSON数据
            try:
                problem_dict = json.loads(problem)
            except:
                # 如果不是JSON，则作为问题描述处理
                return self._analyze_optimization_problem(problem, optimization_type)
            
            # 根据优化类型执行不同的优化
            if optimization_type == "inventory":
                return self._inventory_optimization(problem_dict)
            elif optimization_type == "routing":
                return self._routing_optimization(problem_dict)
            elif optimization_type == "resource":
                return self._resource_optimization(problem_dict)
            else:
                return f"不支持的优化类型: {optimization_type}"
        except Exception as e:
            return f"优化分析出错: {str(e)}"
    
    def _analyze_optimization_problem(self, description: str, optimization_type: str) -> str:
        """分析优化问题描述"""
        if optimization_type == "inventory":
            return f"基于您提供的库存优化问题描述: {description}\n\n建议优化方向:\n1. 经济订货量(EOQ)模型\n2. 安全库存计算\n3. 再订货点确定\n4. 库存周转率优化"
        elif optimization_type == "routing":
            return f"基于您提供的路径优化问题描述: {description}\n\n建议优化方向:\n1. 旅行商问题(TSP)求解\n2. 车辆路径问题(VRP)求解\n3. 配送中心选址\n4. 运输成本最小化"
        elif optimization_type == "resource":
            return f"基于您提供的资源分配问题描述: {description}\n\n建议优化方向:\n1. 线性规划模型\n2. 整数规划模型\n3. 多目标优化\n4. 约束满足问题"
        else:
            return f"不支持的优化类型: {optimization_type}"
    
    def _inventory_optimization(self, problem: Dict[str, Any]) -> str:
        """库存优化"""
        result = "库存优化结果:\n\n"
        
        # 检查必要参数
        if "demand" not in problem or "holding_cost" not in problem or "order_cost" not in problem:
            return "库存优化需要以下参数: demand(年需求量), holding_cost(单位持有成本), order_cost(每次订货成本)"
        
        # 提取参数
        demand = problem["demand"]
        holding_cost = problem["holding_cost"]
        order_cost = problem["order_cost"]
        
        # 计算经济订货量(EOQ)
        eoq = math.sqrt(2 * demand * order_cost / holding_cost)
        
        # 计算年订货次数
        order_frequency = demand / eoq
        
        # 计算年总成本
        total_cost = (demand / eoq) * order_cost + (eoq / 2) * holding_cost
        
        result += f"年需求量: {demand}\n"
        result += f"单位持有成本: {holding_cost}\n"
        result += f"每次订货成本: {order_cost}\n\n"
        result += f"经济订货量(EOQ): {eoq:.2f}\n"
        result += f"年订货次数: {order_frequency:.2f}\n"
        result += f"年总成本: {total_cost:.2f}\n"
        
        # 如果有缺货成本，计算再订货点
        if "shortage_cost" in problem and "lead_time" in problem:
            shortage_cost = problem["shortage_cost"]
            lead_time = problem["lead_time"]
            
            # 计算最优缺货概率
            optimal_shortage_prob = holding_cost / (holding_cost + shortage_cost)
            
            # 计算再订货点
            daily_demand = demand / 365  # 假设一年365天
            reorder_point = daily_demand * lead_time
            
            result += f"\n再订货点: {reorder_point:.2f}\n"
            result += f"最优缺货概率: {optimal_shortage_prob:.4f}\n"
        
        return result
    
    def _routing_optimization(self, problem: Dict[str, Any]) -> str:
        """路径优化"""
        result = "路径优化结果:\n\n"
        
        # 检查必要参数
        if "locations" not in problem or "distances" not in problem:
            return "路径优化需要以下参数: locations(位置列表), distances(距离矩阵)"
        
        locations = problem["locations"]
        distances = problem["distances"]
        
        # 简单的最近邻算法求解TSP
        n = len(locations)
        if n <= 1:
            return "需要至少2个位置进行路径优化"
        
        # 从第一个位置开始
        visited = [0]  # 已访问的位置索引
        unvisited = list(range(1, n))  # 未访问的位置索引
        current = 0  # 当前位置索引
        total_distance = 0
        
        # 最近邻算法
        while unvisited:
            # 找到最近的未访问位置
            nearest = min(unvisited, key=lambda x: distances[current][x])
            total_distance += distances[current][nearest]
            visited.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # 返回起点
        total_distance += distances[current][0]
        visited.append(0)
        
        result += f"位置数量: {n}\n"
        result += f"优化路径: {' -> '.join(locations[i] for i in visited)}\n"
        result += f"总距离: {total_distance:.2f}\n"
        
        return result
    
    def _resource_optimization(self, problem: Dict[str, Any]) -> str:
        """资源分配优化"""
        result = "资源分配优化结果:\n\n"
        
        # 检查必要参数
        if "resources" not in problem or "tasks" not in problem or "efficiency" not in problem:
            return "资源分配优化需要以下参数: resources(资源列表), tasks(任务列表), efficiency(效率矩阵)"
        
        resources = problem["resources"]
        tasks = problem["tasks"]
        efficiency = problem["efficiency"]
        
        # 简单的贪心算法进行资源分配
        n_resources = len(resources)
        n_tasks = len(tasks)
        
        # 初始化分配结果
        allocation = [-1] * n_tasks  # -1表示未分配
        allocated_resources = set()
        
        # 按效率从高到低排序所有可能的分配
        allocations = []
        for i in range(n_resources):
            for j in range(n_tasks):
                allocations.append((i, j, efficiency[i][j]))
        
        allocations.sort(key=lambda x: x[2], reverse=True)
        
        # 贪心分配
        for resource_idx, task_idx, eff in allocations:
            if resource_idx not in allocated_resources and allocation[task_idx] == -1:
                allocation[task_idx] = resource_idx
                allocated_resources.add(resource_idx)
        
        # 计算总效率
        total_efficiency = 0
        for task_idx, resource_idx in enumerate(allocation):
            if resource_idx != -1:
                total_efficiency += efficiency[resource_idx][task_idx]
        
        result += f"资源数量: {n_resources}\n"
        result += f"任务数量: {n_tasks}\n\n"
        result += "资源分配结果:\n"
        for task_idx, resource_idx in enumerate(allocation):
            if resource_idx != -1:
                result += f"{tasks[task_idx]} -> {resources[resource_idx]} (效率: {efficiency[resource_idx][task_idx]})\n"
            else:
                result += f"{tasks[task_idx]} -> 未分配\n"
        
        result += f"\n总效率: {total_efficiency:.2f}\n"
        
        return result
    
    async def _arun(self, problem: str, optimization_type: str = "inventory") -> str:
        """异步执行优化分析"""
        return self._run(problem, optimization_type)


class RiskAssessmentTool(BaseTool):
    """风险评估工具"""
    name: str = "risk_assessment"
    description: str = "用于供应链风险评估，包括供应商风险、物流风险、市场风险等，支持风险识别、评估和缓解建议"
    
    def _run(self, data: str, risk_type: str = "supplier") -> str:
        """
        执行风险评估
        
        Args:
            data: 风险评估数据，可以是JSON格式的数据或描述
            risk_type: 风险类型，包括supplier(供应商)、logistics(物流)、market(市场)
            
        Returns:
            风险评估结果
        """
        try:
            # 尝试解析JSON数据
            try:
                data_dict = json.loads(data)
            except:
                # 如果不是JSON，则作为风险描述处理
                return self._analyze_risk_description(data, risk_type)
            
            # 根据风险类型执行不同的评估
            if risk_type == "supplier":
                return self._supplier_risk_assessment(data_dict)
            elif risk_type == "logistics":
                return self._logistics_risk_assessment(data_dict)
            elif risk_type == "market":
                return self._market_risk_assessment(data_dict)
            else:
                return f"不支持的风险类型: {risk_type}"
        except Exception as e:
            return f"风险评估出错: {str(e)}"
    
    def _analyze_risk_description(self, description: str, risk_type: str) -> str:
        """分析风险描述"""
        if risk_type == "supplier":
            return f"基于您提供的供应商风险描述: {description}\n\n建议评估方向:\n1. 供应商财务稳定性\n2. 供应商交付可靠性\n3. 质量一致性\n4. 供应链依赖度"
        elif risk_type == "logistics":
            return f"基于您提供的物流风险描述: {description}\n\n建议评估方向:\n1. 运输延迟风险\n2. 货物损坏风险\n3. 成本波动风险\n4. 基础设施可靠性"
        elif risk_type == "market":
            return f"基于您提供的市场风险描述: {description}\n\n建议评估方向:\n1. 需求波动风险\n2. 价格波动风险\n3. 竞争格局变化\n4. 宏观经济影响"
        else:
            return f"不支持的风险类型: {risk_type}"
    
    def _supplier_risk_assessment(self, data: Dict[str, Any]) -> str:
        """供应商风险评估"""
        result = "供应商风险评估结果:\n\n"
        
        # 提取供应商信息
        if "suppliers" not in data:
            return "缺少供应商信息，请提供suppliers字段"
        
        suppliers = data["suppliers"]
        if not isinstance(suppliers, list):
            return "suppliers字段应为列表格式"
        
        # 评估每个供应商
        risk_scores = []
        for supplier in suppliers:
            if "name" not in supplier:
                continue
                
            name = supplier["name"]
            
            # 计算风险分数
            score = 50  # 基础分数
            
            # 财务稳定性
            if "financial_stability" in supplier:
                financial = supplier["financial_stability"]
                if financial == "high":
                    score -= 20
                elif financial == "medium":
                    score -= 10
                elif financial == "low":
                    score += 20
            
            # 交付可靠性
            if "delivery_reliability" in supplier:
                reliability = supplier["delivery_reliability"]
                if reliability >= 0.95:
                    score -= 15
                elif reliability >= 0.9:
                    score -= 5
                elif reliability >= 0.8:
                    score += 5
                else:
                    score += 15
            
            # 质量一致性
            if "quality_consistency" in supplier:
                quality = supplier["quality_consistency"]
                if quality >= 0.98:
                    score -= 15
                elif quality >= 0.95:
                    score -= 5
                elif quality >= 0.9:
                    score += 5
                else:
                    score += 15
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            risk_scores.append((name, score))
        
        # 按风险分数排序
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 输出结果
        result += "供应商风险排名:\n"
        for i, (name, score) in enumerate(risk_scores):
            risk_level = "低" if score < 30 else "中" if score < 70 else "高"
            result += f"{i+1}. {name}: 风险分数 {score:.1f} ({risk_level}风险)\n"
        
        # 风险缓解建议
        result += "\n风险缓解建议:\n"
        high_risk = [name for name, score in risk_scores if score >= 70]
        if high_risk:
            result += f"高风险供应商({', '.join(high_risk)}):\n"
            result += "- 建议寻找备选供应商\n"
            result += "- 增加库存缓冲\n"
            result += "- 加强质量监控\n"
        
        medium_risk = [name for name, score in risk_scores if 30 <= score < 70]
        if medium_risk:
            result += f"\n中等风险供应商({', '.join(medium_risk)}):\n"
            result += "- 定期评估供应商表现\n"
            result += "- 建立供应商发展计划\n"
            result += "- 考虑部分业务转移\n"
        
        return result
    
    def _logistics_risk_assessment(self, data: Dict[str, Any]) -> str:
        """物流风险评估"""
        result = "物流风险评估结果:\n\n"
        
        # 提取物流信息
        if "routes" not in data:
            return "缺少物流路线信息，请提供routes字段"
        
        routes = data["routes"]
        if not isinstance(routes, list):
            return "routes字段应为列表格式"
        
        # 评估每条路线
        risk_scores = []
        for route in routes:
            if "name" not in route:
                continue
                
            name = route["name"]
            
            # 计算风险分数
            score = 50  # 基础分数
            
            # 运输距离
            if "distance" in route:
                distance = route["distance"]
                if distance > 1000:
                    score += 15
                elif distance > 500:
                    score += 5
            
            # 运输方式
            if "transport_mode" in route:
                mode = route["transport_mode"]
                if mode == "air":
                    score -= 10  # 空运速度快，风险低
                elif mode == "sea":
                    score += 5   # 海运时间长，风险中等
                elif mode == "road":
                    score += 10  # 公路运输易受影响
            
            # 历史延误率
            if "delay_rate" in route:
                delay_rate = route["delay_rate"]
                if delay_rate < 0.05:
                    score -= 15
                elif delay_rate < 0.1:
                    score -= 5
                elif delay_rate < 0.2:
                    score += 5
                else:
                    score += 15
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            risk_scores.append((name, score))
        
        # 按风险分数排序
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 输出结果
        result += "物流路线风险排名:\n"
        for i, (name, score) in enumerate(risk_scores):
            risk_level = "低" if score < 30 else "中" if score < 70 else "高"
            result += f"{i+1}. {name}: 风险分数 {score:.1f} ({risk_level}风险)\n"
        
        # 风险缓解建议
        result += "\n风险缓解建议:\n"
        high_risk = [name for name, score in risk_scores if score >= 70]
        if high_risk:
            result += f"高风险路线({', '.join(high_risk)}):\n"
            result += "- 考虑多式联运\n"
            result += "- 增加运输时间缓冲\n"
            result += "- 购买运输保险\n"
        
        medium_risk = [name for name, score in risk_scores if 30 <= score < 70]
        if medium_risk:
            result += f"\n中等风险路线({', '.join(medium_risk)}):\n"
            result += "- 优化运输计划\n"
            result += "- 加强物流跟踪\n"
            result += "- 建立应急计划\n"
        
        return result
    
    def _market_risk_assessment(self, data: Dict[str, Any]) -> str:
        """市场风险评估"""
        result = "市场风险评估结果:\n\n"
        
        # 提取市场信息
        if "products" not in data:
            return "缺少产品信息，请提供products字段"
        
        products = data["products"]
        if not isinstance(products, list):
            return "products字段应为列表格式"
        
        # 评估每个产品
        risk_scores = []
        for product in products:
            if "name" not in product:
                continue
                
            name = product["name"]
            
            # 计算风险分数
            score = 50  # 基础分数
            
            # 需求波动性
            if "demand_volatility" in product:
                volatility = product["demand_volatility"]
                if volatility < 0.1:
                    score -= 20
                elif volatility < 0.2:
                    score -= 10
                elif volatility < 0.3:
                    score += 0
                else:
                    score += 20
            
            # 价格波动性
            if "price_volatility" in product:
                price_vol = product["price_volatility"]
                if price_vol < 0.05:
                    score -= 15
                elif price_vol < 0.1:
                    score -= 5
                elif price_vol < 0.2:
                    score += 5
                else:
                    score += 15
            
            # 竞争激烈程度
            if "competition_level" in product:
                competition = product["competition_level"]
                if competition == "low":
                    score -= 15
                elif competition == "medium":
                    score += 0
                elif competition == "high":
                    score += 15
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            risk_scores.append((name, score))
        
        # 按风险分数排序
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 输出结果
        result += "产品市场风险排名:\n"
        for i, (name, score) in enumerate(risk_scores):
            risk_level = "低" if score < 30 else "中" if score < 70 else "高"
            result += f"{i+1}. {name}: 风险分数 {score:.1f} ({risk_level}风险)\n"
        
        # 风险缓解建议
        result += "\n风险缓解建议:\n"
        high_risk = [name for name, score in risk_scores if score >= 70]
        if high_risk:
            result += f"高风险产品({', '.join(high_risk)}):\n"
            result += "- 多元化产品组合\n"
            result += "- 灵活定价策略\n"
            result += "- 需求预测与监控\n"
        
        medium_risk = [name for name, score in risk_scores if 30 <= score < 70]
        if medium_risk:
            result += f"\n中等风险产品({', '.join(medium_risk)}):\n"
            result += "- 市场趋势分析\n"
            result += "- 竞争对手监控\n"
            result += "- 库存策略优化\n"
        
        return result
    
    async def _arun(self, data: str, risk_type: str = "supplier") -> str:
        """异步执行风险评估"""
        return self._run(data, risk_type)