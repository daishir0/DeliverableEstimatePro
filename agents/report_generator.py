"""
DeliverableEstimate Pro - Report Generator Agent
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ReportGenerator:
    """見積書生成・承認管理エージェント"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """見積書生成・承認プロセス"""
        try:
            cost_calculation = state.get("cost_calculation", {})
            finalized_assumptions = state.get("finalized_assumptions", {})
            env_config = state.get("env_config", {})
            
            # 必須データの確認
            if not cost_calculation:
                return {
                    **state,
                    "error": "Cost calculation data is missing"
                }
            
            # コンソール見積書表示
            self._display_estimation_report(cost_calculation, finalized_assumptions)
            
            # ユーザー承認プロセス
            approval_result = self._get_user_approval()
            
            if approval_result["approved"]:
                # Excel出力実行
                excel_output = self._generate_excel_output(
                    state.get("deliverables", []),
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
    
    def _display_estimation_report(self, cost_calculation: Dict, finalized_assumptions: Dict):
        """見積書プレビューの表示"""
        print("\n📊 見積書プレビュー")
        print("=" * 60)
        
        # 成果物別見積表示
        print("📋 成果物別見積:")
        deliverable_costs = cost_calculation['deliverable_costs']
        for item in deliverable_costs:
            print(f"  {item['name']}: {item['effort_days']}人日 → {item['amount']:,}円")
        
        # 技術前提条件表示
        print(f"\n🛠️ 技術前提条件:")
        print(f"  エンジニアレベル: {finalized_assumptions.get('engineer_level', 'N/A')}")
        print(f"  技術スタック: {finalized_assumptions.get('tech_stack', 'N/A')}")
        
        # 数値前提条件
        if 'database_tables' in finalized_assumptions:
            print(f"  データベーステーブル: {finalized_assumptions['database_tables']}テーブル")
        if 'api_endpoints' in finalized_assumptions:
            print(f"  APIエンドポイント: {finalized_assumptions['api_endpoints']}個")
        if 'test_pages' in finalized_assumptions:
            print(f"  テストページ: {finalized_assumptions['test_pages']}ページ")
        
        # 財務サマリー
        summary = cost_calculation['financial_summary']
        print(f"\n💰 財務サマリー:")
        print(f"  小計: {summary['subtotal']:,}円")
        print(f"  税額({summary['tax_rate']*100:.0f}%): {summary['tax_amount']:,}円")
        print(f"  総額: {summary['total_amount']:,}円")
        print(f"  総工数: {summary['total_effort_days']}人日")
        
        # リスクアラート
        high_risk_items = []
        for item in deliverable_costs:
            if item.get('confidence_level'):
                confidence = int(item['confidence_level'].rstrip('%'))
                if confidence < 80:
                    high_risk_items.append(f"{item['name']} (信頼度{confidence}%)")
        
        if high_risk_items:
            print(f"\n⚠️ リスクアラート:")
            for item in high_risk_items:
                print(f"  • {item}")
        
        # 質問応答セッション情報
        qa_stats = finalized_assumptions.get('qa_session_stats', {})
        if qa_stats:
            print(f"\n📝 質問応答セッション:")
            print(f"  質問数: {qa_stats.get('total_questions', 0)}")
            print(f"  回答数: {qa_stats.get('answered_questions', 0)}")
    
    def _get_user_approval(self) -> Dict[str, Any]:
        """ユーザー承認プロセス"""
        approval = input("""
🔍 見積書の確認をお願いします:

この見積書で問題ありませんか？
1. はい（Yes）- Excel出力して終了
2. いいえ（No）- 修正・調整が必要

選択（Y/N）: """).lower()
        
        if approval in ['y', 'yes', 'はい', '1']:
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
    
    def _generate_excel_output(self, deliverables: List[Dict], cost_calculation: Dict, 
                              finalized_assumptions: Dict, env_config: Dict) -> Dict[str, Any]:
        """Excel出力の生成"""
        # タイムスタンプ付きファイル名生成
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}.xlsx"
        file_path = self.output_dir / filename
        
        # 元のデータを復元
        original_data = []
        deliverable_costs = cost_calculation['deliverable_costs']
        
        # 成果物データを結合
        for cost_info in deliverable_costs:
            # 対応する成果物情報を検索
            deliverable_info = next(
                (d for d in deliverables if d.get('name') == cost_info['name']),
                None
            )
            
            description = deliverable_info.get('description', '詳細説明') if deliverable_info else '詳細説明'
            
            original_data.append({
                'A': cost_info['name'],
                'B': description,
                'C': cost_info['effort_days'],
                'D': cost_info['amount']
            })
        
        # DataFrame作成
        df = pd.DataFrame(original_data)
        
        # 言語設定に応じたヘッダー
        if env_config.get('language') == 'ja':
            df.columns = ['成果物名', '説明', '予想工数(人日)', f'金額({env_config.get("currency", "JPY")})']
        else:
            df.columns = ['Deliverable', 'Description', 'Effort (Person-Days)', f'Amount ({env_config.get("currency", "JPY")})']
        
        # 財務サマリー行を追加
        summary = cost_calculation['financial_summary']
        
        # 空行追加
        df.loc[len(df)] = ['', '', '', '']
        
        # サマリー行追加
        if env_config.get('language') == 'ja':
            df.loc[len(df)] = ['小計', '', summary['total_effort_days'], summary['subtotal']]
            df.loc[len(df)] = [f'税額({summary["tax_rate"]*100:.0f}%)', '', '', summary['tax_amount']]
            df.loc[len(df)] = ['総額', '', '', summary['total_amount']]
            df.loc[len(df)] = ['', '', '', '']
            df.loc[len(df)] = ['【見積前提条件】', '', '', '']
        else:
            df.loc[len(df)] = ['Subtotal', '', summary['total_effort_days'], summary['subtotal']]
            df.loc[len(df)] = [f'Tax ({summary["tax_rate"]*100:.0f}%)', '', '', summary['tax_amount']]
            df.loc[len(df)] = ['Total', '', '', summary['total_amount']]
            df.loc[len(df)] = ['', '', '', '']
            df.loc[len(df)] = ['【Estimation Assumptions】', '', '', '']
        
        # 前提条件を追加
        assumptions_to_add = [
            ('エンジニアレベル' if env_config.get('language') == 'ja' else 'Engineer Level', 
             finalized_assumptions.get('engineer_level', 'N/A')),
            ('人日単価' if env_config.get('language') == 'ja' else 'Daily Rate', 
             f"{env_config.get('daily_rate', 0):,} ({env_config.get('currency', 'JPY')})"),
            ('技術スタック' if env_config.get('language') == 'ja' else 'Tech Stack', 
             finalized_assumptions.get('tech_stack', 'N/A')),
        ]
        
        # 数値前提条件
        if 'database_tables' in finalized_assumptions:
            assumptions_to_add.append((
                'データベーステーブル' if env_config.get('language') == 'ja' else 'Database Tables',
                f"{finalized_assumptions['database_tables']}テーブル想定" if env_config.get('language') == 'ja' else f"{finalized_assumptions['database_tables']} tables assumed"
            ))
        
        if 'api_endpoints' in finalized_assumptions:
            assumptions_to_add.append((
                'APIエンドポイント' if env_config.get('language') == 'ja' else 'API Endpoints',
                f"{finalized_assumptions['api_endpoints']}エンドポイント想定" if env_config.get('language') == 'ja' else f"{finalized_assumptions['api_endpoints']} endpoints assumed"
            ))
        
        if 'test_pages' in finalized_assumptions:
            assumptions_to_add.append((
                'テストページ' if env_config.get('language') == 'ja' else 'Test Pages',
                f"{finalized_assumptions['test_pages']}ページ想定" if env_config.get('language') == 'ja' else f"{finalized_assumptions['test_pages']} pages assumed"
            ))
        
        # 前提条件を追加
        for label, value in assumptions_to_add:
            df.loc[len(df)] = [label, value, '', '']
        
        # Excelファイル作成
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='見積書')
            
            # ワークシートの取得と書式設定
            worksheet = writer.sheets['見積書']
            
            # 列幅の調整
            worksheet.column_dimensions['A'].width = 25
            worksheet.column_dimensions['B'].width = 50
            worksheet.column_dimensions['C'].width = 15
            worksheet.column_dimensions['D'].width = 15
            
            # 数値フォーマットの設定（金額列）
            for row in range(2, len(df) + 2):
                if isinstance(df.iloc[row-2, 3], (int, float)) and df.iloc[row-2, 3] != '':
                    worksheet.cell(row=row, column=4).number_format = '#,##0'
        
        print(f"\n✅ 見積書を出力しました: {file_path}")
        
        return {
            "file_path": str(file_path),
            "filename": filename,
            "metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "total_rows": len(df),
                "data_rows": len(deliverables),
                "summary_rows": len(df) - len(deliverables),
                "language": env_config.get('language', 'ja'),
                "currency": env_config.get('currency', 'JPY')
            }
        }