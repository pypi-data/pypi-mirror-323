import os
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict
from gai.lib.common.utils import get_app_path

class ModuleConfig(BaseSettings):
    name: str
    class_: str = Field(alias="class")  # Use 'class' as an alias for 'class_'

    class Config:
        allow_population_by_name = True  # Allow access via both 'class' and 'class_'

class GaiGeneratorConfig(BaseSettings):
    type: str
    engine: str
    model: str
    name: str
    hyperparameters: Optional[Dict] = {}
    extra: Optional[Dict] = None
    module: ModuleConfig
    class Config:
        extra = "allow"

    @classmethod
    def from_name(cls,name:str, file_path:str=None) -> "GaiGeneratorConfig":
        return cls._get_generator_config(name=name, file_path=file_path)
    
    @classmethod
    def from_dict(cls, config:dict) -> "GaiGeneratorConfig":
        return cls._get_generator_config(config=config)
    
    @classmethod
    def _get_generator_config(
            cls,
            name: Optional[str] = None,
            config: Optional[dict] = None,
            file_path: Optional[str] = None    
        ) -> "GaiGeneratorConfig":
        if config:
            return cls(**config)
        if name:
            gai_dict = None
            try:
                app_dir=get_app_path()
                global_lib_config_path = os.path.join(app_dir, 'gai.yml')
                if file_path:
                    global_lib_config_path = file_path
                with open(global_lib_config_path, 'r') as f:
                    gai_dict = yaml.load(f, Loader=yaml.FullLoader)
            except Exception as e:
                raise ValueError(f"GaiClientConfig: Error loading client config from file: {e}")

            generator_config = None
            generator_config = gai_dict["generators"].get(name, None)
            if not generator_config:
                raise ValueError(f"GaiGeneratorConfig: Generator Config not found. name={name}")            
            return cls(**generator_config)
        raise ValueError("GaiGeneratorConfig: Invalid arguments. Either 'name' or 'config' must be provided.")
