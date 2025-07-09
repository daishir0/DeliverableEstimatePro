# Human-in-the-Loop設計

## 👤 HITL概要

### **Human-in-the-Loopの目的**
- AIの自動判断と人間の経験・直感の最適な組み合わせ
- 見積精度の継続的改善とカスタマイゼーション
- ビジネスコンテキストに応じた柔軟な対応
- ユーザーが納得できる見積書の作成

### **HITL実装ポイント**
1. **Report Generatorでのユーザー承認** - 最終見積書の品質チェック
2. **フィードバックループ** - 修正・改善の繰り返しプロセス
3. **動的質問応答** - Question Generatorでの精度向上
4. **カスタム前提条件** - プロジェクト固有の調整

---

## 📊 HITL-1: 見積結果プレビューと承認

### **実装ポイント: Report Generator**

#### **目的**
- 最終見積書の品質チェック
- ビジネスコンテキストに応じた最終調整
- ユーザーが納得できる見積書の作成

#### **コンソール表示内容**
```python
def display_estimation_preview(state):
    """見積書プレビュー表示"""
    cost_calculation = state['cost_calculation']
    finalized_assumptions = state['finalized_assumptions']
    
    print("\\n📊 見積書プレビュー")
    print("=" * 60)
    
    # 成果物別見積表示
    print("📋 成果物別見積:")
    for item in cost_calculation['deliverable_costs']:
        print(f"  {item['name']}: {item['effort_days']}人日 → {item['amount']:,}円")
    
    # 技術前提条件表示
    print(f"\\n🛠️ 技術前提条件:")
    assumptions = finalized_assumptions
    print(f"  エンジニアレベル: {assumptions['engineer_level']}")
    print(f"  技術スタック: {assumptions['tech_stack']}")
    print(f"  データベーステーブル: {assumptions['database_tables']}テーブル")
    print(f"  APIエンドポイント: {assumptions['api_endpoints']}個")
    
    # 財務サマリー
    summary = cost_calculation['financial_summary']
    print(f"\\n💰 財務サマリー:")
    print(f"  小計: {summary['subtotal']:,}円")
    print(f"  税額({summary['tax_rate']*100:.0f}%): {summary['tax_amount']:,}円")
    print(f"  総額: {summary['total_amount']:,}円")
    print(f"  総工数: {summary['total_effort_days']}人日")
    
    # リスクアラート
    high_risk_items = [item for item in cost_calculation['deliverable_costs'] 
                      if item['confidence_level'] and int(item['confidence_level'].rstrip('%')) < 80]
    if high_risk_items:
        print(f"\\n⚠️ リスクアラート:")
        for item in high_risk_items:
            print(f"  {item['name']}: 信頼度{item['confidence_level']}")
```

#### **ユーザー承認プロセス**
```python
def get_user_approval():
    """ユーザー承認プロセス"""
    approval = input("""
🔍 見積書の確認をお願いします:

この見積書で問題ありませんか？
1. はい（Yes）- Excel出力して終了
2. いいえ（No）- 修正・調整が必要

選択（Y/N）: """).lower()
    
    if approval in ['y', 'yes', 'はい']:
        return {
            "approved": True,
            "action": "generate_excel"
        }
    else:
        # 詳細フィードバック収集
        feedback = input("""
修正したい項目を選択してください:

1. 成果物の追加・削除
2. 技術前提条件の変更
3. 工数調整
4. 価格調整
5. その他

修正内容を詳しく記入: """)
        
        return {
            "approved": False,
            "feedback": feedback,
            "action": "revise_estimate"
        }
```

---

## 🔄 HITL-2: フィードバックループ処理

### **実装ポイント: User Feedback Processor**

#### **目的**
- ユーザーフィードバックの構造化と解析
- 適切なエージェントへのルーティング
- 修正指示の精密な伝達

#### **フィードバック解析**
```python
def analyze_user_feedback(feedback: str) -> Dict[str, Any]:
    """ユーザーフィードバックの構造化解析"""
    
    # キーワードベース分類
    feedback_categories = {
        "deliverable_changes": ["追加", "削除", "成果物", "アイテム"],
        "effort_adjustments": ["工数", "日数", "人日", "時間", "期間"],
        "tech_changes": ["技術", "スタック", "フレームワーク", "データベース"],
        "pricing_adjustments": ["価格", "金額", "単価", "コスト", "料金"],
        "assumption_changes": ["前提", "条件", "エンジニア", "レベル"]
    }
    
    detected_categories = []
    for category, keywords in feedback_categories.items():
        if any(keyword in feedback for keyword in keywords):
            detected_categories.append(category)
    
    # 具体的な要求の抽出
    specific_requests = extract_specific_requests(feedback)
    
    # 緊急度の評価
    urgency_level = assess_urgency_level(feedback)
    
    return {
        "original_feedback": feedback,
        "detected_categories": detected_categories,
        "specific_requests": specific_requests,
        "urgency_level": urgency_level,
        "processing_timestamp": datetime.now().isoformat()
    }

def extract_specific_requests(feedback: str) -> List[Dict[str, str]]:
    """具体的な要求の抽出"""
    requests = []
    
    # 数値の抽出例
    import re
    
    # 工数調整
    effort_pattern = r'(\\d+)(人日|日間?)'
    effort_matches = re.findall(effort_pattern, feedback)
    for match in effort_matches:
        requests.append({
            "type": "effort_adjustment",
            "value": match[0],
            "unit": match[1]
        })
    
    # 金額調整
    price_pattern = r'(\\d+)(億|万|円)'
    price_matches = re.findall(price_pattern, feedback)
    for match in price_matches:
        requests.append({
            "type": "price_adjustment",
            "value": match[0],
            "unit": match[1]
        })
    
    return requests

def assess_urgency_level(feedback: str) -> str:
    """緊急度の評価"""
    urgent_keywords = ["緊急", "急いで", "すぐに", "明日まで"]
    moderate_keywords = ["できるだけ早く", "なるべく早く"]
    
    if any(keyword in feedback for keyword in urgent_keywords):
        return "high"
    elif any(keyword in feedback for keyword in moderate_keywords):
        return "medium"
    else:
        return "low"
```

#### **修正指示生成**
```python
def generate_revision_instructions(feedback_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """修正指示の生成"""
    instructions = {
        "deliverable_changes": [],
        "effort_adjustments": [],
        "tech_assumption_changes": [],
        "pricing_adjustments": [],
        "question_changes": []
    }
    
    detected_categories = feedback_analysis["detected_categories"]
    specific_requests = feedback_analysis["specific_requests"]
    
    # カテゴリ別指示生成
    if "deliverable_changes" in detected_categories:
        instructions["deliverable_changes"] = generate_deliverable_instructions(specific_requests)
    
    if "effort_adjustments" in detected_categories:
        instructions["effort_adjustments"] = generate_effort_instructions(specific_requests)
    
    if "tech_changes" in detected_categories:
        instructions["tech_assumption_changes"] = generate_tech_instructions(specific_requests)
    
    if "pricing_adjustments" in detected_categories:
        instructions["pricing_adjustments"] = generate_pricing_instructions(specific_requests)
    
    return instructions

def determine_revision_target(state: EstimationState) -> str:
    """修正対象エージェントの決定"""
    revision_instructions = state.get("revision_instructions", {})
    
    if revision_instructions.get("deliverable_changes"):
        return "deliverable_revision"
    elif revision_instructions.get("effort_adjustments"):
        return "effort_revision"
    elif revision_instructions.get("tech_assumption_changes"):
        return "question_revision"
    elif revision_instructions.get("pricing_adjustments"):
        return "effort_revision"  # 価格調整は工数調整で対応
    else:
        return "complete_revision"
```

---

## ❓ HITL-3: 動的質問応答システム

### **実装ポイント: Question Generator**

#### **目的**
- 見積精度を向上させるための動的質問生成
- プロジェクト固有の詳細情報収集
- 不明確な要素の明確化

#### **動的質問生成**
```python
def generate_dynamic_questions(unclear_elements: List[Dict], tech_assumptions: Dict) -> List[Dict]:
    """動的質問生成"""
    questions = []
    
    for element in unclear_elements:
        if element["type"] == "database_complexity":
            questions.append({
                "id": f"db_{element['deliverable_name']}",
                "question": f"{element['deliverable_name']}のデータベース設計で、何種類のテーブルが必要ですか？",
                "type": "number",
                "default": tech_assumptions.get("database_tables", 10),
                "impact": "データベース設計工数に影響",
                "category": "technical_specification"
            })
        
        elif element["type"] == "api_complexity":
            questions.append({
                "id": f"api_{element['deliverable_name']}",
                "question": f"{element['deliverable_name']}で必要なAPIエンドポイント数はどれくらいですか？",
                "type": "number",
                "default": tech_assumptions.get("api_endpoints", 20),
                "impact": "API設計・開発工数に影響",
                "category": "technical_specification"
            })
        
        elif element["type"] == "ui_complexity":
            questions.append({
                "id": f"ui_{element['deliverable_name']}",
                "question": f"{element['deliverable_name']}でテスト対象となるページ数はどれくらいですか？",
                "type": "number",
                "default": tech_assumptions.get("test_pages", 50),
                "impact": "テスト実装工数に影響",
                "category": "quality_assurance"
            })
        
        elif element["type"] == "integration_complexity":
            questions.append({
                "id": f"integration_{element['deliverable_name']}",
                "question": f"{element['deliverable_name']}で必要な外部システム連携はありますか？",
                "type": "choice",
                "options": ["なし", "簡単な連携", "複雑な連携"],
                "default": "簡単な連携",
                "impact": "結合テスト工数に影響",
                "category": "system_integration"
            })
    
    return questions

def conduct_qa_session(questions: List[Dict]) -> List[Dict]:
    """質問応答セッションの実行"""
    questions_and_answers = []
    
    print("\\n❓ 見積精度向上のための質問")
    print("=" * 50)
    print("より正確な見積のため、いくつか質問させていただきます。")
    print("不明な場合はEnterでデフォルト値を使用します。\\n")
    
    for i, question in enumerate(questions, 1):
        print(f"\\n質問 {i}/{len(questions)}:")
        print(f"{question['question']}")
        print(f"影響: {question['impact']}")
        
        if question["type"] == "number":
            print(f"デフォルト: {question['default']}")
            answer = input("回答: ")
            if answer.strip() == "":
                answer = str(question["default"])
            
            # 数値バリデーション
            try:
                answer = int(answer)
            except ValueError:
                answer = question["default"]
        
        elif question["type"] == "choice":
            print(f"選択肢: {', '.join(question['options'])}")
            print(f"デフォルト: {question['default']}")
            answer = input("回答: ")
            if answer.strip() == "" or answer not in question["options"]:
                answer = question["default"]
        
        questions_and_answers.append({
            "question_id": question["id"],
            "question": question["question"],
            "answer": answer,
            "impact": question["impact"],
            "category": question["category"]
        })
    
    return questions_and_answers
```

---

## 🔧 HITL-4: カスタム前提条件設定

### **実装ポイント: Input Processor & Question Generator**

#### **目的**
- プロジェクト固有の特殊条件への対応
- 業界・顧客固有の要件への柔軟な対応
- デフォルト前提条件のカスタマイズ

#### **カスタム前提条件設定**
```python
def customize_tech_assumptions(base_assumptions: Dict, project_context: Dict) -> Dict:
    """プロジェクトコンテキストに応じた前提条件カスタマイズ"""
    
    customized_assumptions = base_assumptions.copy()
    
    # プロジェクトタイプ別調整
    if project_context.get("project_type") == "ECサイト":
        customized_assumptions.update({
            "database_tables": 25,  # ECサイトはテーブル数が多め
            "api_endpoints": 60,    # APIエンドポイントも多め
            "security_requirements": "高セキュリティ",
            "payment_integration": "決済システム連携あり"
        })
    
    elif project_context.get("project_type") == "社内システム":
        customized_assumptions.update({
            "database_tables": 15,  # 社内システムはシンプル
            "api_endpoints": 30,
            "security_requirements": "中セキュリティ",
            "user_training": "ユーザートレーニング必要"
        })
    
    # 複雑度別調整
    complexity_multipliers = {
        "simple": 0.8,
        "medium": 1.0,
        "complex": 1.3,
        "very_complex": 1.6
    }
    
    complexity = project_context.get("complexity", "medium")
    multiplier = complexity_multipliers.get(complexity, 1.0)
    
    customized_assumptions["database_tables"] = int(customized_assumptions["database_tables"] * multiplier)
    customized_assumptions["api_endpoints"] = int(customized_assumptions["api_endpoints"] * multiplier)
    
    return customized_assumptions

def get_custom_assumptions_from_user():
    """ユーザーからのカスタム前提条件入力"""
    print("\\n🔧 カスタム前提条件設定")
    print("=" * 40)
    print("プロジェクト固有の特殊条件がありましたら教えてください。")
    print("一般的な条件でよろしければEnterでスキップできます。\\n")
    
    custom_assumptions = {}
    
    # エンジニアレベルカスタマイズ
    engineer_level = input("エンジニアレベル [デフォルト: Python使用可能な平均的エンジニア]: ")
    if engineer_level.strip():
        custom_assumptions["engineer_level"] = engineer_level
    
    # 技術スタックカスタマイズ
    tech_stack = input("技術スタック [デフォルト: React/Vue.js + Node.js/Python]: ")
    if tech_stack.strip():
        custom_assumptions["tech_stack"] = tech_stack
    
    # データベーステーブル数
    db_tables = input("データベーステーブル数 [デフォルト: 20]: ")
    if db_tables.strip():
        try:
            custom_assumptions["database_tables"] = int(db_tables)
        except ValueError:
            pass
    
    # APIエンドポイント数
    api_endpoints = input("APIエンドポイント数 [デフォルト: 50]: ")
    if api_endpoints.strip():
        try:
            custom_assumptions["api_endpoints"] = int(api_endpoints)
        except ValueError:
            pass
    
    # 特殊要件
    special_requirements = input("特殊要件 (セキュリティ、パフォーマンスなど): ")
    if special_requirements.strip():
        custom_assumptions["special_requirements"] = special_requirements
    
    return custom_assumptions
```

---

## 📊 HITLパフォーマンス指標

### **品質指標**
- ユーザー承認率: > 90%
- フィードバック反映時間: < 5分
- 見積精度向上: 15%以上の改善

### **ユーザーエクスペリエンス指標**
- コンソール対話の理解しやすさ
- フィードバックの簡単さ
- 修正結果の予測可能性

### **システム効率指標**
- フィードバックループ数: 平均 2回以下
- セッション完了時間: < 45分
- システムレスポンス性: < 3秒

---

## 🚀 HITLベストプラクティス

### **ユーザーインターフェース設計**
- クリアで直感的なコンソール表示
- フィードバックの構造化とガイド
- エラーメッセージの明確性

### **フィードバック処理戦略**
- ユーザー意図の正確な把握
- 部分修正と全面修正の適切な判断
- フィードバック履歴の管理と学習

### **システムパフォーマンス最適化**
- フィードバックループの効率化
- ユーザー応答のキャッシュ機能
- システムリソースの最適化

---
**作成日**: 2025年7月9日  
**バージョン**: 1.0