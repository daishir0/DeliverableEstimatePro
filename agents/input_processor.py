"""
DeliverableEstimate Pro - Input Processor Agent
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from config.settings import settings


class InputProcessor:
    """入力処理・データ構造化エージェント"""
    
    def __init__(self):
        self.settings = settings
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """入力データの処理と構造化"""
        try:
            # Excel ファイル読み込み
            excel_data = self._load_excel_file(state["excel_input"])
            
            # システム要件テキスト解析
            project_context = self._parse_system_requirements(state["system_requirements"])
            
            # 環境設定読み込み
            env_config = self._load_environment_config()
            
            # データバリデーション
            validation_result = self._validate_input_data(excel_data, project_context, env_config)
            
            # デフォルト技術前提条件設定
            tech_assumptions = self._set_default_tech_assumptions(project_context)
            
            return {
                **state,
                "deliverables": excel_data["deliverables"],
                "analyzed_deliverables": excel_data["deliverables"],  # 分析済み成果物として追加
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
    
    def _load_excel_file(self, file_path: str) -> Dict[str, Any]:
        """Excelファイルの読み込み"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            
            # A列とB列のデータを抽出
            if len(df.columns) < 2:
                raise ValueError("Excel file must have at least 2 columns (A: Name, B: Description)")
            
            deliverables = []
            for index, row in df.iterrows():
                if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                    deliverables.append({
                        "name": str(row.iloc[0]).strip(),
                        "description": str(row.iloc[1]).strip()
                    })
            
            if not deliverables:
                raise ValueError("No valid deliverables found in Excel file")
            
            return {
                "deliverables": deliverables,
                "original_dataframe": df
            }
            
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {str(e)}")
    
    def _parse_system_requirements(self, requirements_text: str) -> Dict[str, Any]:
        """システム要件テキストの解析"""
        if not requirements_text.strip():
            raise ValueError("System requirements text cannot be empty")
        
        # 基本的な解析
        project_context = {
            "raw_text": requirements_text,
            "project_type": self._detect_project_type(requirements_text),
            "complexity": self._assess_complexity(requirements_text),
            "technologies": self._extract_technologies(requirements_text),
            "special_requirements": self._extract_special_requirements(requirements_text)
        }
        
        return project_context
    
    def _detect_project_type(self, text: str) -> str:
        """プロジェクトタイプの検出"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ["ec", "ecommerce", "オンラインショップ", "通販"]):
            return "ECサイト"
        elif any(keyword in text_lower for keyword in ["社内", "internal", "管理システム"]):
            return "社内システム"
        elif any(keyword in text_lower for keyword in ["web", "ウェブ", "サイト"]):
            return "Webシステム"
        elif any(keyword in text_lower for keyword in ["mobile", "モバイル", "アプリ"]):
            return "モバイルアプリ"
        else:
            return "その他"
    
    def _assess_complexity(self, text: str) -> str:
        """複雑度の評価"""
        text_lower = text.lower()
        complexity_indicators = 0
        
        # 複雑度を上げる要因をカウント
        if any(keyword in text_lower for keyword in ["決済", "payment", "クレジット"]):
            complexity_indicators += 2
        if any(keyword in text_lower for keyword in ["認証", "auth", "ログイン"]):
            complexity_indicators += 1
        if any(keyword in text_lower for keyword in ["api", "連携", "integration"]):
            complexity_indicators += 1
        if any(keyword in text_lower for keyword in ["管理画面", "admin", "ダッシュボード"]):
            complexity_indicators += 1
        if any(keyword in text_lower for keyword in ["検索", "search", "フィルタ"]):
            complexity_indicators += 1
        
        if complexity_indicators >= 4:
            return "complex"
        elif complexity_indicators >= 2:
            return "medium"
        else:
            return "simple"
    
    def _extract_technologies(self, text: str) -> List[str]:
        """技術スタックの抽出"""
        text_lower = text.lower()
        technologies = []
        
        # Frontend
        if any(tech in text_lower for tech in ["react", "vue", "angular"]):
            technologies.extend(["React", "Vue.js", "Angular"])
        
        # Backend
        if any(tech in text_lower for tech in ["node", "python", "java", "php"]):
            technologies.extend(["Node.js", "Python", "Java", "PHP"])
        
        # Database
        if any(tech in text_lower for tech in ["mysql", "postgresql", "mongodb"]):
            technologies.extend(["MySQL", "PostgreSQL", "MongoDB"])
        
        # デフォルト技術スタック
        if not technologies:
            technologies = ["React", "Node.js", "PostgreSQL"]
        
        return technologies
    
    def _extract_special_requirements(self, text: str) -> List[str]:
        """特殊要件の抽出"""
        text_lower = text.lower()
        requirements = []
        
        if any(keyword in text_lower for keyword in ["決済", "payment"]):
            requirements.append("決済機能")
        if any(keyword in text_lower for keyword in ["レスポンシブ", "responsive", "モバイル対応"]):
            requirements.append("レスポンシブ対応")
        if any(keyword in text_lower for keyword in ["ssl", "セキュリティ", "security"]):
            requirements.append("高セキュリティ要件")
        if any(keyword in text_lower for keyword in ["パフォーマンス", "performance", "高速"]):
            requirements.append("パフォーマンス要件")
        
        return requirements
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """環境設定の読み込み"""
        return {
            "daily_rate": self.settings.daily_rate,
            "tax_rate": self.settings.tax_rate,
            "currency": self.settings.currency,
            "language": self.settings.language,
            "model": self.settings.model
        }
    
    def _set_default_tech_assumptions(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """デフォルト技術前提条件の設定"""
        base_assumptions = self.settings.default_assumptions.copy()
        
        # プロジェクトタイプに応じた調整
        if project_context["project_type"] == "ECサイト":
            base_assumptions.update({
                "database_tables": 25,
                "api_endpoints": 60,
                "security_requirements": "高セキュリティ",
                "payment_integration": "決済システム連携あり"
            })
        elif project_context["project_type"] == "社内システム":
            base_assumptions.update({
                "database_tables": 15,
                "api_endpoints": 30,
                "security_requirements": "中セキュリティ",
                "user_training": "ユーザートレーニング必要"
            })
        
        # 複雑度に応じた調整
        complexity_multipliers = {
            "simple": 0.8,
            "medium": 1.0,
            "complex": 1.3
        }
        
        multiplier = complexity_multipliers.get(project_context["complexity"], 1.0)
        base_assumptions["database_tables"] = int(base_assumptions["database_tables"] * multiplier)
        base_assumptions["api_endpoints"] = int(base_assumptions["api_endpoints"] * multiplier)
        
        return base_assumptions
    
    def _validate_input_data(self, excel_data: Dict, project_context: Dict, env_config: Dict) -> Dict[str, Any]:
        """データの妥当性チェック"""
        errors = []
        
        # Excel データのチェック
        if not excel_data.get("deliverables"):
            errors.append("No deliverables found in Excel file")
        elif len(excel_data["deliverables"]) > self.settings.max_deliverables:
            errors.append(f"Too many deliverables (max: {self.settings.max_deliverables})")
        
        # プロジェクトコンテキストのチェック
        if not project_context.get("raw_text"):
            errors.append("System requirements text is empty")
        
        # 環境設定のチェック
        if not env_config.get("daily_rate") or env_config["daily_rate"] <= 0:
            errors.append("Invalid daily rate")
        
        return {
            "all_valid": len(errors) == 0,
            "errors": errors,
            "validation_timestamp": datetime.now().isoformat()
        }