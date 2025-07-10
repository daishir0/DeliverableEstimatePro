#!/usr/bin/env python3
"""
Debug test for individual components
"""

from tools.cost_calculator import CostCalculator

def test_cost_calculator():
    """コスト計算コンポーネントのテスト"""
    print("🧪 コスト計算コンポーネントのテスト...")
    
    calculator = CostCalculator()
    
    # テスト用の初期状態
    test_state = {
        "effort_estimates": [
            {"name": "基本システム開発", "effort_days": 20, "confidence_level": "80%"},
            {"name": "API連携", "effort_days": 10, "confidence_level": "70%"},
            {"name": "テスト", "effort_days": 5, "confidence_level": "90%"}
        ],
        "env_config": {
            "daily_rate": 50000,
            "tax_rate": 0.10,
            "currency": "JPY"
        }
    }
    
    # 処理実行
    result = calculator.process(test_state)
    
    if result.get("error"):
        print(f"❌ エラー: {result['error']}")
        return False
    
    # 結果確認
    cost_calc = result.get("cost_calculation", {})
    if cost_calc:
        print("✅ コスト計算成功")
        print(f"  - Deliverable costs: {len(cost_calc.get('deliverable_costs', []))} items")
        print(f"  - Financial summary: {cost_calc.get('financial_summary', {})}")
        return True
    else:
        print("❌ コスト計算データがありません")
        return False

if __name__ == "__main__":
    success = test_cost_calculator()
    print(f"\n{'✅ テスト成功' if success else '❌ テスト失敗'}")