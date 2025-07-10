"""
DeliverableEstimate Pro - Effort Estimator Agent
"""

from datetime import datetime
from typing import Dict, List, Any
import math


class EffortEstimator:
    """工数見積・リスク調整エージェント"""
    
    def __init__(self):
        # カテゴリ別基礎工数（人日）
        self.base_effort_by_category = {
            "documentation": {
                "low": 3,
                "medium": 5,
                "high": 8
            },
            "frontend_development": {
                "low": 8,
                "medium": 15,
                "high": 25
            },
            "backend_development": {
                "low": 10,
                "medium": 18,
                "high": 30
            },
            "database": {
                "low": 5,
                "medium": 10,
                "high": 18
            },
            "testing": {
                "low": 5,
                "medium": 10,
                "high": 15
            },
            "deployment": {
                "low": 2,
                "medium": 5,
                "high": 10
            },
            "integration": {
                "low": 5,
                "medium": 12,
                "high": 20
            },
            "security": {
                "low": 3,
                "medium": 8,
                "high": 15
            },
            "other": {
                "low": 3,
                "medium": 6,
                "high": 12
            }
        }
        
        # プロジェクト複雑度による調整係数
        self.project_complexity_multipliers = {
            "low": 0.8,
            "medium": 1.0,
            "medium-high": 1.2,
            "high": 1.4
        }
        
        # リスクファクター別バッファ係数
        self.risk_buffer_factors = {
            "新技術・未経験領域": 0.3,
            "外部システム依存": 0.2,
            "パフォーマンス要件": 0.25,
            "要件変更の可能性": 0.15,
            "ステークホルダー調整": 0.1,
            "決済機能の複雑性": 0.35,
            "セキュリティ要件の厳格性": 0.2,
            "標準的なリスク": 0.05
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """工数見積とリスク調整"""
        try:
            analyzed_deliverables = state.get("analyzed_deliverables", [])
            project_context = state.get("project_context", {})
            tech_assumptions = state.get("tech_assumptions", {})
            overall_assessment = state.get("overall_assessment", {})
            
            # デフォルト値設定
            if not analyzed_deliverables:
                analyzed_deliverables = state.get("deliverables", [])
                # 基本的な分析情報を追加
                for deliverable in analyzed_deliverables:
                    if not deliverable.get("category"):
                        deliverable["category"] = "other"
                    if not deliverable.get("complexity_level"):
                        deliverable["complexity_level"] = "medium"
                    if not deliverable.get("risk_factors"):
                        deliverable["risk_factors"] = ["標準的なリスク"]
            
            effort_estimates = []
            
            for deliverable in analyzed_deliverables:
                # 基礎工数算出
                base_effort = self._calculate_base_effort(
                    deliverable["category"], 
                    deliverable["complexity_level"]
                )
                
                # 複雑度調整
                complexity_adjustment = self._calculate_complexity_adjustment(
                    deliverable["complexity_level"],
                    overall_assessment.get("project_complexity", "medium")
                )
                
                # リスクバッファ計算
                risk_buffer = self._calculate_risk_buffer(deliverable["risk_factors"])
                
                # 過去実績データ検証
                historical_validation = self._validate_against_historical_data(
                    deliverable, base_effort, complexity_adjustment
                )
                
                # 最終工数算出
                adjusted_effort = base_effort * complexity_adjustment
                final_effort = adjusted_effort + (adjusted_effort * risk_buffer)
                
                # 信頼度算出
                confidence_level = self._calculate_confidence_level(
                    deliverable, historical_validation, risk_buffer
                )
                
                # 見積根拠生成
                estimation_rationale = self._generate_estimation_rationale(
                    deliverable, base_effort, complexity_adjustment, risk_buffer
                )
                
                effort_estimates.append({
                    "name": deliverable["name"],
                    "category": deliverable["category"],
                    "complexity_level": deliverable["complexity_level"],
                    "base_effort_days": round(base_effort, 1),
                    "complexity_adjustment": round(complexity_adjustment, 2),
                    "risk_buffer": round(risk_buffer, 2),
                    "final_effort_days": round(final_effort, 1),
                    "confidence_level": f"{confidence_level}%",
                    "estimation_rationale": estimation_rationale,
                    "historical_validation": historical_validation,
                    "risk_factors": deliverable["risk_factors"]
                })
            
            # 全体サマリー生成
            summary = self._generate_effort_summary(effort_estimates, tech_assumptions)
            
            # 調整ファクター計算
            adjustment_factors = self._calculate_adjustment_factors(
                project_context, overall_assessment
            )
            
            return {
                **state,
                "effort_estimates": effort_estimates,
                "effort_summary": summary,
                "tech_assumptions_used": tech_assumptions,
                "adjustment_factors": adjustment_factors,
                "estimation_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                **state,
                "error": f"Effort estimation failed: {str(e)}"
            }
    
    def _calculate_base_effort(self, category: str, complexity_level: str) -> float:
        """基礎工数の算出"""
        category_efforts = self.base_effort_by_category.get(category, self.base_effort_by_category["other"])
        return float(category_efforts.get(complexity_level, category_efforts["medium"]))
    
    def _calculate_complexity_adjustment(self, deliverable_complexity: str, project_complexity: str) -> float:
        """複雑度調整係数の計算"""
        # 成果物個別の複雑度調整
        deliverable_multiplier = {
            "low": 0.9,
            "medium": 1.0,
            "high": 1.3
        }.get(deliverable_complexity, 1.0)
        
        # プロジェクト全体の複雑度調整
        project_multiplier = self.project_complexity_multipliers.get(project_complexity, 1.0)
        
        # 組み合わせ調整（単純な乗算ではなく、調整済み）
        combined_adjustment = deliverable_multiplier * (1 + (project_multiplier - 1) * 0.5)
        
        return max(0.7, min(2.0, combined_adjustment))  # 0.7～2.0の範囲に制限
    
    def _calculate_risk_buffer(self, risk_factors: List[str]) -> float:
        """リスクバッファの計算"""
        if not risk_factors:
            return 0.05  # 最小リスクバッファ
        
        total_buffer = 0
        for risk_factor in risk_factors:
            buffer = self.risk_buffer_factors.get(risk_factor, 0.1)
            total_buffer += buffer
        
        # 複数リスクの相乗効果を考慮（単純加算ではなく減衰）
        if len(risk_factors) > 1:
            total_buffer = total_buffer * (1 - 0.1 * (len(risk_factors) - 1))
        
        return max(0.05, min(0.5, total_buffer))  # 5%～50%の範囲に制限
    
    def _validate_against_historical_data(self, deliverable: Dict, base_effort: float, complexity_adjustment: float) -> Dict[str, Any]:
        """過去実績データとの比較検証"""
        historical_match = deliverable.get("historical_matches", {})
        
        if historical_match.get("historical_average_days"):
            historical_days = historical_match["historical_average_days"]
            estimated_days = base_effort * complexity_adjustment
            
            # 乖離率計算
            variance = abs(estimated_days - historical_days) / historical_days
            
            # 妥当性評価
            if variance <= 0.2:
                validity = "high"
            elif variance <= 0.4:
                validity = "medium"
            else:
                validity = "low"
            
            return {
                "has_historical_data": True,
                "historical_average_days": historical_days,
                "estimated_days": round(estimated_days, 1),
                "variance_rate": round(variance, 2),
                "validity": validity,
                "confidence": historical_match.get("confidence", 0.5)
            }
        else:
            return {
                "has_historical_data": False,
                "validity": "medium",
                "confidence": 0.5
            }
    
    def _calculate_confidence_level(self, deliverable: Dict, historical_validation: Dict, risk_buffer: float) -> int:
        """信頼度レベルの算出"""
        base_confidence = 75  # ベース信頼度
        
        # 過去実績データによる調整
        if historical_validation["has_historical_data"]:
            if historical_validation["validity"] == "high":
                base_confidence += 15
            elif historical_validation["validity"] == "medium":
                base_confidence += 5
            else:
                base_confidence -= 10
        
        # リスクレベルによる調整
        if risk_buffer <= 0.1:
            base_confidence += 10
        elif risk_buffer <= 0.25:
            base_confidence += 0
        else:
            base_confidence -= 15
        
        # 成果物カテゴリによる調整
        category = deliverable.get("category", "other")
        if category in ["documentation", "testing"]:
            base_confidence += 5  # 比較的予測しやすい
        elif category in ["integration", "security"]:
            base_confidence -= 5  # 不確実性が高い
        
        return max(50, min(95, base_confidence))  # 50%～95%の範囲に制限
    
    def _generate_estimation_rationale(self, deliverable: Dict, base_effort: float, complexity_adjustment: float, risk_buffer: float) -> str:
        """見積根拠の生成"""
        category = deliverable["category"]
        complexity = deliverable["complexity_level"]
        risk_factors = deliverable["risk_factors"]
        
        rationale_parts = []
        
        # ベース工数の説明
        rationale_parts.append(f"{category}カテゴリの{complexity}複雑度として基礎工数{base_effort}人日を設定")
        
        # 複雑度調整の説明
        if complexity_adjustment > 1.1:
            rationale_parts.append(f"高複雑度により{complexity_adjustment:.1f}倍に調整")
        elif complexity_adjustment < 0.9:
            rationale_parts.append(f"低複雑度により{complexity_adjustment:.1f}倍に調整")
        
        # リスクバッファの説明
        if risk_buffer > 0.2:
            primary_risks = [rf for rf in risk_factors if self.risk_buffer_factors.get(rf, 0) > 0.15]
            if primary_risks:
                rationale_parts.append(f"主要リスク（{', '.join(primary_risks[:2])}）により{risk_buffer*100:.0f}%のバッファを追加")
            else:
                rationale_parts.append(f"複数のリスクファクターにより{risk_buffer*100:.0f}%のバッファを追加")
        elif risk_buffer > 0.05:
            rationale_parts.append(f"標準的なリスクを考慮し{risk_buffer*100:.0f}%のバッファを追加")
        
        return "、".join(rationale_parts)
    
    def _generate_effort_summary(self, effort_estimates: List[Dict], tech_assumptions: Dict) -> Dict[str, Any]:
        """全体工数サマリーの生成"""
        total_effort_days = sum(estimate["final_effort_days"] for estimate in effort_estimates)
        
        # 信頼度レベルの平均算出
        confidence_values = []
        for estimate in effort_estimates:
            confidence_str = estimate["confidence_level"].rstrip('%')
            confidence_values.append(int(confidence_str))
        
        average_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 75
        
        # 高リスクアイテムの特定
        high_risk_items = []
        for estimate in effort_estimates:
            if (estimate["risk_buffer"] > 0.2 or 
                int(estimate["confidence_level"].rstrip('%')) < 75):
                high_risk_items.append(estimate["name"])
        
        # クリティカル依存関係の特定
        critical_dependencies = []
        for estimate in effort_estimates:
            if (estimate["category"] in ["documentation"] and 
                any(keyword in estimate["name"].lower() for keyword in ["設計", "仕様"])):
                critical_dependencies.append(f"{estimate['name']} → 開発全般")
        
        # カテゴリ別工数分布
        category_distribution = {}
        for estimate in effort_estimates:
            category = estimate["category"]
            category_distribution[category] = category_distribution.get(category, 0) + estimate["final_effort_days"]
        
        return {
            "total_effort_days": round(total_effort_days, 1),
            "average_confidence": f"{average_confidence:.0f}%",
            "high_risk_items": high_risk_items,
            "high_risk_count": len(high_risk_items),
            "critical_dependencies": critical_dependencies,
            "category_distribution": {k: round(v, 1) for k, v in category_distribution.items()},
            "tech_assumptions_applied": {
                "engineer_level": tech_assumptions.get("engineer_level"),
                "productivity_factor": 1.0  # 標準生産性
            }
        }
    
    def _calculate_adjustment_factors(self, project_context: Dict, overall_assessment: Dict) -> Dict[str, float]:
        """調整ファクターの計算"""
        
        # プロジェクト複雑度
        project_complexity_factor = self.project_complexity_multipliers.get(
            overall_assessment["project_complexity"], 1.0
        )
        
        # チーム経験度（簡易版）
        team_experience_factor = 1.0  # デフォルト値
        
        # スケジュール圧力（特殊要件から推測）
        schedule_pressure_factor = 1.0
        if "パフォーマンス要件" in project_context.get("special_requirements", []):
            schedule_pressure_factor = 1.1
        
        # 技術スタックの影響
        technologies = project_context.get("technologies", [])
        tech_stack_factor = 1.0
        if len(technologies) > 4:  # 多数の技術スタック
            tech_stack_factor = 1.1
        
        return {
            "project_complexity": round(project_complexity_factor, 2),
            "team_experience": round(team_experience_factor, 2),
            "schedule_pressure": round(schedule_pressure_factor, 2),
            "tech_stack": round(tech_stack_factor, 2)
        }