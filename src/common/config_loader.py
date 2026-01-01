import yaml
import os
import re
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Loads a YAML config file and environment variables.
    """
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at: {path.absolute()}")

    env_pattern = re.compile(r".*?\${(\w+)(?::([^}]*))?}.*?")

    def env_constructor(loader, node):
        """Custom YAML constructor to resolve environment variables."""
        value = loader.construct_scalar(node)
        match = env_pattern.findall(value)
        if match:
            full_value = value
            for var, default in match:

                env_val = os.environ.get(var, default if default is not None else "")
                full_value = full_value.replace(f"${{{var}{':' + default if default else ''}}}", env_val)
            return full_value
        return value

    yaml.SafeLoader.add_constructor("tag:yaml.org,2002:str", env_constructor)
    yaml.SafeLoader.add_implicit_resolver("!env", env_pattern, None)

    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
            if config is None:
                raise ValueError(f"Config file is empty: {path}")
            return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading config: {e}")
        raise