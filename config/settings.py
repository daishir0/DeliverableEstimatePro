"""
DeliverableEstimate Pro - Configuration Settings
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """システム設定管理クラス"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.daily_rate = float(os.getenv("DAILY_RATE", 50000))
        self.tax_rate = float(os.getenv("TAX_RATE", 0.10))
        self.currency = os.getenv("CURRENCY", "JPY")
        self.language = os.getenv("LANGUAGE", "ja")
        self.model = os.getenv("MODEL", "gpt-4o-mini")
        
        # Technical Assumptions
        self.default_assumptions = {
            "engineer_level": os.getenv("DEFAULT_ENGINEER_LEVEL", "Python使用可能な平均的エンジニア"),
            "development_environment": os.getenv("DEFAULT_DEVELOPMENT_ENVIRONMENT", "標準的な開発環境"),
            "database_tables": int(os.getenv("DEFAULT_DATABASE_TABLES", 20)),
            "api_endpoints": int(os.getenv("DEFAULT_API_ENDPOINTS", 50)),
            "test_pages": int(os.getenv("DEFAULT_TEST_PAGES", 1000)),
            "tech_stack": os.getenv("DEFAULT_TECH_STACK", "React/Vue.js + Node.js/Python")
        }
        
        # System Configuration
        self.max_deliverables = int(os.getenv("MAX_DELIVERABLES", 100))
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", 5))
        self.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", 60))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "logs/estimation.log")
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """設定の妥当性チェック"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required but not set")
        
        if self.daily_rate <= 0:
            raise ValueError("DAILY_RATE must be positive")
        
        if not (0 <= self.tax_rate <= 1):
            raise ValueError("TAX_RATE must be between 0 and 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書形式で返す"""
        return {
            "openai_api_key": self.openai_api_key,
            "daily_rate": self.daily_rate,
            "tax_rate": self.tax_rate,
            "currency": self.currency,
            "language": self.language,
            "model": self.model,
            "default_assumptions": self.default_assumptions,
            "max_deliverables": self.max_deliverables,
            "max_iterations": self.max_iterations,
            "session_timeout_minutes": self.session_timeout_minutes,
            "log_level": self.log_level,
            "log_file": self.log_file
        }

# Global settings instance
settings = Settings()