import os
import importlib.util
import sys
import inspect
from jay_ai.agent import ParsedAgent


def load_parsed_agent(agent_path: str) -> ParsedAgent:
    agent_dir = os.path.dirname(agent_path)
    if agent_dir not in sys.path:
        sys.path.insert(0, agent_dir)

    try:
        functions_module = load_functions_module(agent_path)
    except Exception as e:
        print(f"Error loading functions module: {e}")
        sys.exit(1)

    return ParsedAgent(**functions_module.agent.model_dump())


def load_functions_module(module_path):
    spec = importlib.util.spec_from_file_location("", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
