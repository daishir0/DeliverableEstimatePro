# LangGraph実装設計

## 🔄 LangGraphワークフロー設計

### **状態管理システム**

#### **システム状態定義**
```python
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

class EstimationState(TypedDict):
    # 入力データ
    excel_input: str
    system_requirements: str
    env_config: Dict[str, Any]
    
    # エージェント処理結果
    deliverables: List[Dict[str, Any]]
    analyzed_deliverables: List[Dict[str, Any]]
    effort_estimates: List[Dict[str, Any]]
    questions_and_answers: List[Dict[str, Any]]
    cost_calculation: Dict[str, Any]
    
    # ユーザーインタラクション
    user_feedback: str
    approved: bool
    iteration_count: int
    
    # 最終出力
    final_excel_output: str
    session_metadata: Dict[str, Any]
```

#### **ワークフローグラフ定義**
```python
def create_estimation_workflow():
    """DeliverableEstimate Proのメインワークフローを作成"""
    workflow = StateGraph(EstimationState)
    
    # エージェントノード追加
    workflow.add_node("input_processor", input_processor_node)
    workflow.add_node("deliverable_analyzer", deliverable_analyzer_node)
    workflow.add_node("effort_estimator", effort_estimator_node)
    workflow.add_node("question_generator", question_generator_node)
    workflow.add_node("cost_calculator", cost_calculator_node)
    workflow.add_node("report_generator", report_generator_node)
    workflow.add_node("user_feedback_processor", user_feedback_processor_node)
    
    # エントリーポイント設定
    workflow.set_entry_point("input_processor")
    
    # シーケンシャルエッジ
    workflow.add_edge("input_processor", "deliverable_analyzer")
    workflow.add_edge("deliverable_analyzer", "effort_estimator")
    workflow.add_edge("effort_estimator", "question_generator")
    workflow.add_edge("question_generator", "cost_calculator")
    workflow.add_edge("cost_calculator", "report_generator")
    
    # 条件分岐エッジ
    workflow.add_conditional_edges(
        "report_generator",
        lambda state: "approved" if state.get("approved", False) else "feedback",
        {
            "approved": END,
            "feedback": "user_feedback_processor"
        }
    )
    
    workflow.add_conditional_edges(
        "user_feedback_processor",
        lambda state: determine_revision_target(state),
        {
            "deliverable_revision": "deliverable_analyzer",
            "effort_revision": "effort_estimator", 
            "question_revision": "question_generator",
            "complete_revision": "input_processor"
        }
    )
    
    return workflow.compile()
```

## 🔄 エージェントノード実装

### **Input Processor Node**
```python
def input_processor_node(state: EstimationState) -> EstimationState:
    """入力データの処理と構造化"""
    try:
        # Excel ファイル読み込み
        excel_data = load_excel_file(state["excel_input"])
        
        # システム要件テキスト解析
        project_context = parse_system_requirements(state["system_requirements"])
        
        # 環境設定読み込み
        env_config = load_environment_config()
        
        # データバリデーション
        validation_result = validate_input_data(excel_data, project_context, env_config)
        
        # デフォルト技術前提条件設定
        tech_assumptions = set_default_tech_assumptions(project_context)
        
        return {
            **state,
            "deliverables": excel_data["deliverables"],
            "project_context": project_context,
            "env_config": env_config,
            "tech_assumptions": tech_assumptions,
            "validation_status": validation_result,
            "session_metadata": {
                "processing_timestamp": datetime.now().isoformat(),
                "input_file": state["excel_input"],
                "validation_passed": validation_result["all_valid"]
            }
        }
    except Exception as e:
        return {
            **state,
            "error": f"Input processing failed: {str(e)}",
            "validation_status": {"all_valid": False, "error": str(e)}
        }
```

### **Deliverable Analyzer Node**
```python
def deliverable_analyzer_node(state: EstimationState) -> EstimationState:
    """成果物の詳細分析と複雑度評価"""
    try:
        deliverables = state["deliverables"]
        project_context = state["project_context"]
        tech_assumptions = state["tech_assumptions"]
        
        analyzed_deliverables = []
        
        for deliverable in deliverables:
            # 成果物の意味解析
            semantic_analysis = analyze_deliverable_semantics(deliverable)
            
            # 複雑度レベル判定
            complexity_level = determine_complexity_level(
                deliverable, project_context, tech_assumptions
            )
            
            # リスクファクター特定
            risk_factors = identify_risk_factors(deliverable, project_context)
            
            # 依存関係分析
            dependencies = analyze_dependencies(deliverable, deliverables)
            
            # 過去実績データマッチング
            historical_matches = find_historical_matches(deliverable)
            
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
        overall_assessment = generate_overall_assessment(analyzed_deliverables)
        
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
```

### **Effort Estimator Node**
```python
def effort_estimator_node(state: EstimationState) -> EstimationState:
    """工数見積とリスク調整"""
    try:
        analyzed_deliverables = state["analyzed_deliverables"]
        project_context = state["project_context"]
        tech_assumptions = state["tech_assumptions"]
        
        effort_estimates = []
        
        for deliverable in analyzed_deliverables:
            # 基礎工数算出
            base_effort = calculate_base_effort(
                deliverable["category"], 
                deliverable["complexity_level"]
            )
            
            # 複雑度調整
            complexity_adjustment = calculate_complexity_adjustment(
                deliverable["complexity_level"],
                project_context["complexity"]
            )
            
            # リスクバッファ計算
            risk_buffer = calculate_risk_buffer(deliverable["risk_factors"])
            
            # 過去実績データ検証
            historical_validation = validate_against_historical_data(
                deliverable, base_effort, complexity_adjustment
            )
            
            # 最終工数算出
            final_effort = base_effort * complexity_adjustment + risk_buffer
            
            # 信頼度算出
            confidence_level = calculate_confidence_level(
                deliverable, historical_validation, risk_buffer
            )
            
            effort_estimates.append({
                "name": deliverable["name"],
                "base_effort_days": base_effort,
                "complexity_adjustment": complexity_adjustment,
                "risk_buffer": risk_buffer,
                "final_effort_days": final_effort,
                "confidence_level": confidence_level,
                "estimation_rationale": generate_estimation_rationale(
                    deliverable, base_effort, complexity_adjustment, risk_buffer
                ),
                "historical_validation": historical_validation
            })
        
        # 全体サマリー生成
        summary = generate_effort_summary(effort_estimates)
        
        return {
            **state,
            "effort_estimates": effort_estimates,
            "effort_summary": summary,
            "tech_assumptions_used": tech_assumptions,
            "estimation_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            **state,
            "error": f"Effort estimation failed: {str(e)}"
        }
```

### **Question Generator Node**
```python
def question_generator_node(state: EstimationState) -> EstimationState:
    """精度向上のための動的質問生成"""
    try:
        analyzed_deliverables = state["analyzed_deliverables"]
        effort_estimates = state["effort_estimates"]
        tech_assumptions = state["tech_assumptions"]
        
        # 不明確な要素の特定
        unclear_elements = identify_unclear_elements(
            analyzed_deliverables, effort_estimates
        )
        
        # 動的質問生成
        dynamic_questions = generate_dynamic_questions(
            unclear_elements, tech_assumptions
        )
        
        # ユーザーとの対話セッション
        questions_and_answers = conduct_qa_session(dynamic_questions)
        
        # 回答に基づく前提条件更新
        finalized_assumptions = update_assumptions_from_answers(
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
```

### **Cost Calculator Node**
```python
def cost_calculator_node(state: EstimationState) -> EstimationState:
    """コスト算出と財務サマリー生成"""
    try:
        effort_estimates = state["effort_estimates"]
        env_config = state["env_config"]
        
        deliverable_costs = []
        
        for estimate in effort_estimates:
            # 基本金額算出
            amount = estimate["final_effort_days"] * env_config["daily_rate"]
            
            deliverable_costs.append({
                "name": estimate["name"],
                "effort_days": estimate["final_effort_days"],
                "daily_rate": env_config["daily_rate"],
                "amount": amount,
                "confidence_level": estimate["confidence_level"]
            })
        
        # 財務サマリー算出
        subtotal = sum(cost["amount"] for cost in deliverable_costs)
        tax_amount = subtotal * env_config["tax_rate"]
        total_amount = subtotal + tax_amount
        total_effort_days = sum(cost["effort_days"] for cost in deliverable_costs)
        
        financial_summary = {
            "subtotal": subtotal,
            "tax_rate": env_config["tax_rate"],
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "total_effort_days": total_effort_days,
            "average_daily_rate": env_config["daily_rate"],
            "currency": env_config["currency"]
        }
        
        # コスト分析
        cost_analysis = generate_cost_analysis(deliverable_costs, financial_summary)
        
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
```

### **Report Generator Node**
```python
def report_generator_node(state: EstimationState) -> EstimationState:
    """見積書表示とユーザー承認処理"""
    try:
        cost_calculation = state["cost_calculation"]
        finalized_assumptions = state["finalized_assumptions"]
        env_config = state["env_config"]
        
        # コンソール見積書表示
        display_estimation_report(cost_calculation, finalized_assumptions)
        
        # ユーザー承認プロセス
        approval_result = get_user_approval()
        
        if approval_result["approved"]:
            # Excel出力実行
            excel_output = generate_excel_output(
                state["deliverables"],
                cost_calculation,
                finalized_assumptions,
                env_config
            )
            
            return {
                **state,
                "approved": True,
                "final_excel_output": excel_output["file_path"],
                "excel_generation_metadata": excel_output["metadata"],
                "completion_timestamp": datetime.now().isoformat()
            }
        else:
            return {
                **state,
                "approved": False,
                "user_feedback": approval_result["feedback"],
                "iteration_count": state.get("iteration_count", 0) + 1
            }
    except Exception as e:
        return {
            **state,
            "error": f"Report generation failed: {str(e)}"
        }
```

## 🔄 フィードバックループ実装

### **ユーザーフィードバック処理**
```python
def user_feedback_processor_node(state: EstimationState) -> EstimationState:
    """ユーザーフィードバックの解析と修正指示生成"""
    try:
        user_feedback = state["user_feedback"]
        
        # フィードバック解析
        feedback_analysis = analyze_user_feedback(user_feedback)
        
        # 修正指示生成
        revision_instructions = generate_revision_instructions(feedback_analysis)
        
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

def determine_revision_target(state: EstimationState) -> str:
    """フィードバックに基づく修正対象エージェントの決定"""
    revision_instructions = state.get("revision_instructions", {})
    
    if revision_instructions.get("deliverable_changes"):
        return "deliverable_revision"
    elif revision_instructions.get("effort_adjustments"):
        return "effort_revision"
    elif revision_instructions.get("question_changes"):
        return "question_revision"
    else:
        return "complete_revision"
```

## 🔒 メモリ管理とチェックポイント

### **チェックポイント設定**
```python
from langgraph.checkpoint.memory import MemorySaver

def create_estimation_workflow_with_checkpoints():
    """チェックポイント機能付きワークフロー作成"""
    workflow = create_estimation_workflow()
    
    # メモリセーバー設定
    memory = MemorySaver()
    
    # チェックポイント付きコンパイル
    return workflow.compile(checkpointer=memory)
```

### **セッション管理**
```python
class EstimationSession:
    """見積セッション管理クラス"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.workflow = create_estimation_workflow_with_checkpoints()
        self.thread_config = {"configurable": {"thread_id": self.session_id}}
    
    def start_estimation(self, excel_file: str, requirements: str):
        """見積セッション開始"""
        initial_state = {
            "excel_input": excel_file,
            "system_requirements": requirements,
            "iteration_count": 0,
            "approved": False
        }
        
        return self.workflow.invoke(initial_state, config=self.thread_config)
    
    def get_session_history(self):
        """セッション履歴取得"""
        return self.workflow.get_state_history(config=self.thread_config)
    
    def resume_session(self, user_input: str):
        """セッション継続"""
        current_state = self.workflow.get_state(config=self.thread_config)
        
        updated_state = {
            **current_state.values,
            "user_feedback": user_input
        }
        
        return self.workflow.invoke(updated_state, config=self.thread_config)
```

## 🚀 ワークフロー実行例

### **基本実行例**
```python
def main():
    """メイン実行関数"""
    # セッション作成
    session = EstimationSession()
    
    # 見積セッション開始
    result = session.start_estimation(
        excel_file="input.xlsx",
        requirements="ECサイトの構築プロジェクト"
    )
    
    # 結果出力
    if result["approved"]:
        print(f"見積完了: {result['final_excel_output']}")
    else:
        print(f"修正が必要です: {result['user_feedback']}")
    
    return result

if __name__ == "__main__":
    result = main()
```

### **エラーハンドリング例**
```python
def run_estimation_with_error_handling():
    """エラーハンドリング付き実行"""
    try:
        session = EstimationSession()
        result = session.start_estimation("input.xlsx", "Project requirements")
        
        # エラーチェック
        if "error" in result:
            print(f"エラー発生: {result['error']}")
            return None
        
        return result
        
    except Exception as e:
        print(f"システムエラー: {str(e)}")
        return None
```

---
**作成日**: 2025年7月9日  
**バージョン**: 1.0