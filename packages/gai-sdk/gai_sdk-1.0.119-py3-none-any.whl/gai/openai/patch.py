from gai.lib.common.generators_utils import chat_string_to_list
from gai.lib.common.logging import getLogger
logger = getLogger(__name__)
from gai.lib.config import GaiClientConfig


from openai.types.chat_model import ChatModel
from openai import OpenAI
from typing import get_args,Union, Optional,Callable
from gai.openai.attach_extractor import attach_extractor
import inspect
from pydantic import BaseModel

from gai.ttt.client.ttt_client import TTTClient
from ollama import chat


# This class is used by the monkey patch to override the openai's chat.completions.create() function.
# This is also the class responsible for for GAI's text-to-text completion.
# The main driver is the create() function that can be used to generate or stream completions as JSON output.
# The output from create() should be indisguishable from the output of openai's chat.completions.create() function.
#
# Example:
# from openai import OpenAI
# client = OpenAI()
# from gai.openai.patch import patch_chatcompletions
# openai=patch_chatcompletions(openai)
# openai.chat.completions.create(model="llama3.1", messages=[{"role": "system", "content": "You are a helpful assistant."}], max_tokens=100)

# override_get_client_from_model is meant to be used for unit testing
def patch_chatcompletions(openai_client:OpenAI, file_path:str=None):

    # Save the original openai functions
    openai_create = openai_client.chat.completions.create
    openai_parse = openai_client.beta.chat.completions.parse
    
    def is_BaseModel(item):
        """
        Check if the given item is a subclass of BaseModel.
        This is used to validate response_format.

        Parameters:
            item: The item to check.

        Returns:
            bool: True if the item is a subclass of BaseModel, False otherwise.
        """
        return inspect.isclass(item) and issubclass(item, BaseModel)    
    
    
    # Replace openai.completions.create with a wrapper over the original create function
    def patched_create(**kwargs):
        # The model is required to determine the client type patched to the openai_client so it should be determined first.
        model = kwargs.get("model", None)
        if not model:
            raise Exception("completions.patched_create: Model not provided")

        # Based on the model name, determine the client used to generate completions, eg. "gai" uses ttt_client.
        client_config = GaiClientConfig.from_name(model)
        if file_path:
            # When used for testing outside of docker-compose, use gai.localhost.yml
            # otherwise default to ~/.gai/gai.yml
            client_config = GaiClientConfig.from_name(model,file_path)
        
        # a) openai model
        if client_config and client_config.client_type == "openai" and client_config.model in get_args(ChatModel):
            stream=kwargs.get("stream",False)
            response = openai_create(**kwargs)
            response = attach_extractor(response,stream)
            return response
        
        # b) ollama model
        if client_config and client_config.client_type == "ollama":
            
            # Map openai parameters to ollama parameters
            kwargs={
                # Get actual model from config and not from model parameter
                "model": client_config.model,
                "messages": kwargs.get("messages", None),
                "options": {
                    "temperature": kwargs.get("temperature", None),
                    "top_k": kwargs.get("top_k", None),
                    "top_p": kwargs.get("top_p", None),
                    "num_predict" : kwargs.get("max_tokens", None),
                },
                "stream": kwargs.get("stream", False),
                "tools": kwargs.get("tools", None),
            }
            if kwargs.get("tools"):
                kwargs["stream"] = False
            response = chat(**kwargs)
            
            # Format ollama output to match openai output
            stream = kwargs["stream"]
            tools = kwargs["tools"]
            
            from gai.openai.ollama_response_builders.completions_factory import CompletionsFactory
            factory = CompletionsFactory()
            if stream and not tools:
                response = factory.chunk.build_stream(response)
                response = attach_extractor(response,stream)  
                response = (chunk for chunk in response)
            else:
                if tools:
                    response = factory.message.build_toolcall(response)
                else:
                    response = factory.message.build_content(response)
                response = attach_extractor(response,stream)
            return response
        
        # c) gai model        
        if client_config and client_config.client_type == "gai":
            
            # Map openai parameters to gai parameters
            kwargs = {
                "messages": kwargs.get("messages", None),
                "stream": kwargs.get("stream", False),
                "max_tokens": kwargs.get("max_tokens", None),
                "temperature": kwargs.get("temperature", None),
                "top_p": kwargs.get("top_p", None),
                "top_k": kwargs.get("top_k", None),
                "tools": kwargs.get("tools", None),
                "tool_choice": kwargs.get("tool_choice", None),
                "stop": kwargs.get("stop", None),
                "timeout": kwargs.get("timeout", None),
            }

            ttt = TTTClient(client_config)
            response = ttt(**kwargs)
            return response

        raise Exception(f"completions.patched_create: Model {model} not found in config")

        
    # Used with response_format    
    def patch_parse(**kwargs):
        # The model is required to determine the client type patched to the openai_client so it should be determined first.
        model = kwargs.get("model", None)
        if not model:
            raise Exception("completions.patched_parse: Model not provided")

        # Response format is required
        response_format = kwargs.get("response_format", None)
        if not response_format:
            raise Exception("completions.patched_parse: response_format is not provided")

        # Based on the model name, determine the client used to generate completions, eg. "gai" uses ttt_client.
        client_config = GaiClientConfig.from_name(model)
        if file_path:
            # When used for testing outside of docker-compose, use gai.localhost.yml
            # otherwise default to ~/.gai/gai.yml
            client_config = GaiClientConfig.from_name(model,file_path)

        # a) openai model
        if client_config and client_config.client_type == "openai" and client_config.model in get_args(ChatModel):
            stream=kwargs.pop("stream",False)
            response = openai_parse(**kwargs)
            response = attach_extractor(response,stream)
            return response
        
        # b) ollama model
        if client_config and client_config.client_type == "ollama":
            
            # Map openai parameters to ollama parameters
            kwargs={
                # Get actual model from config and not from model parameter
                "model": client_config.model,
                "messages": kwargs.get("messages", None),
                "options": {
                    "temperature": 0,
                    "num_predict" : kwargs.get("max_tokens", None),
                },
                "stream": False,
            }
            if is_BaseModel(response_format):
                schema = response_format.model_json_schema()
                kwargs["format"] = schema
            elif type(response_format) is dict:
                kwargs["format"] = response_format["json_schema"]["schema"]
            else:
                raise Exception("completions.patched_parse: response_format must be a dict or a pydantic BaseModel")    
            response = chat(**kwargs)
            
            # Format ollama output to match openai output
            stream = kwargs["stream"]
            from gai.openai.ollama_response_builders.completions_factory import CompletionsFactory
            factory = CompletionsFactory()
            response = factory.message.build_content(response)
            response = attach_extractor(response,stream)
            return response        

        # c) gai model
        if client_config and client_config.client_type == "gai":
            
            # Map openai parameters to gai parameters
            kwargs = {
                "messages": kwargs.get("messages", None),
                "stream": False,
                "max_tokens": kwargs.get("max_tokens", None),
                "timeout": kwargs.get("timeout", None),
            }
            if is_BaseModel(response_format):
                schema = response_format.model_json_schema()
                kwargs["json_schema"] = schema
            elif type(response_format) is dict:
                kwargs["json_schema"] = response_format["json_schema"]["schema"]
            else:
                raise Exception("completions.patched_parse: response_format must be a dict or a pydantic BaseModel")    

            ttt = TTTClient(client_config)
            response = ttt(**kwargs)
            return response

    openai_client.chat.completions.create = patched_create    
    openai_client.beta.chat.completions.parse = patch_parse
    
    return openai_client    




