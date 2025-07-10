"""
DeliverableEstimate Pro - Main Application Entry Point
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from workflow import EstimationSession, run_estimation_with_error_handling
from config.settings import settings


def main():
    """メインアプリケーション"""
    print("=" * 60)
    print("🚀 DeliverableEstimate Pro - AI駆動成果物見積もり自動化システム")
    print("=" * 60)
    
    # 設定確認
    try:
        if not settings.openai_api_key:
            print("❌ エラー: OPENAI_API_KEYが設定されていません")
            print("📝 .envファイルを作成し、APIキーを設定してください")
            return
        
        print(f"✅ 設定確認完了")
        print(f"   - 人日単価: {settings.daily_rate:,}円")
        print(f"   - 税率: {settings.tax_rate*100:.0f}%")
        print(f"   - 通貨: {settings.currency}")
        print(f"   - 言語: {settings.language}")
        print(f"   - AIモデル: {settings.model}")
        
    except Exception as e:
        print(f"❌ 設定エラー: {str(e)}")
        return
    
    # 入力ファイルの確認
    input_file = input("\n📄 Excelファイルのパス (例: input/sample_input.xlsx): ").strip()
    
    if not input_file:
        input_file = "input/sample_input.xlsx"
    
    if not os.path.exists(input_file):
        print(f"❌ エラー: ファイルが見つかりません: {input_file}")
        return
    
    # システム要件の入力
    print("\n📝 システム要件を入力してください:")
    print("   例: ECサイトの構築プロジェクト")
    print("       - ユーザー管理機能")
    print("       - 商品管理機能")
    print("       - 決済機能")
    print("\n入力してください (複数行可、空行で終了):")
    
    requirements_lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        requirements_lines.append(line)
    
    if not requirements_lines:
        print("❌ エラー: システム要件が入力されていません")
        return
    
    system_requirements = "\n".join(requirements_lines)
    
    print("\n" + "=" * 60)
    print("🔄 見積処理を開始します...")
    print("=" * 60)
    
    # 見積処理実行
    try:
        session = EstimationSession()
        result = session.start_estimation(input_file, system_requirements)
        
        if result.get("error"):
            print(f"❌ エラー: {result['error']}")
            return
        
        if result.get("approved"):
            print("\n" + "=" * 60)
            print("✅ 見積処理が完了しました!")
            print("=" * 60)
            print(f"📊 出力ファイル: {result.get('final_excel_output')}")
            
            # セッション情報の表示
            metadata = result.get("excel_generation_metadata", {})
            if metadata:
                print(f"📝 生成情報:")
                print(f"   - 生成時刻: {metadata.get('generation_timestamp', 'N/A')}")
                print(f"   - 総行数: {metadata.get('total_rows', 'N/A')}")
                print(f"   - データ行数: {metadata.get('data_rows', 'N/A')}")
                print(f"   - 言語: {metadata.get('language', 'N/A')}")
                print(f"   - 通貨: {metadata.get('currency', 'N/A')}")
        else:
            print("\n❌ 見積処理が完了しませんでした")
            if result.get("user_feedback"):
                print(f"📝 最終フィードバック: {result['user_feedback']}")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 処理が中断されました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {str(e)}")
    
    print("\n👋 ご利用ありがとうございました")


def quick_demo():
    """クイックデモ"""
    print("🎯 クイックデモを実行します")
    
    # サンプルデータで実行
    demo_result = run_estimation_with_error_handling(
        excel_file="input/sample_input.xlsx",
        requirements="""ECサイトの構築プロジェクト
- ユーザー管理機能
- 商品管理機能  
- 決済機能
- 管理画面
- レスポンシブ対応"""
    )
    
    if demo_result["success"]:
        print("✅ デモ実行成功!")
        result = demo_result["result"]
        if result.get("final_excel_output"):
            print(f"📊 出力ファイル: {result['final_excel_output']}")
    else:
        print(f"❌ デモ実行失敗: {demo_result['error']}")


if __name__ == "__main__":
    # コマンドライン引数の確認
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        quick_demo()
    else:
        main()