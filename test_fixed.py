#!/usr/bin/env python3
"""
Fixed system test for DeliverableEstimate Pro
"""

import sys
import os
from workflow import EstimationSession

def test_fixed_system():
    """修正されたシステムのテスト"""
    
    print("🧪 修正されたシステムのテスト開始...")
    
    # 1. 基本インポートテスト
    print("1️⃣ 基本インポートテスト...")
    try:
        session = EstimationSession()
        print("✅ EstimationSessionインスタンス作成成功")
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False
    
    # 2. ワークフローテスト
    print("2️⃣ ワークフローテスト...")
    try:
        excel_file = "input/sample_input.xlsx"
        requirements = "1000ページあるWordPress、基幹システムと接続の前提。"
        
        # テスト用の初期状態
        initial_state = {
            "excel_input": excel_file,
            "system_requirements": requirements,
            "iteration_count": 0,
            "approved": False,
            "user_feedback": "",
            "error": "",
            "session_metadata": {
                "session_id": "test_session",
                "start_time": "2025-07-09T00:00:00"
            }
        }
        
        # ワークフローの実行（再帰制限対応）
        print("🔄 ワークフロー実行中...")
        result = session.compiled_workflow.invoke(initial_state, config={"recursion_limit": 50})
        
        if result.get("error"):
            print(f"⚠️ 処理エラー: {result['error']}")
            return False
        else:
            print("✅ ワークフロー実行成功")
            print(f"📊 結果: approved={result.get('approved')}, iteration_count={result.get('iteration_count')}")
            return True
            
    except Exception as e:
        print(f"❌ ワークフローエラー: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_system()
    if success:
        print("\n🎉 修正されたシステムのテストが完了しました！")
        sys.exit(0)
    else:
        print("\n❌ テストが失敗しました。")
        sys.exit(1)