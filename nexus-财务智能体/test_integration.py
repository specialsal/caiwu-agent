#!/usr/bin/env python3
"""
测试前后端联通功能的脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import FinancialAgent

def test_financial_agent():
    """测试FinancialAgent的前后端联通功能"""
    print("🧪 开始测试FinancialAgent前后端联通功能...")
    
    # 创建agent实例（不提供API key，测试subprocess调用）
    agent = FinancialAgent(api_key=None)
    
    # 测试查询
    test_query = "分析腾讯控股(00700.HK)的最新财务状况"
    
    print(f"📝 测试查询: {test_query}")
    print("🔄 正在调用subprocess执行命令行工具...")
    
    try:
        # 执行分析
        result = agent.analyze(test_query)
        
        print("✅ 分析完成！")
        print(f"📊 报告标题: {result.get('title', 'N/A')}")
        print(f"📋 摘要: {result.get('summary', 'N/A')[:100]}...")
        print(f"📈 指标数量: {len(result.get('metrics', []))}")
        print(f"📊 趋势数据点: {len(result.get('revenue_trend', []))}")
        print(f"🧬 成本结构项: {len(result.get('cost_structure', []))}")
        print(f"📝 日志条目: {len(result.get('logs', []))}")
        
        # 显示前几个指标
        print("\n📊 关键指标:")
        for i, metric in enumerate(result.get('metrics', [])[:2]):
            print(f"  {i+1}. {metric.get('label', 'N/A')}: {metric.get('value', 'N/A')} ({metric.get('change', 'N/A')})")
        
        # 显示前几条日志
        print("\n📝 系统日志:")
        for i, log in enumerate(result.get('logs', [])[:3]):
            print(f"  {i+1}. {log}")
        
        print("\n🎉 前后端联通测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_financial_agent()
    sys.exit(0 if success else 1)