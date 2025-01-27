import os
import yaml
from pydantic_settings import BaseSettings
from typing import Optional, Dict
from gai.lib.common.utils import get_app_path

class GaiClientConfig(BaseSettings):
    client_type: str
    type: Optional[str] = None
    engine: Optional[str] = None
    model: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    env: Optional[Dict] = None
    extra: Optional[Dict] = None
    hyperparameters: Optional[Dict] = {}

    @classmethod
    def from_name(cls,name:str, file_path:str=None) -> "GaiClientConfig":
        return cls._get_client_config(name=name, file_path=file_path)

    @classmethod
    def from_dict(cls, config:dict) -> "GaiClientConfig":
        """
        Class method to create an instance of GaiClientConfig from a dictionary.

        Parameters:
            config (dict): A dictionary containing the configuration data.

        Returns:
            GaiClientConfig: An instance of GaiClientConfig populated with the configuration data.

        Usage example:
            config = GaiClientConfig.from_dict(config={
                "url": "https://api.openai.com/v1/engines/davinci-codex/completions",
                "type": "openai",
                "engine": "davinci-codex",
                "model": "davinci-codex",
                "name": "OpenAI Codex",
                "client_type": "openai"
            })
        """        
        return cls._get_client_config(config=config)

    @classmethod
    def _get_gai_config(cls, file_path:str) -> Dict:
        gai_dict = None
        try:
            with open(file_path, 'r') as f:
                gai_dict = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            raise ValueError(f"GaiClientConfig: Error loading client config from file: {e}")
        return gai_dict    

    @classmethod
    def _get_client_config(
            cls,
            name: Optional[str] = None,
            config: Optional[dict] = None,
            file_path: Optional[str] = None    
        ) -> "GaiClientConfig":
        """
        Retrieves a GaiClientConfig object based on the provided arguments.

        Parameters:
            name (str, optional): The name of the configuration.
            config (dict, optional): A dictionary containing the configuration data.
            file_path (str, optional): Path to the configuration file.

        Returns:
            GaiClientConfig: The configuration object based on the provided arguments.

        Raises:
            ValueError: If the arguments are invalid or required keys are missing.

        Usage examples:
            1. Using a dict:
                config = GaiClientConfig.from_dict(config={
                    "url": "https://api.openai.com/v1/engines/davinci-codex/completions",
                    "type": "openai",
                    "engine": "davinci-codex",
                    "model": "davinci-codex",
                    "name": "OpenAI Codex",
                    "client_type": "openai"
                })

            2. Get default ttt config from a specific configuration file:
                config = ClientLLMConfig.from_name(name="ttt", file_path="config.yaml")

            3. Get default ttt config from ~/.gai/gai.yml:
                config = ClientLLMConfig.from_name(name="ttt")
        """
        
        if config:
            return cls(**config)
        
        if name:
            gai_dict = None
            try:
                app_dir=get_app_path()
                global_lib_config_path = os.path.join(app_dir, 'gai.yml')
                if file_path:
                    global_lib_config_path = file_path
                gai_dict = cls._get_gai_config(global_lib_config_path)
            except Exception as e:
                raise ValueError(f"GaiClientConfig: Error loading client config from file: {e}")

            client_config = None    
            client_config = gai_dict["clients"].get(name, None)
            if not client_config:
                raise ValueError(f"GaiClientConfig: Client Config not found. name={name}")
            return cls(**client_config)
        raise ValueError("GaiClientConfig: Invalid arguments. Either 'name' or 'config' must be provided.")
