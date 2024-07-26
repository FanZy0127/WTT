import os
import pytest
from app.config import Settings
from pydantic import ValidationError

@pytest.fixture
def set_env_vars():
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
    os.environ["DATA_URL"] = "http://localhost/data"
    os.environ["JSON_SERVER_PATH"] = "/path/to/json/server"
    yield
    del os.environ["DATABASE_URL"]
    del os.environ["DATA_URL"]
    del os.environ["JSON_SERVER_PATH"]

def test_settings(set_env_vars):
    settings = Settings()

    assert settings.DATABASE_URL == "sqlite+aiosqlite:///./test.db"
    assert settings.DATA_URL == "http://localhost/data"
    assert settings.JSON_SERVER_PATH == "/path/to/json/server"

def test_env_file_loading():
    with open(".env", "w", encoding="utf-8") as f:
        f.write("DATABASE_URL=sqlite+aiosqlite:///./env_test.db\n")
        f.write("DATA_URL=http://localhost/env_data\n")
        f.write("JSON_SERVER_PATH=/path/to/env/json/server\n")

    settings = Settings()

    assert settings.DATABASE_URL == "sqlite+aiosqlite:///./env_test.db"
    assert settings.DATA_URL == "http://localhost/env_data"
    assert settings.JSON_SERVER_PATH == "/path/to/env/json/server"

    os.remove(".env")

def test_missing_env_vars():
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    if "DATA_URL" in os.environ:
        del os.environ["DATA_URL"]
    if "JSON_SERVER_PATH" in os.environ:
        del os.environ["JSON_SERVER_PATH"]

    with pytest.raises(ValidationError):
        settings = Settings()

@pytest.fixture(scope="module", autouse=True)
def ensure_env_file():
    env_file_content = (
        "DATABASE_URL=sqlite+aiosqlite:///./test.db\n"
        "DATA_URL=http://localhost:3000/measurements\n"
        "JSON_SERVER_PATH=\"Path\\\\To\\\\Your\\\\npm\\\\json-server.cmd\"\n"
    )

    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_file_content)

    yield

    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_file_content)
