"""
サンプルExcelファイル作成スクリプト
"""

import pandas as pd
from pathlib import Path

# サンプルデータ
sample_data = {
    'A': [
        '要件定義書',
        'システム設計書', 
        'データベース設計',
        'フロントエンド開発',
        'バックエンド開発',
        'API設計・実装',
        'ユーザー管理機能',
        '商品管理機能',
        '決済機能',
        '管理画面',
        '単体テスト',
        '結合テスト',
        'システムテスト',
        '運用マニュアル',
        'デプロイメント'
    ],
    'B': [
        'システムの機能要件・非機能要件を詳細に記載した文書',
        'システム全体のアーキテクチャ設計とコンポーネント設計',
        'データベースのER図作成とテーブル設計',
        'React/Vue.jsを使用したユーザーインターフェースの実装',
        'Node.js/Pythonを使用したサーバーサイドアプリケーション開発',
        'RESTful APIの設計と実装',
        'ユーザー登録・認証・プロファイル管理機能',
        '商品カタログ・在庫管理・商品検索機能',
        'クレジットカード決済・決済履歴管理機能',
        '管理者用ダッシュボード・データ分析機能',
        '各機能モジュールの単体テスト実装',
        'システム全体の結合テスト実施',
        'エンドツーエンドのシステムテスト実施',
        'システム運用・保守のためのマニュアル作成',
        '本番環境への展開とサーバー設定'
    ]
}

# DataFrameを作成
df = pd.DataFrame(sample_data)

# パスの作成
file_path = Path("input/sample_input.xlsx")
file_path.parent.mkdir(parents=True, exist_ok=True)

# Excelファイルとして保存
df.to_excel(file_path, index=False, header=False)

print(f"✅ サンプルExcelファイルを作成しました: {file_path}")