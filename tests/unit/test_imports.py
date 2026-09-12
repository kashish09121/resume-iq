import pytest

def test_resumeiq_package_import():
    """Verify that the core package can be imported successfully."""
    import resume_iq
    assert resume_iq.__version__ == "0.1.0"

def test_config_loads():
    """Verify that the settings module loads safely."""
    from resume_iq.config.settings import settings
    assert settings.ENV in ["development", "production", "test"]
    assert settings.MAX_UPLOAD_SIZE_MB >= 1
