from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import os

try:
    from dotenv import dotenv_values  # type: ignore
except Exception:
    dotenv_values = None  # type: ignore

# project paths
ROOT = Path(__file__).resolve().parent.parent  # backend/
ENV_PATH = ROOT / ".env"

@dataclass
class Settings:
    PROVIDER: str = "auto"             # "openai" | "ollama" | "auto"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OLLAMA_HOST: Optional[str] = None
    OLLAMA_MODEL: str = "llama3.1"
    LLM_TEMPERATURE: float = 0.35

_CACHE: Dict[str, Any] = {"mtime": None, "settings": None}

def _load_env_map() -> Dict[str, str]:
    # Prefer .env (if exists), else fall back to process env
    env_map: Dict[str, str] = {}
    if ENV_PATH.exists() and dotenv_values:
        env_map = {k: v for k, v in dotenv_values(str(ENV_PATH)).items() if v is not None}  # type: ignore
    else:
        for k in ["PROVIDER", "OPENAI_API_KEY", "OPENAI_MODEL", "OLLAMA_HOST", "OLLAMA_MODEL", "LLM_TEMPERATURE"]:
            if k in os.environ:
                env_map[k] = os.environ[k]
    return env_map

def _build_settings(env: Dict[str, str]) -> Settings:
    return Settings(
        PROVIDER=env.get("PROVIDER", "auto").lower(),
        OPENAI_API_KEY=env.get("OPENAI_API_KEY"),
        OPENAI_MODEL=env.get("OPENAI_MODEL", "gpt-4o-mini"),
        OLLAMA_HOST=env.get("OLLAMA_HOST"),
        OLLAMA_MODEL=env.get("OLLAMA_MODEL", "llama3.1"),
        LLM_TEMPERATURE=float(env.get("LLM_TEMPERATURE", "0.35")),
    )

def get_settings() -> Settings:
    """
    Return Settings, reloading if backend/.env changed.
    This allows changing models/keys without restarting the server.
    """
    mtime = ENV_PATH.stat().st_mtime if ENV_PATH.exists() else None
    if _CACHE["settings"] is None or _CACHE["mtime"] != mtime:
        env_map = _load_env_map()
        _CACHE["settings"] = _build_settings(env_map)
        _CACHE["mtime"] = mtime
    return _CACHE["settings"]

def choose_llm(s: Settings) -> Optional[Tuple[str, Dict[str, str]]]:
    """
    Return ('openai', {'model':..., 'api_key':...}) or ('ollama', {'model':..., 'host':...}) or None.
    Honors s.PROVIDER = 'openai' | 'ollama' | 'auto'.
    """
    provider = (s.PROVIDER or "auto").lower()
    if provider == "openai" or (provider == "auto" and s.OPENAI_API_KEY):
        if not s.OPENAI_API_KEY:
            return None
        return ("openai", {"model": s.OPENAI_MODEL, "api_key": s.OPENAI_API_KEY})
    if provider == "ollama" or (provider == "auto" and s.OLLAMA_HOST):
        if not s.OLLAMA_HOST:
            return None
        return ("ollama", {"model": s.OLLAMA_MODEL, "host": s.OLLAMA_HOST})
    return None
