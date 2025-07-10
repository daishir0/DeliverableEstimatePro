"""
DeliverableEstimate Pro - LangGraph Workflow Implementation
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents import (
    InputProcessor,
    DeliverableAnalyzer,
    EffortEstimator,
    QuestionGenerator,
    ReportGenerator
)
from tools.cost_calculator import CostCalculator
from hitl.feedback_processor import FeedbackProcessor


class EstimationState(TypedDict):
    """見積システムの状態定義"""
    # 入力データ
    excel_input: str
    system_requirements: str
    
    # エージェント処理結果
    deliverables: List[Dict[str, Any]]
    analyzed_deliverables: List[Dict[str, Any]]
    effort_estimates: List[Dict[str, Any]]
    questions_and_answers: List[Dict[str, Any]]
    cost_calculation: Dict[str, Any]
    
    # 環境・設定
    env_config: Dict[str, Any]
    tech_assumptions: Dict[str, Any]
    finalized_assumptions: Dict[str, Any]
    
    # ユーザーインタラクション
    user_feedback: str
    approved: bool
    iteration_count: int
    
    # 最終出力
    final_excel_output: str
    session_metadata: Dict[str, Any]
    
    # エラーハンドリング
    error: str


class EstimationWorkflow:
    """見積ワークフロー管理クラス"""
    
    def __init__(self):
        self.input_processor = InputProcessor()
        self.deliverable_analyzer = DeliverableAnalyzer()
        self.effort_estimator = EffortEstimator()
        self.question_generator = QuestionGenerator()
        self.cost_calculator = CostCalculator()
        self.report_generator = ReportGenerator()
        self.feedback_processor = FeedbackProcessor()
        
        # ワークフローの構築
        self.workflow = self._create_workflow()
        
    def _create_workflow(self) -> StateGraph:
        """LangGraphワークフローの作成"""
        workflow = StateGraph(EstimationState)
        
        # ノード追加
        workflow.add_node("input_processor", self._input_processor_node)
        workflow.add_node("deliverable_analyzer", self._deliverable_analyzer_node)
        workflow.add_node("effort_estimator", self._effort_estimator_node)
        workflow.add_node("question_generator", self._question_generator_node)
        workflow.add_node("cost_calculator", self._cost_calculator_node)
        workflow.add_node("report_generator", self._report_generator_node)
        workflow.add_node("feedback_processor", self._feedback_processor_node)
        
        # エントリーポイント
        workflow.set_entry_point("input_processor")
        
        # シーケンシャルフロー
        workflow.add_edge("input_processor", "deliverable_analyzer")
        workflow.add_edge("deliverable_analyzer", "effort_estimator")
        workflow.add_edge("effort_estimator", "question_generator")
        workflow.add_edge("question_generator", "cost_calculator")
        workflow.add_edge("cost_calculator", "report_generator")
        
        # 条件分岐: 承認/修正
        workflow.add_conditional_edges(
            "report_generator",
            self._should_continue_or_end,
            {
                "approved": END,
                "feedback": "feedback_processor"
            }
        )
        
        # フィードバック処理後のルーティング（再帰制限対応）
        workflow.add_conditional_edges(
            "feedback_processor",
            self._determine_revision_target,
            {
                "deliverable_revision": "deliverable_analyzer",
                "effort_revision": "effort_estimator",
                "question_revision": "question_generator",
                "complete_revision": "input_processor",
                "max_iterations": END
            }
        )
        
        return workflow
    
    def _input_processor_node(self, state: EstimationState) -> EstimationState:
        """入力処理ノード"""
        print("🔄 入力データを処理中...")
        return self.input_processor.process(state)
    
    def _deliverable_analyzer_node(self, state: EstimationState) -> EstimationState:
        """成果物分析ノード"""
        print("🔍 成果物を分析中...")
        return self.deliverable_analyzer.process(state)
    
    def _effort_estimator_node(self, state: EstimationState) -> EstimationState:
        """工数見積ノード"""
        print("⏱️ 工数を見積中...")
        return self.effort_estimator.process(state)
    
    def _question_generator_node(self, state: EstimationState) -> EstimationState:
        """質問生成ノード"""
        print("❓ 精度向上のための質問を生成中...")
        return self.question_generator.process(state)
    
    def _cost_calculator_node(self, state: EstimationState) -> EstimationState:
        """コスト計算ノード"""
        print("💰 コストを計算中...")
        return self.cost_calculator.process(state)
    
    def _report_generator_node(self, state: EstimationState) -> EstimationState:
        """レポート生成ノード"""
        print("📊 見積書を生成中...")
        return self.report_generator.process(state)
    
    def _feedback_processor_node(self, state: EstimationState) -> EstimationState:
        """フィードバック処理ノード"""
        print("🔄 フィードバックを処理中...")
        return self.feedback_processor.process(state)
    
    def _should_continue_or_end(self, state: EstimationState) -> str:
        """承認/修正の判定"""
        if state.get("approved", False):
            return "approved"
        else:
            return "feedback"
    
    def _determine_revision_target(self, state: EstimationState) -> str:
        """修正対象の決定（再帰制限対応）"""
        # 反復回数チェック
        current_iterations = state.get("iteration_count", 0)
        max_iterations = 5  # 最大反復回数
        
        if current_iterations >= max_iterations:
            print(f"⚠️ 最大反復回数 ({max_iterations}) に達しました。処理を終了します。")
            return "max_iterations"
        
        feedback_analysis = state.get("feedback_analysis", {})
        detected_categories = feedback_analysis.get("detected_categories", [])
        
        if "deliverable_changes" in detected_categories:
            return "deliverable_revision"
        elif "effort_adjustments" in detected_categories:
            return "effort_revision"
        elif "tech_changes" in detected_categories:
            return "question_revision"
        else:
            return "complete_revision"
    
    def compile(self):
        """ワークフローのコンパイル"""
        return self.workflow.compile()


class EstimationSession:
    """見積セッション管理"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.workflow = EstimationWorkflow()
        self.compiled_workflow = self.workflow.compile()
        self.thread_config = {"configurable": {"thread_id": self.session_id}}
        
    def start_estimation(self, excel_file: str, requirements: str) -> Dict[str, Any]:
        """見積セッションの開始"""
        print(f"🚀 見積セッションを開始します (ID: {self.session_id})")
        print(f"📄 入力ファイル: {excel_file}")
        print(f"📝 システム要件: {requirements[:100]}...")
        
        initial_state = {
            "excel_input": excel_file,
            "system_requirements": requirements,
            "iteration_count": 0,
            "approved": False,
            "user_feedback": "",
            "error": "",
            "session_metadata": {
                "session_id": self.session_id,
                "start_time": datetime.now().isoformat()
            }
        }
        
        try:
            result = self.compiled_workflow.invoke(initial_state, config={"recursion_limit": 50})
            
            # 結果の後処理
            if result.get("approved"):
                print(f"✅ 見積が承認されました!")
                print(f"📊 出力ファイル: {result.get('final_excel_output')}")
            else:
                print(f"🔄 見積が修正されました (反復回数: {result.get('iteration_count', 0)})")
            
            return result
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            return {
                **initial_state,
                "error": str(e),
                "approved": False
            }
    
    def get_session_history(self) -> List[Dict]:
        """セッション履歴の取得"""
        try:
            return list(self.compiled_workflow.get_state_history(config=self.thread_config))
        except Exception as e:
            print(f"履歴取得エラー: {str(e)}")
            return []
    
    def resume_session(self, user_input: str) -> Dict[str, Any]:
        """セッションの継続"""
        try:
            current_state = self.compiled_workflow.get_state(config=self.thread_config)
            
            updated_state = {
                **current_state.values,
                "user_feedback": user_input,
                "iteration_count": current_state.values.get("iteration_count", 0) + 1
            }
            
            return self.compiled_workflow.invoke(updated_state, config={**self.thread_config, "recursion_limit": 50})
            
        except Exception as e:
            print(f"セッション継続エラー: {str(e)}")
            return {"error": str(e), "approved": False}


# メモリ付きワークフローの作成
class EstimationSessionWithMemory(EstimationSession):
    """メモリ付き見積セッション"""
    
    def __init__(self, session_id: str = None):
        super().__init__(session_id)
        
        # メモリセーバー付きでワークフローを再コンパイル
        memory = MemorySaver()
        self.compiled_workflow = self.workflow.workflow.compile(checkpointer=memory)
        
    def get_memory_state(self) -> Dict[str, Any]:
        """メモリ状態の取得"""
        try:
            return self.compiled_workflow.get_state(config=self.thread_config).values
        except Exception as e:
            print(f"メモリ状態取得エラー: {str(e)}")
            return {}


# エラーハンドリング付きワークフロー実行
def run_estimation_with_error_handling(excel_file: str, requirements: str) -> Dict[str, Any]:
    """エラーハンドリング付きの見積実行"""
    try:
        session = EstimationSession()
        result = session.start_estimation(excel_file, requirements)
        
        if result.get("error"):
            print(f"⚠️ 処理中にエラーが発生しました: {result['error']}")
            return {"success": False, "error": result["error"]}
        
        return {"success": True, "result": result}
        
    except Exception as e:
        print(f"❌ システムエラーが発生しました: {str(e)}")
        return {"success": False, "error": str(e)}


# 使用例
if __name__ == "__main__":
    # 基本的な使用例
    result = run_estimation_with_error_handling(
        excel_file="input/sample_input.xlsx",
        requirements="ECサイトの構築プロジェクト"
    )
    
    if result["success"]:
        print("見積処理が完了しました！")
    else:
        print(f"見積処理に失敗しました: {result['error']}")