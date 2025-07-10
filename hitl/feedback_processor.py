"""
DeliverableEstimate Pro - Feedback Processor
"""

import re
from datetime import datetime
from typing import Dict, List, Any


class FeedbackProcessor:
    """ユーザーフィードバック処理"""
    
    def __init__(self):
        # フィードバック分類キーワード
        self.feedback_categories = {
            "deliverable_changes": ["追加", "削除", "成果物", "アイテム", "項目"],
            "effort_adjustments": ["工数", "日数", "人日", "時間", "期間", "短縮", "延長"],
            "tech_changes": ["技術", "スタック", "フレームワーク", "データベース", "言語"],
            "pricing_adjustments": ["価格", "金額", "単価", "コスト", "料金", "安く", "高く"],
            "assumption_changes": ["前提", "条件", "エンジニア", "レベル", "環境"]
        }
        
        # 緊急度判定キーワード
        self.urgency_keywords = {
            "high": ["緊急", "急いで", "すぐに", "明日まで", "至急"],
            "medium": ["できるだけ早く", "なるべく早く", "早めに"],
            "low": ["時間があるときに", "後で", "いつでも"]
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """フィードバック処理"""
        try:
            user_feedback = state.get("user_feedback", "")
            
            # 空のフィードバックまたは自動承認の場合
            if not user_feedback.strip():
                return {
                    **state,
                    "approved": True,
                    "feedback_analysis": {
                        "original_feedback": "",
                        "detected_categories": [],
                        "specific_requests": [],
                        "urgency_level": "low",
                        "processing_timestamp": datetime.now().isoformat()
                    },
                    "revision_instructions": {},
                    "feedback_processing_timestamp": datetime.now().isoformat()
                }
            
            # フィードバック解析
            feedback_analysis = self._analyze_user_feedback(user_feedback)
            
            # 修正指示生成
            revision_instructions = self._generate_revision_instructions(feedback_analysis)
            
            return {
                **state,
                "feedback_analysis": feedback_analysis,
                "revision_instructions": revision_instructions,
                "feedback_processing_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Feedback processing failed: {str(e)}"
            }
    
    def _analyze_user_feedback(self, feedback: str) -> Dict[str, Any]:
        """フィードバック解析"""
        if not feedback.strip():
            return {
                "original_feedback": feedback,
                "detected_categories": [],
                "specific_requests": [],
                "urgency_level": "low",
                "processing_timestamp": datetime.now().isoformat()
            }
        
        # カテゴリ検出
        detected_categories = []
        for category, keywords in self.feedback_categories.items():
            if any(keyword in feedback for keyword in keywords):
                detected_categories.append(category)
        
        # 具体的な数値要求の抽出
        specific_requests = self._extract_specific_requests(feedback)
        
        # 緊急度評価
        urgency_level = self._assess_urgency_level(feedback)
        
        return {
            "original_feedback": feedback,
            "detected_categories": detected_categories,
            "specific_requests": specific_requests,
            "urgency_level": urgency_level,
            "processing_timestamp": datetime.now().isoformat()
        }
    
    def _extract_specific_requests(self, feedback: str) -> List[Dict[str, str]]:
        """具体的な数値要求の抽出"""
        requests = []
        
        # 工数調整パターン
        effort_patterns = [
            r'(\d+)(人日|日間?)',
            r'(\d+)(時間|h|hour)',
            r'(\d+)(週間?|week)',
            r'(\d+)(ヶ?月|month)'
        ]
        
        for pattern in effort_patterns:
            matches = re.findall(pattern, feedback)
            for match in matches:
                requests.append({
                    "type": "effort_adjustment",
                    "value": match[0],
                    "unit": match[1]
                })
        
        # 金額調整パターン
        price_patterns = [
            r'(\d+)(億|億円)',
            r'(\d+)(万|万円)',
            r'(\d+)(千|千円)',
            r'(\d+)(円|yen)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, feedback)
            for match in matches:
                requests.append({
                    "type": "price_adjustment",
                    "value": match[0],
                    "unit": match[1]
                })
        
        # 比率調整パターン
        ratio_patterns = [
            r'(\d+)(%|パーセント|割)',
            r'(\d+)(倍|x|×)'
        ]
        
        for pattern in ratio_patterns:
            matches = re.findall(pattern, feedback)
            for match in matches:
                requests.append({
                    "type": "ratio_adjustment",
                    "value": match[0],
                    "unit": match[1]
                })
        
        return requests
    
    def _assess_urgency_level(self, feedback: str) -> str:
        """緊急度評価"""
        feedback_lower = feedback.lower()
        
        for level, keywords in self.urgency_keywords.items():
            if any(keyword in feedback_lower for keyword in keywords):
                return level
        
        return "low"  # デフォルト
    
    def _generate_revision_instructions(self, feedback_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """修正指示生成"""
        instructions = {
            "deliverable_changes": [],
            "effort_adjustments": [],
            "tech_assumption_changes": [],
            "pricing_adjustments": [],
            "question_changes": []
        }
        
        detected_categories = feedback_analysis["detected_categories"]
        specific_requests = feedback_analysis["specific_requests"]
        original_feedback = feedback_analysis["original_feedback"]
        
        # カテゴリ別の指示生成
        if "deliverable_changes" in detected_categories:
            instructions["deliverable_changes"] = self._generate_deliverable_instructions(
                original_feedback, specific_requests
            )
        
        if "effort_adjustments" in detected_categories:
            instructions["effort_adjustments"] = self._generate_effort_instructions(
                original_feedback, specific_requests
            )
        
        if "tech_changes" in detected_categories:
            instructions["tech_assumption_changes"] = self._generate_tech_instructions(
                original_feedback, specific_requests
            )
        
        if "pricing_adjustments" in detected_categories:
            instructions["pricing_adjustments"] = self._generate_pricing_instructions(
                original_feedback, specific_requests
            )
        
        return instructions
    
    def _generate_deliverable_instructions(self, feedback: str, requests: List[Dict]) -> List[Dict]:
        """成果物変更指示生成"""
        instructions = []
        
        if any(word in feedback for word in ["追加", "add"]):
            instructions.append({
                "action": "add",
                "description": "成果物を追加する",
                "details": feedback
            })
        
        if any(word in feedback for word in ["削除", "remove", "不要"]):
            instructions.append({
                "action": "remove",
                "description": "成果物を削除する",
                "details": feedback
            })
        
        if any(word in feedback for word in ["変更", "修正", "update"]):
            instructions.append({
                "action": "modify",
                "description": "成果物を修正する",
                "details": feedback
            })
        
        return instructions
    
    def _generate_effort_instructions(self, feedback: str, requests: List[Dict]) -> List[Dict]:
        """工数調整指示生成"""
        instructions = []
        
        # 具体的な数値要求がある場合
        effort_requests = [req for req in requests if req["type"] == "effort_adjustment"]
        for req in effort_requests:
            instructions.append({
                "action": "adjust_effort",
                "target_value": req["value"],
                "target_unit": req["unit"],
                "description": f"工数を{req['value']}{req['unit']}に調整",
                "details": feedback
            })
        
        # 抽象的な調整要求
        if any(word in feedback for word in ["短縮", "減らす", "削減"]):
            instructions.append({
                "action": "reduce_effort",
                "description": "工数を短縮する",
                "details": feedback
            })
        
        if any(word in feedback for word in ["延長", "増やす", "追加"]):
            instructions.append({
                "action": "increase_effort",
                "description": "工数を延長する",
                "details": feedback
            })
        
        return instructions
    
    def _generate_tech_instructions(self, feedback: str, requests: List[Dict]) -> List[Dict]:
        """技術前提変更指示生成"""
        instructions = []
        
        # 技術スタック変更
        if any(word in feedback for word in ["技術", "スタック", "フレームワーク"]):
            instructions.append({
                "action": "change_tech_stack",
                "description": "技術スタックを変更する",
                "details": feedback
            })
        
        # エンジニアレベル変更
        if any(word in feedback for word in ["エンジニア", "レベル", "スキル"]):
            instructions.append({
                "action": "change_engineer_level",
                "description": "エンジニアレベルを変更する",
                "details": feedback
            })
        
        return instructions
    
    def _generate_pricing_instructions(self, feedback: str, requests: List[Dict]) -> List[Dict]:
        """価格調整指示生成"""
        instructions = []
        
        # 具体的な価格要求
        price_requests = [req for req in requests if req["type"] == "price_adjustment"]
        for req in price_requests:
            instructions.append({
                "action": "adjust_price",
                "target_value": req["value"],
                "target_unit": req["unit"],
                "description": f"価格を{req['value']}{req['unit']}に調整",
                "details": feedback
            })
        
        # 抽象的な価格調整
        if any(word in feedback for word in ["安く", "下げる", "削減"]):
            instructions.append({
                "action": "reduce_price",
                "description": "価格を下げる",
                "details": feedback
            })
        
        if any(word in feedback for word in ["高く", "上げる", "増額"]):
            instructions.append({
                "action": "increase_price",
                "description": "価格を上げる",
                "details": feedback
            })
        
        return instructions