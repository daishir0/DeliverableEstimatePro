"""
DeliverableEstimate Pro - Cost Calculator Tool
"""

from datetime import datetime
from typing import Dict, List, Any


class CostCalculator:
    """コスト算出ツール（非AI数値計算）"""
    
    def __init__(self):
        pass
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """コスト算出と財務サマリー生成"""
        try:
            effort_estimates = state["effort_estimates"]
            env_config = state["env_config"]
            
            # 成果物別コスト計算
            deliverable_costs = self._calculate_deliverable_costs(
                effort_estimates, env_config
            )
            
            # 財務サマリー計算
            financial_summary = self._calculate_financial_summary(
                deliverable_costs, env_config
            )
            
            # コスト分析
            cost_analysis = self._generate_cost_analysis(
                deliverable_costs, financial_summary
            )
            
            return {
                **state,
                "cost_calculation": {
                    "deliverable_costs": deliverable_costs,
                    "financial_summary": financial_summary,
                    "cost_analysis": cost_analysis
                },
                "calculation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Cost calculation failed: {str(e)}"
            }
    
    def _calculate_deliverable_costs(self, effort_estimates: List[Dict], env_config: Dict) -> List[Dict]:
        """成果物別コスト計算"""
        deliverable_costs = []
        
        for estimate in effort_estimates:
            amount = estimate["final_effort_days"] * env_config["daily_rate"]
            
            deliverable_costs.append({
                "name": estimate["name"],
                "category": estimate.get("category", "other"),
                "effort_days": estimate["final_effort_days"],
                "daily_rate": env_config["daily_rate"],
                "amount": int(amount),
                "confidence_level": estimate.get("confidence_level", "75%"),
                "risk_factors": estimate.get("risk_factors", [])
            })
        
        return deliverable_costs
    
    def _calculate_financial_summary(self, deliverable_costs: List[Dict], env_config: Dict) -> Dict[str, Any]:
        """財務サマリー計算"""
        # 小計計算
        subtotal = sum(cost["amount"] for cost in deliverable_costs)
        
        # 税額計算
        tax_amount = int(subtotal * env_config["tax_rate"])
        
        # 総額計算
        total_amount = subtotal + tax_amount
        
        # 総工数計算
        total_effort_days = sum(cost["effort_days"] for cost in deliverable_costs)
        
        return {
            "subtotal": subtotal,
            "tax_rate": env_config["tax_rate"],
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "total_effort_days": round(total_effort_days, 1),
            "average_daily_rate": env_config["daily_rate"],
            "currency": env_config["currency"]
        }
    
    def _generate_cost_analysis(self, deliverable_costs: List[Dict], financial_summary: Dict) -> Dict[str, Any]:
        """コスト分析生成"""
        if not deliverable_costs:
            return {}
        
        # 最高・最低コストアイテム
        highest_cost_item = max(deliverable_costs, key=lambda x: x["amount"])
        lowest_cost_item = min(deliverable_costs, key=lambda x: x["amount"])
        
        # カテゴリ別コスト分析
        category_costs = {}
        for cost in deliverable_costs:
            category = cost["category"]
            category_costs[category] = category_costs.get(category, 0) + cost["amount"]
        
        # 開発/ドキュメント比率
        development_categories = ["frontend_development", "backend_development", "database", "integration"]
        development_cost = sum(category_costs.get(cat, 0) for cat in development_categories)
        documentation_cost = category_costs.get("documentation", 0)
        
        total_cost = financial_summary["subtotal"]
        development_ratio = development_cost / total_cost if total_cost > 0 else 0
        documentation_ratio = documentation_cost / total_cost if total_cost > 0 else 0
        
        # 平均コスト
        cost_per_deliverable = total_cost / len(deliverable_costs) if deliverable_costs else 0
        
        return {
            "highest_cost_item": highest_cost_item["name"],
            "highest_cost_amount": highest_cost_item["amount"],
            "lowest_cost_item": lowest_cost_item["name"],
            "lowest_cost_amount": lowest_cost_item["amount"],
            "development_cost_ratio": round(development_ratio, 2),
            "documentation_cost_ratio": round(documentation_ratio, 2),
            "cost_per_deliverable": int(cost_per_deliverable),
            "category_distribution": category_costs,
            "total_deliverables": len(deliverable_costs)
        }