import os
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, List
from gai.lib.common.utils import get_app_path

from gai.lib.config.client_config import GaiClientConfig
from gai.lib.config.generator_config import GaiGeneratorConfig

class LogConfig(BaseSettings):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"
    filename: Optional[str] = None
    filemode: str = "a"
    stream: str = "stdout"
    loggers: Optional[Dict] = None
    
class GaiConfig(BaseSettings):
    version: str
    gai_url: str
    logging: LogConfig
    clients: Optional[dict[str,GaiClientConfig] ] = None
    generators: Optional[dict[str,GaiGeneratorConfig] ] = None
    class Config:
        extra = "ignore"

    @classmethod
    def from_path(cls, file_path=None) -> "GaiConfig":
        """
        Class method to create an instance of GaiConfig from a YAML configuration file.

        Parameters:
            file_path (str, optional): Path to the configuration file. If not provided,
                                       the default path 'gai.yml' in the application directory is used.

        Returns:
            GaiConfig: An instance of GaiConfig populated with the configuration data.

        Usage example:
            config = GaiConfig.from_config()
        """
        app_dir=get_app_path()
        global_lib_config_path = os.path.join(app_dir, 'gai.yml')
        if file_path:
            global_lib_config_path = file_path
        with open(global_lib_config_path, 'r') as f:
            dict = yaml.load(f, Loader=yaml.FullLoader)
            gai_config = GaiConfig(**dict)
            return gai_config
        return config
