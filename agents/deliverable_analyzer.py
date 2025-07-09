"""
DeliverableEstimate Pro - Deliverable Analyzer Agent
"""

from datetime import datetime
from typing import Dict, List, Any
import re


class DeliverableAnalyzer:
    """成果物分析・複雑度評価エージェント"""
    
    def __init__(self):
        # 成果物カテゴリのマッピング
        self.category_mapping = {
            "documentation": ["要件", "仕様", "設計", "マニュアル", "ドキュメント", "document", "spec"],
            "frontend_development": ["フロントエンド", "ui", "画面", "ページ", "interface", "frontend"],
            "backend_development": ["バックエンド", "api", "サーバー", "backend", "server"],
            "database": ["データベース", "db", "テーブル", "database"],
            "testing": ["テスト", "test", "検証", "verification"],
            "deployment": ["デプロイ", "環境構築", "インフラ", "deploy", "infrastructure"],
            "integration": ["連携", "統合", "integration"],
            "security": ["セキュリティ", "認証", "security", "auth"]
        }
        
        # 複雑度レベルの判定基準
        self.complexity_keywords = {
            "high": ["複雑", "高度", "カスタム", "独自", "複数システム", "マイクロサービス"],
            "medium": ["標準", "一般的", "基本", "通常"],
            "low": ["簡単", "シンプル", "基礎", "最小限"]
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """成果物の詳細分析と複雑度評価"""
        try:
            deliverables = state["deliverables"]
            project_context = state["project_context"]
            tech_assumptions = state["tech_assumptions"]
            
            analyzed_deliverables = []
            
            for deliverable in deliverables:
                # 成果物の意味解析
                semantic_analysis = self._analyze_deliverable_semantics(deliverable)
                
                # 複雑度レベル判定
                complexity_level = self._determine_complexity_level(
                    deliverable, project_context, tech_assumptions
                )
                
                # リスクファクター特定
                risk_factors = self._identify_risk_factors(deliverable, project_context)
                
                # 依存関係分析
                dependencies = self._analyze_dependencies(deliverable, deliverables)
                
                # 過去実績データマッチング（簡易版）
                historical_matches = self._find_historical_matches(deliverable)
                
                analyzed_deliverables.append({
                    "name": deliverable["name"],
                    "description": deliverable["description"],
                    "category": semantic_analysis["category"],
                    "complexity_level": complexity_level,
                    "risk_factors": risk_factors,
                    "dependencies": dependencies,
                    "historical_matches": historical_matches,
                    "semantic_analysis": semantic_analysis
                })
            
            # 全体アセスメント
            overall_assessment = self._generate_overall_assessment(analyzed_deliverables)
            
            return {
                **state,
                "analyzed_deliverables": analyzed_deliverables,
                "overall_assessment": overall_assessment,
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                **state,
                "error": f"Deliverable analysis failed: {str(e)}"
            }
    
    def _analyze_deliverable_semantics(self, deliverable: Dict[str, Any]) -> Dict[str, Any]:
        """成果物の意味解析"""
        name = deliverable["name"].lower()
        description = deliverable["description"].lower()
        combined_text = f"{name} {description}"
        
        # カテゴリ判定
        category = "other"
        max_matches = 0
        
        for cat, keywords in self.category_mapping.items():
            matches = sum(1 for keyword in keywords if keyword in combined_text)
            if matches > max_matches:
                max_matches = matches
                category = cat
        
        # 技術的複雑性の評価
        technical_complexity = self._assess_technical_complexity(combined_text)
        
        # ビジネス影響度の評価
        business_impact = self._assess_business_impact(combined_text)
        
        return {
            "category": category,
            "technical_complexity": technical_complexity,
            "business_impact": business_impact,
            "keyword_matches": max_matches
        }
    
    def _assess_technical_complexity(self, text: str) -> str:
        """技術的複雑性の評価"""
        high_complexity_indicators = [
            "マイクロサービス", "分散", "リアルタイム", "機械学習", "ai",
            "パフォーマンス最適化", "大量データ", "並行処理"
        ]
        
        medium_complexity_indicators = [
            "api", "データベース", "認証", "検索", "フィルタ",
            "管理画面", "レポート", "csv出力"
        ]
        
        high_count = sum(1 for indicator in high_complexity_indicators if indicator in text)
        medium_count = sum(1 for indicator in medium_complexity_indicators if indicator in text)
        
        if high_count >= 2 or (high_count >= 1 and medium_count >= 2):
            return "high"
        elif high_count >= 1 or medium_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _assess_business_impact(self, text: str) -> str:
        """ビジネス影響度の評価"""
        high_impact_indicators = [
            "決済", "料金", "売上", "顧客データ", "個人情報",
            "セキュリティ", "コンプライアンス", "法的要件"
        ]
        
        medium_impact_indicators = [
            "ユーザー管理", "商品管理", "在庫", "注文",
            "レポート", "分析", "通知"
        ]
        
        high_count = sum(1 for indicator in high_impact_indicators if indicator in text)
        medium_count = sum(1 for indicator in medium_impact_indicators if indicator in text)
        
        if high_count >= 1:
            return "high"
        elif medium_count >= 1:
            return "medium"
        else:
            return "low"
    
    def _determine_complexity_level(self, deliverable: Dict, project_context: Dict, tech_assumptions: Dict) -> str:
        """複雑度レベルの判定"""
        base_complexity = deliverable.get("semantic_analysis", {}).get("technical_complexity", "medium")
        
        # プロジェクト全体の複雑度による調整
        project_complexity = project_context.get("complexity", "medium")
        
        # 複雑度の組み合わせによる最終判定
        complexity_matrix = {
            ("low", "simple"): "low",
            ("low", "medium"): "low", 
            ("low", "complex"): "medium",
            ("medium", "simple"): "low",
            ("medium", "medium"): "medium",
            ("medium", "complex"): "high",
            ("high", "simple"): "medium",
            ("high", "medium"): "high",
            ("high", "complex"): "high"
        }
        
        return complexity_matrix.get((base_complexity, project_complexity), "medium")
    
    def _identify_risk_factors(self, deliverable: Dict, project_context: Dict) -> List[str]:
        """リスクファクターの特定"""
        risk_factors = []
        name_desc = f"{deliverable['name']} {deliverable['description']}".lower()
        
        # 技術的リスク
        if any(keyword in name_desc for keyword in ["新技術", "初回", "未経験", "実験的"]):
            risk_factors.append("新技術・未経験領域")
        
        if any(keyword in name_desc for keyword in ["外部", "third-party", "api連携"]):
            risk_factors.append("外部システム依存")
        
        if any(keyword in name_desc for keyword in ["パフォーマンス", "大量", "高負荷"]):
            risk_factors.append("パフォーマンス要件")
        
        # ビジネスリスク
        if any(keyword in name_desc for keyword in ["要件", "仕様"]):
            risk_factors.append("要件変更の可能性")
        
        if any(keyword in name_desc for keyword in ["ステークホルダー", "承認", "レビュー"]):
            risk_factors.append("ステークホルダー調整")
        
        # プロジェクト固有リスク
        special_requirements = project_context.get("special_requirements", [])
        if "決済機能" in special_requirements and "決済" in name_desc:
            risk_factors.append("決済機能の複雑性")
        
        if "高セキュリティ要件" in special_requirements:
            risk_factors.append("セキュリティ要件の厳格性")
        
        return risk_factors if risk_factors else ["標準的なリスク"]
    
    def _analyze_dependencies(self, current_deliverable: Dict, all_deliverables: List[Dict]) -> List[str]:
        """依存関係の分析"""
        dependencies = []
        current_name = current_deliverable["name"].lower()
        
        # 一般的な依存関係パターン
        dependency_patterns = {
            "開発": ["設計", "仕様"],
            "テスト": ["開発", "実装"],
            "デプロイ": ["テスト", "開発"],
            "api": ["設計", "仕様"],
            "ui": ["設計", "api"],
            "画面": ["設計", "api"]
        }
        
        for deliverable in all_deliverables:
            if deliverable["name"] == current_deliverable["name"]:
                continue
                
            other_name = deliverable["name"].lower()
            
            # パターンマッチングによる依存関係検出
            for dependent_keyword, prerequisite_keywords in dependency_patterns.items():
                if dependent_keyword in current_name:
                    for prereq_keyword in prerequisite_keywords:
                        if prereq_keyword in other_name:
                            dependencies.append(deliverable["name"])
                            break
        
        return dependencies
    
    def _find_historical_matches(self, deliverable: Dict) -> Dict[str, Any]:
        """過去実績データマッチング（簡易版）"""
        # 実際の実装では、データベースから類似成果物を検索
        # ここでは簡易的な実装
        
        name_lower = deliverable["name"].lower()
        
        # 簡易的な過去実績データ
        historical_data = {
            "要件定義": {"average_days": 5, "confidence": 0.9},
            "設計": {"average_days": 8, "confidence": 0.85},
            "開発": {"average_days": 20, "confidence": 0.8},
            "テスト": {"average_days": 10, "confidence": 0.85},
            "api": {"average_days": 15, "confidence": 0.8},
            "ui": {"average_days": 12, "confidence": 0.75}
        }
        
        best_match = None
        best_score = 0
        
        for key, data in historical_data.items():
            if key in name_lower:
                score = len(key) / len(name_lower)  # 簡易的なマッチングスコア
                if score > best_score:
                    best_score = score
                    best_match = {
                        "matched_keyword": key,
                        "historical_average_days": data["average_days"],
                        "confidence": data["confidence"],
                        "match_score": score
                    }
        
        return best_match or {"matched_keyword": None, "historical_average_days": None, "confidence": 0.5, "match_score": 0}
    
    def _generate_overall_assessment(self, analyzed_deliverables: List[Dict]) -> Dict[str, Any]:
        """全体アセスメントの生成"""
        total_count = len(analyzed_deliverables)
        
        # カテゴリ別集計
        category_counts = {}
        complexity_counts = {"low": 0, "medium": 0, "high": 0}
        high_risk_items = []
        
        for deliverable in analyzed_deliverables:
            # カテゴリ集計
            category = deliverable["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # 複雑度集計
            complexity = deliverable["complexity_level"]
            complexity_counts[complexity] += 1
            
            # 高リスクアイテム特定
            if len(deliverable["risk_factors"]) > 2 or complexity == "high":
                high_risk_items.append(deliverable["name"])
        
        # 開発/ドキュメント比率計算
        development_categories = ["frontend_development", "backend_development", "database", "integration"]
        development_count = sum(category_counts.get(cat, 0) for cat in development_categories)
        documentation_count = category_counts.get("documentation", 0)
        
        development_ratio = development_count / total_count if total_count > 0 else 0
        documentation_ratio = documentation_count / total_count if total_count > 0 else 0
        
        # プロジェクト複雑度の総合評価
        if complexity_counts["high"] > total_count * 0.3:
            project_complexity = "high"
        elif complexity_counts["medium"] > total_count * 0.5:
            project_complexity = "medium-high"
        elif complexity_counts["low"] > total_count * 0.6:
            project_complexity = "low"
        else:
            project_complexity = "medium"
        
        # クリティカルパスアイテムの特定
        critical_path_items = []
        for deliverable in analyzed_deliverables:
            if (deliverable["category"] in ["documentation"] and 
                any(keyword in deliverable["name"].lower() for keyword in ["設計", "仕様"])):
                critical_path_items.append(deliverable["name"])
            elif deliverable["category"] in development_categories and deliverable["complexity_level"] == "high":
                critical_path_items.append(deliverable["name"])
        
        return {
            "project_complexity": project_complexity,
            "total_deliverable_count": total_count,
            "category_distribution": category_counts,
            "complexity_distribution": complexity_counts,
            "documentation_ratio": round(documentation_ratio, 2),
            "development_ratio": round(development_ratio, 2),
            "high_risk_items_count": len(high_risk_items),
            "high_risk_items": high_risk_items,
            "critical_path_items": critical_path_items,
            "recommendations": self._generate_recommendations(analyzed_deliverables, category_counts, complexity_counts)
        }
    
    def _generate_recommendations(self, deliverables: List[Dict], categories: Dict, complexities: Dict) -> List[str]:
        """推奨事項の生成"""
        recommendations = []
        
        # 高リスクアイテムに対する推奨
        high_risk_count = sum(1 for d in deliverables if len(d["risk_factors"]) > 2)
        if high_risk_count > len(deliverables) * 0.3:
            recommendations.append("高リスクアイテムが多いため、プロトタイピングと早期検証を推奨")
        
        # 複雑度に基づく推奨
        if complexities["high"] > len(deliverables) * 0.2:
            recommendations.append("複雑度の高い成果物について、十分なバッファ時間の確保が必要")
        
        # カテゴリ別推奨
        if categories.get("testing", 0) < categories.get("backend_development", 0) + categories.get("frontend_development", 0):
            recommendations.append("開発成果物に対してテスト成果物が不足している可能性があります")
        
        # 決済機能特有の推奨
        payment_items = [d for d in deliverables if "決済" in d["name"].lower() or "payment" in d["description"].lower()]
        if payment_items:
            recommendations.append("決済機能については、セキュリティ要件とコンプライアンス確認を重点的に実施")
        
        return recommendations if recommendations else ["標準的な開発プロセスに従って進行"]