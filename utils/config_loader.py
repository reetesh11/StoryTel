# utils/config_loader.py
import yaml
import os
from typing import Dict, Any

def load_ollama_config() -> Dict[str, Any]:
    """Load Ollama configuration from YAML file"""
    config_path = os.path.join("config", "crew_config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("ollama", {})

def load_agents_config() -> Dict[str, any]:
    """Load Agents configuration from YAML file"""
    config_path = os.path.join("config", "crew_config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("agents", {})

def load_tasks_config() -> Dict[str, any]:
    """Load Agents configuration from YAML file"""
    config_path = os.path.join("config", "crew_config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("tasks", {})