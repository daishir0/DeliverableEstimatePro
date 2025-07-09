# エージェント詳細仕様

## 🤖 エージェント構成概要

### **5エージェントシステム**
1. **Input Processor** - 入力処理・データ構造化
2. **Deliverable Analyzer** - 成果物分析・複雑度評価
3. **Effort Estimator** - 工数見積・リスク調整
4. **Question Generator** - 精度向上質問生成
5. **Report Generator** - 見積書出力・承認管理

---

## 📝 Agent 1: Input Processor

### **責務**
- Excelファイル(input.xlsx)の読み込みとパーシング
- システム要件テキストの構造化
- .envファイルからの設定情報読み込み
- データ整合性チェック
- デフォルト技術前提条件の設定

### **入力データ**
```yaml
excel_file_path: "input.xlsx"
system_requirements_text: |
  ECサイトの構築プロジェクト
  - ユーザー管理機能
  - 商品管理機能
  - 決済機能
env_file_path: ".env"
```

### **処理ロジック**
1. Excelファイルの読み込み(pandas)
2. A列(Name)、B列(Description)のデータ抽出
3. システム要件テキストの自然言語解析
4. .envファイルからDAILY_RATE, OPENAI_API_KEY, TAX_RATE取得
5. データバリデーションとエラーハンドリング

### **出力データ**
```yaml
deliverables:
  - name: "要件定義書"
    description: "システムの機能要件、非機能要件を詳細に記載した文書"
  - name: "システム設計書"
    description: "アーキテクチャ、DB設計、インターフェース設計を含む技術設計書"

project_context:
  project_type: "ECサイト構築"
  complexity: "medium"
  technologies: ["React", "Node.js", "PostgreSQL"]
  team_size: 5
  duration_months: 3
  special_requirements: ["決済機能", "レスポンシブ対応"]

config:
  daily_rate: 50000
  tax_rate: 0.10
  language: "ja"
  model: "gpt-4o-mini"
  currency: "JPY"

tech_assumptions:
  engineer_level: "Python使用可能な平均的エンジニア"
  development_environment: "標準的な開発環境"

validation_status:
  excel_valid: true
  requirements_parsed: true
  config_loaded: true
  error_messages: []
```

---

## 🔍 Agent 2: Deliverable Analyzer

### **責務**
- 必要となる成果物の詳細分析
- 成果物の種類と複雑度分析
- プロジェクトコンテキストに基づく難易度評価
- 類似成果物の過去実績データ参照
- 成果物間の依存関係分析

### **入力データ**
```yaml
deliverables: ["成果物リスト"]
project_context: "プロジェクト情報"
historical_data: "過去実績データベース"
tech_assumptions: "技術前提条件"
```

### **処理ロジック**
1. 成果物名と説明文の意味解析
2. プロジェクトタイプと技術スタックに基づく複雑度判定
3. 類似成果物の過去データ検索とマッチング
4. 依存関係と作業順序の特定
5. リスクファクターの抽出

### **出力データ**
```yaml
analyzed_deliverables:
  - name: "要件定義書"
    category: "documentation"
    complexity_level: "medium"
    risk_factors: ["要件変更の可能性", "ステークホルダーの調整コスト"]
    technology_dependencies: ["技術スタックの確定"]

overall_assessment:
  project_complexity: "medium-high"
  total_deliverable_count: 5
  documentation_ratio: 0.4
  development_ratio: 0.6
  high_risk_items: 2
  critical_path_items: ["システム設計書", "フロントエンド開発"]

recommendations:
  - "決済機能の早期プロトタイピングを推奨"
  - "パフォーマンステストの十分な時間確保が必要"
```

---

## 📊 Agent 3: Effort Estimator

### **責務**
- 人・技術側面の前提条件に基づく工数算出
- 成果物ごとの詳細工数算出
- 複雑度・リスクファクターによる調整
- 過去実績データに基づく検証
- 不確実性とバッファの考慮
- デフォルト前提：Python使用可能な平均的エンジニア

### **入力データ**
```yaml
analyzed_deliverables: "前エージェントからの成果物分析結果"
project_context: "プロジェクト情報"
historical_data: "過去実績データベース"
tech_assumptions: "人・技術側面の前提条件"
```

### **処理ロジック**
1. 成果物カテゴリ別の基礎工数算出
2. 複雑度レベルによる調整係数適用
3. リスクファクターに基づくバッファ計算
4. 過去実績データとの比較検証
5. 信頼度レベルの算出

### **出力データ**
```yaml
deliverable_estimates:
  - name: "要件定義書"
    base_effort_days: 4.0
    complexity_adjustment: 1.2
    risk_buffer: 0.3
    final_effort_days: 5.0
    confidence_level: "85%"
    estimation_rationale: "中規模ECサイトの標準的な要件定義、ステークホルダー調整考慮"
  - name: "システム設計書"
    base_effort_days: 6.0
    complexity_adjustment: 1.3
    risk_buffer: 0.8
    final_effort_days: 8.0
    confidence_level: "80%"
    estimation_rationale: "マイクロサービスアーキテクチャの設計複雑性を考慮"

tech_assumptions_used:
  engineer_level: "Python使用可能な平均的エンジニア"
  productivity_factor: 1.0

summary:
  total_effort_days: 80.0
  average_confidence: "82%"
  high_risk_items: ["バックエンド開発", "テスト実装"]
  critical_dependencies: ["システム設計書 → 開発全般"]

adjustment_factors:
  project_complexity: 1.2
  team_experience: 1.0
  schedule_pressure: 1.1
```

---

## ❓ Agent 4: Question Generator

### **責務**
- 見積精度向上のための質問生成
- 成果物の詳細仕様確認
- 技術的要件の明確化
- 最終的な見積前提条件の確定

### **入力データ**
```yaml
analyzed_deliverables: "成果物分析結果"
effort_estimates: "工数見積結果"
tech_assumptions: "技術前提条件"
```

### **処理ロジック**
1. 成果物ごとの不明確な要素の特定
2. 工数に影響する技術的質問の生成
3. ユーザーとの対話による回答収集
4. 回答に基づく見積前提条件の更新

### **出力データ**
```yaml
questions_and_answers:
  - question: "データベース設計でのER図作成において、何種類のテーブルが必要か？"
    answer: "20テーブル"
    impact: "データベース設計工数に影響"
  - question: "バックエンド開発において、必要なAPIのエンドポイント数はどれくらいか？"
    answer: "50"
    impact: "API設計・開発工数に影響"

finalized_assumptions:
  engineer_level: "Python使用可能な平均的エンジニア"
  daily_rate: 40000
  currency: "JPY"
  database_tables: 20
  api_endpoints: 50
  test_pages: 1000
  tech_stack: "React/Vue.js + Node.js/Python"
```

---

## 📊 Agent 5: Report Generator

### **責務**
- コンソールでの見積書表示
- ユーザー承認の待機
- 承認時：Excel出力実行（見積前提条件含む）
- 否認時：フィードバック収集とプロセス再実行
- 言語設定に応じたExcelヘッダ生成
- 見積前提条件の構造的記載
- タイムスタンプ付きファイル名でExcel出力

### **入力データ**
```json
{
  "original_excel_data": "元のExcelファイル内容",
  "deliverable_costs": "前エージェントからのコスト計算結果",
  "session_context": "AIエージェントセッション情報",
  "config": {
    "daily_rate": 50000,
    "tax_rate": 0.10
  }
}
```

### **処理ロジック**
1. 元のExcel構造の保持（A列・B列）
2. 言語設定に応じたヘッダ生成
3. C列に予想工数（人日）を追加
4. D列に金額（設定通貨）を追加
5. 最終行に財務サマリー（言語対応）追記
6. 見積前提条件の構造化記載（言語対応）
7. タイムスタンプ付きファイル名生成（yyyymmdd-hhmmss.xlsx）

### **出力データ**
```json
{
  "excel_output": {
    "file_path": "/output/20250709-143000.xlsx",
    "file_name": "20250709-143000.xlsx",
    "generation_timestamp": "2025-01-09T14:30:00Z",
    "total_rows": 12,
    "data_rows": 5,
    "summary_rows": 7
  },
  "session_info_section": {
    "estimation_assumptions_ja": {
      "engineer_level": "Python使用可能な平均的エンジニア",
      "daily_rate": "40,000 (.env設定通貨)",
      "tech_stack": "React/Vue.js + Node.js/Python",
      "database_tables": "20テーブル想定"
    }
  }
}
```

---

## 🔄 エージェント間連携フロー

### **メインフロー**
```
Input Processor → Deliverable Analyzer → Effort Estimator → Question Generator → Cost Calculator → Report Generator
```

### **フィードバックループ**
```
Report Generator → ユーザー承認 → [YES: 終了] / [NO: 修正フィードバック] → 適切なエージェントに戻る
```

### **データ受け渡し形式**
- **YAMLフォーマット**: 構造化データの可読性と保守性
- **JSONフォーマット**: 財務データの精密な数値処理
- **エラーハンドリング**: 各エージェントでのバリデーションとエラー伝播

---
**作成日**: 2025年7月9日  
**バージョン**: 1.0