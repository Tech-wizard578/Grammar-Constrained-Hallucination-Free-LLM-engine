"""Tests for config.py - Configuration Management (4 tests)."""

import pytest
import os
from unittest.mock import patch


class TestConfigValidation:
    """Tests for configuration validation logic."""
    
    def test_validate_config_passes_with_valid_keys(self):
        """Test validation passes when API keys are present."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "TAVILY_API_KEY": "tavily-key"
        }):
            # Re-import to trigger validation
            from config import validate_config
            assert validate_config() is True
    
    def test_mutual_exclusivity_raises_error(self):
        """Test that both USE_GROQ and USE_OPENROUTER raises ValueError."""
        with patch.dict(os.environ, {
            "USE_GROQ": "true",
            "USE_OPENROUTER": "true",
            "GROQ_API_KEY": "key",
            "OPENROUTER_API_KEY": "key"
        }, clear=False):
            with pytest.raises(ValueError, match="Only one API provider"):
                # Force reimport
                import importlib
                import config
                importlib.reload(config)
    
    def test_get_config_summary_returns_dict(self):
        """Test config summary returns expected keys."""
        from config import get_config_summary
        
        summary = get_config_summary()
        
        assert isinstance(summary, dict)
        assert "api_provider" in summary
        assert "default_model" in summary
        assert "smart_model" in summary
        assert "chunk_size" in summary
    
    def test_environment_profiles_exist(self):
        """Test environment profiles are defined."""
        from config import ENVIRONMENT, LOG_LEVEL, ENABLE_DEBUG_OUTPUT
        
        assert ENVIRONMENT in ["development", "production", "test"]
        assert LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]
        assert isinstance(ENABLE_DEBUG_OUTPUT, bool)
