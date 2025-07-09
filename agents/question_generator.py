"""
DeliverableEstimate Pro - Question Generator Agent
"""

from datetime import datetime
from typing import Dict, List, Any


class QuestionGenerator:
    """精度向上質問生成エージェント"""
    
    def __init__(self):
        # 質問テンプレート
        self.question_templates = {
            "database_complexity": {
                "question": "{deliverable_name}のデータベース設計で、必要なテーブル数はどれくらいですか？",
                "type": "number",
                "impact": "データベース設計工数に影響",
                "category": "technical_specification",
                "min_value": 1,
                "max_value": 100
            },
            "api_complexity": {
                "question": "{deliverable_name}で必要なAPIエンドポイント数はどれくらいですか？",
                "type": "number", 
                "impact": "API設計・開発工数に影響",
                "category": "technical_specification",
                "min_value": 1,
                "max_value": 200
            },
            "ui_complexity": {
                "question": "{deliverable_name}でテスト対象となるページ数はどれくらいですか？",
                "type": "number",
                "impact": "テスト実装工数に影響", 
                "category": "quality_assurance",
                "min_value": 1,
                "max_value": 500
            },
            "integration_complexity": {
                "question": "{deliverable_name}で必要な外部システム連携はありますか？",
                "type": "choice",
                "options": ["なし", "簡単な連携", "複雑な連携"],
                "impact": "統合テスト工数に影響",
                "category": "system_integration"
            },
            "security_level": {
                "question": "{deliverable_name}のセキュリティ要件レベルはどの程度ですか？",
                "type": "choice",
                "options": ["基本", "標準", "高度"],
                "impact": "セキュリティ実装工数に影響",
                "category": "security_requirement"
            },
            "performance_requirement": {
                "question": "{deliverable_name}のパフォーマンス要件はどの程度ですか？",
                "type": "choice",
                "options": ["標準", "高パフォーマンス", "極めて高い"],
                "impact": "パフォーマンス最適化工数に影響",
                "category": "performance_requirement"
            },
            "data_volume": {
                "question": "{deliverable_name}で扱うデータ量はどの程度を想定していますか？",
                "type": "choice",
                "options": ["小規模", "中規模", "大規模"],
                "impact": "データ処理・最適化工数に影響",
                "category": "data_requirement"
            },
            "user_count": {
                "question": "{deliverable_name}の想定同時利用者数はどれくらいですか？",
                "type": "number",
                "impact": "スケーラビリティ対応工数に影響",
                "category": "scalability_requirement",
                "min_value": 1,
                "max_value": 10000
            }
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """精度向上のための動的質問生成"""
        try:
            analyzed_deliverables = state["analyzed_deliverables"]
            effort_estimates = state["effort_estimates"]
            tech_assumptions = state["tech_assumptions"]
            
            # 不明確な要素の特定
            unclear_elements = self._identify_unclear_elements(
                analyzed_deliverables, effort_estimates
            )
            
            # 動的質問生成
            dynamic_questions = self._generate_dynamic_questions(
                unclear_elements, tech_assumptions
            )
            
            # ユーザーとの対話セッション
            questions_and_answers = self._conduct_qa_session(dynamic_questions)
            
            # 回答に基づく前提条件更新
            finalized_assumptions = self._update_assumptions_from_answers(
                tech_assumptions, questions_and_answers
            )
            
            return {
                **state,
                "questions_and_answers": questions_and_answers,
                "finalized_assumptions": finalized_assumptions,
                "unclear_elements": unclear_elements,
                "qa_session_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                **state,
                "error": f"Question generation failed: {str(e)}"
            }
    
    def _identify_unclear_elements(self, analyzed_deliverables: List[Dict], effort_estimates: List[Dict]) -> List[Dict]:
        """不明確な要素の特定"""
        unclear_elements = []
        
        for deliverable in analyzed_deliverables:
            name = deliverable["name"].lower()
            description = deliverable["description"].lower()
            category = deliverable["category"]
            
            # データベース関連の不明確要素
            if (category == "database" or 
                any(keyword in name + description for keyword in ["データベース", "db", "テーブル"])):
                unclear_elements.append({
                    "type": "database_complexity",
                    "deliverable_name": deliverable["name"],
                    "reason": "データベース設計の詳細仕様が不明確"
                })
            
            # API関連の不明確要素
            if (category in ["backend_development", "integration"] or
                any(keyword in name + description for keyword in ["api", "サーバー", "連携"])):
                unclear_elements.append({
                    "type": "api_complexity",
                    "deliverable_name": deliverable["name"],
                    "reason": "API設計の詳細仕様が不明確"
                })
            
            # UI/テスト関連の不明確要素
            if (category in ["frontend_development", "testing"] or
                any(keyword in name + description for keyword in ["画面", "ui", "テスト", "ページ"])):
                unclear_elements.append({
                    "type": "ui_complexity",
                    "deliverable_name": deliverable["name"],
                    "reason": "UI/テスト対象の詳細仕様が不明確"
                })
            
            # セキュリティ関連の不明確要素
            if (category == "security" or
                any(keyword in name + description for keyword in ["セキュリティ", "認証", "権限"])):
                unclear_elements.append({
                    "type": "security_level",
                    "deliverable_name": deliverable["name"],
                    "reason": "セキュリティ要件レベルが不明確"
                })
            
            # パフォーマンス関連の不明確要素
            if any(keyword in name + description for keyword in ["パフォーマンス", "performance", "高速", "最適化"]):
                unclear_elements.append({
                    "type": "performance_requirement",
                    "deliverable_name": deliverable["name"],
                    "reason": "パフォーマンス要件が不明確"
                })
            
            # 統合・連携関連の不明確要素
            if (category == "integration" or
                any(keyword in name + description for keyword in ["連携", "統合", "外部", "third-party"])):
                unclear_elements.append({
                    "type": "integration_complexity",
                    "deliverable_name": deliverable["name"],
                    "reason": "外部システム連携の詳細が不明確"
                })
        
        # 工数見積から高リスク・低信頼度アイテムを特定
        for estimate in effort_estimates:
            confidence = int(estimate["confidence_level"].rstrip('%'))
            if confidence < 75:
                unclear_elements.append({
                    "type": "data_volume",
                    "deliverable_name": estimate["name"],
                    "reason": f"信頼度{confidence}%と低く、データ量の確認が必要"
                })
        
        return unclear_elements
    
    def _generate_dynamic_questions(self, unclear_elements: List[Dict], tech_assumptions: Dict) -> List[Dict]:
        """動的質問生成"""
        questions = []
        
        # 重複除去のためのセット
        asked_combinations = set()
        
        for element in unclear_elements:
            question_type = element["type"]
            deliverable_name = element["deliverable_name"]
            
            # 重複チェック
            combination = f"{question_type}_{deliverable_name}"
            if combination in asked_combinations:
                continue
            asked_combinations.add(combination)
            
            if question_type in self.question_templates:
                template = self.question_templates[question_type]
                
                question = {
                    "id": f"{question_type}_{len(questions)}",
                    "question": template["question"].format(deliverable_name=deliverable_name),
                    "type": template["type"],
                    "impact": template["impact"],
                    "category": template["category"],
                    "deliverable_name": deliverable_name,
                    "unclear_reason": element["reason"]
                }
                
                # typeに応じた追加設定
                if template["type"] == "number":
                    question["default"] = tech_assumptions.get(
                        self._get_assumption_key(question_type), 20
                    )
                    question["min_value"] = template.get("min_value", 1)
                    question["max_value"] = template.get("max_value", 100)
                elif template["type"] == "choice":
                    question["options"] = template["options"]
                    question["default"] = template["options"][1]  # 中間値をデフォルト
                
                questions.append(question)
        
        # 質問数制限（最大10個）
        if len(questions) > 10:
            # 重要度順にソート（高リスク・低信頼度を優先）
            questions = sorted(questions, key=lambda q: self._get_question_priority(q), reverse=True)[:10]
        
        return questions
    
    def _get_assumption_key(self, question_type: str) -> str:
        """質問タイプから前提条件キーを取得"""
        mapping = {
            "database_complexity": "database_tables",
            "api_complexity": "api_endpoints",
            "ui_complexity": "test_pages",
            "user_count": "concurrent_users"
        }
        return mapping.get(question_type, "default_value")
    
    def _get_question_priority(self, question: Dict) -> int:
        """質問の重要度を算出"""
        priority = 0
        
        # カテゴリ別優先度
        category_priority = {
            "technical_specification": 3,
            "quality_assurance": 2,
            "system_integration": 3,
            "security_requirement": 2,
            "performance_requirement": 2,
            "data_requirement": 1,
            "scalability_requirement": 1
        }
        
        priority += category_priority.get(question["category"], 1)
        
        # 成果物名に基づく優先度
        deliverable_name = question["deliverable_name"].lower()
        if any(keyword in deliverable_name for keyword in ["設計", "仕様", "api"]):
            priority += 2
        elif any(keyword in deliverable_name for keyword in ["開発", "実装"]):
            priority += 1
        
        return priority
    
    def _conduct_qa_session(self, questions: List[Dict]) -> List[Dict]:
        """質問応答セッションの実行"""
        questions_and_answers = []
        
        if not questions:
            return questions_and_answers
        
        print("\n❓ 見積精度向上のための質問")
        print("=" * 50)
        print("より正確な見積のため、いくつか質問させていただきます。")
        print("不明な場合はEnterでデフォルト値を使用します。\n")
        
        for i, question in enumerate(questions, 1):
            print(f"\n質問 {i}/{len(questions)}:")
            print(f"{question['question']}")
            print(f"影響: {question['impact']}")
            
            if question["type"] == "number":
                print(f"デフォルト: {question['default']}")
                print(f"範囲: {question['min_value']} - {question['max_value']}")
                
                while True:
                    answer = input("回答: ")
                    if answer.strip() == "":
                        answer = question["default"]
                        break
                    
                    try:
                        answer = int(answer)
                        if question["min_value"] <= answer <= question["max_value"]:
                            break
                        else:
                            print(f"範囲外です。{question['min_value']} - {question['max_value']}の範囲で入力してください。")
                    except ValueError:
                        print("数値を入力してください。")
            
            elif question["type"] == "choice":
                print(f"選択肢: {', '.join(question['options'])}")
                print(f"デフォルト: {question['default']}")
                
                while True:
                    answer = input("回答: ")
                    if answer.strip() == "":
                        answer = question["default"]
                        break
                    elif answer in question["options"]:
                        break
                    else:
                        print(f"選択肢から選んでください: {', '.join(question['options'])}")
            
            questions_and_answers.append({
                "question_id": question["id"],
                "question": question["question"],
                "answer": answer,
                "impact": question["impact"],
                "category": question["category"],
                "deliverable_name": question["deliverable_name"]
            })
        
        return questions_and_answers
    
    def _update_assumptions_from_answers(self, tech_assumptions: Dict, questions_and_answers: List[Dict]) -> Dict:
        """回答に基づく前提条件の更新"""
        finalized_assumptions = tech_assumptions.copy()
        
        for qa in questions_and_answers:
            question_id = qa["question_id"]
            answer = qa["answer"]
            
            # 質問IDからアップデート対象を特定
            if "database_complexity" in question_id:
                finalized_assumptions["database_tables"] = answer
            elif "api_complexity" in question_id:
                finalized_assumptions["api_endpoints"] = answer
            elif "ui_complexity" in question_id:
                finalized_assumptions["test_pages"] = answer
            elif "user_count" in question_id:
                finalized_assumptions["concurrent_users"] = answer
            elif "security_level" in question_id:
                finalized_assumptions["security_level"] = answer
            elif "performance_requirement" in question_id:
                finalized_assumptions["performance_level"] = answer
            elif "data_volume" in question_id:
                finalized_assumptions["data_volume"] = answer
            elif "integration_complexity" in question_id:
                finalized_assumptions["integration_complexity"] = answer
        
        # 質問回答の統計情報を追加
        finalized_assumptions["qa_session_stats"] = {
            "total_questions": len(questions_and_answers),
            "answered_questions": len([qa for qa in questions_and_answers if qa["answer"] != ""]),
            "session_timestamp": datetime.now().isoformat()
        }
        
        return finalized_assumptions