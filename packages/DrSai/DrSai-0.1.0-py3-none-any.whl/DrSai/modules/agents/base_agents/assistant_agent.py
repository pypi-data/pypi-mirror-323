
from typing import Any, List, Dict, Union, Optional, Literal, Callable, Generator, Tuple
import os, sys, copy
from pathlib import Path
here = Path(__file__).parent


from DrSai.apis.base_agent_api import LearnableAgent
from DrSai.apis.base_agent_utils_api import HepAIWrapper
from DrSai.apis.autogen_api import (Agent, log_event, ConversableAgent,
                                  logging_enabled, start, stop, log_chat_completion, log_new_agent, log_new_wrapper, log_new_client, get_connection)
from DrSai.configs import CONST

import hepai
from hepai import HRModel, LRModel
from hepai import HepAI
import inspect
import logging
logger = logging.getLogger(__name__)


class AssistantAgent(LearnableAgent):
    """
    功能：
        + 可自定义回复函数worker_generate_reply, 深度开发消息列表的处理逻辑，支持传入其它任意参数
        + 可访问远程HepAI平台的远程无限函数worker，或者自定义消息列表处理类
    要求：
        + 无论是远程HepAI平台的远程无限函数worker还是自定义消息列表处理类, 都必须调用统一的interface函数接口进行消息列表处理
        + interface函数输出格式必须为纯文本/str生成器/openai stream 或者包括"content"字段的字典，如：{"status":str, "content":str, "image":base64},其他字段另加
        + 自定义回复函数worker_generate_reply自会在配置worker_name时才会生效
    """

    DEFAULT_SYSTEM_MESSAGE = """You are a helpful assisstant.""" 

    DEFAULT_DESCRIPTION = "A assistant agent that can interact with users and provide assistance."

    def __init__(
        self,
        name: str,
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = "NEVER",
        description: Optional[str] = DEFAULT_DESCRIPTION,
        worker_name: Optional[Union[object, str, Dict]] = None, 
        only_worker_reply: Optional[bool] = False, 
        **kwargs,
    ):
        '''
        worker_name: 自定义消息列表处理类或者HepAI平台的远程无限函数worker。
            如果worker_name为模型名字符串，则表示通过DDF1平台访问远程HepAI平台的远程无限函数worker。
            DDF1 平台具体见https://note.ihep.ac.cn/s/cZptfF8r9
            如果worker_name为字典，则表示通过DDF2平台访问远程HepAI平台的远程无限函数worker，字典字段必须包含"name"和"base_url"，请注意hepai版本必须>=1.1.18。
            DDF2 平台具体见https://aiapi001.ihep.ac.cn/mkdocs/workers/
        only_worker_reply: 是否只返回worker的回复，不使用其它的回复函数
        '''
        
        super().__init__(
            name,
            system_message=system_message,
            is_termination_msg=is_termination_msg,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            llm_config=llm_config,
            description=description,
            **kwargs,
        )

        if logging_enabled():
            log_new_agent(self, locals())
        
        # 判断是否使用自定义开发
        self.user_cofig: Dict = kwargs # 用户传递给自定义回复函数的自定义配置
        self._only_worker_reply: bool = only_worker_reply
        if worker_name is None:
            pass
        elif isinstance(worker_name, (str, Dict)):
            self._worker_name: Optional[Union[str, Dict]] = worker_name
            # 配置访问远程 DDF1 HepAI worker
            if isinstance(self._worker_name, str):
                self._api_key: str = llm_config["config_list"][0]["api_key"]
                self._base_url: str = CONST.BASE_URL
                self._hepai_client: HepAI = HepAI(api_key=self._api_key, base_url=self._base_url)
            # TODO: 配置远程访问 DDF2 HepAI worker
            elif isinstance(self._worker_name, Dict):
                self._hepai_client: LRModel = HRModel.connect(
                    **self._worker_name)
            self.register_reply([Agent, None], AssistantAgent.worker_generate_reply)
        elif isinstance(worker_name, object):
            # 判断是否是自定义消息列表处理类
            if hasattr(worker_name, 'interface'):
                self._worker_name: object = worker_name
                self.register_reply([Agent, None], AssistantAgent.worker_generate_reply)
            else:
                raise ValueError(f"worker_name should be a class with interface function, but got {worker_name}.")
        else:
            raise ValueError(f"worker_name should be a string, a dictionary or an object, but got {type(worker_name)}.")


    def hepai_model_api(self, messages, function="interface", **kwargs) -> Tuple[bool, Union[Dict, str, Generator]]:
        '''
        访问hepai DDF1平台的worker无限函数的统一接口
        '''
        try:
            models = hepai.Model.list(api_key = self.llm_config["config_list"][0]["api_key"])
            if self._worker_name in models:
                pass
            else:
                # raise ValueError("Model not found")
                return False, f"Worker <{self._worker_name}> not found"
        except Exception as e:
            # raise ValueError(f"Failed to connect to HepAI platform with error: {e}")
            return False, f"Failed to connect to HepAI platform with error: {e}"
        try:
            result: Union[Dict, str, Generator] = self._hepai_client.request_worker(model=self._worker_name, function=function, messages=messages, **kwargs)
            return True, result
        except Exception as e:
            # raise ValueError(f"Failed to execute the Worker Agent with error: {e}")
            return False, f"Failed to execute the <{self._worker_name}> with error: {e}"
    def hepai_model_api_v2(self, messages, **kwargs) -> Tuple[bool, Union[Dict, str, Generator]]:
        try:
            result: Union[Dict, str, Generator] = self._hepai_client.interface(messages = messages, **kwargs)
            return True, result
        except Exception as e:
            worker_name = self._worker_name.get("name", None)
            return False, f"Failed to execute the <{worker_name}> with error: {e}"

    def local_model_api(self, messages, **kwargs) -> Tuple[bool, Union[Dict, str, Generator]]:
        '''
        访问本地自定义消息列表处理类的统一接口
        '''
        try:
            result: Union[Dict, str, Generator] = self._worker_name.interface(messages=messages, **kwargs)
            return True, result
        except Exception as e:
            return False, f"Failed to execute the {self._worker_name.__class__.__name__} with error: {e}"
    
    def worker_generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[HepAIWrapper] = None,
        system_prompt: Optional[str] = None,
        **kwargs
        ) -> Tuple[bool, Union[str, Dict, None, Generator]]:
        '''
        + 将messages传递给worker进行处理
        + worker输出格式必须为纯文本/str生成器/openai stream 或者包括"content"字段的字典，如：{"status":str, "content":str, "image":base64},其他字段另加
        '''
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        if system_prompt is None:
            system_message = self._oai_system_message
        else:
            if isinstance(system_prompt, str):
                system_message = [{"content": system_prompt, "role": "system"}]
            else:
                system_message = system_prompt
        
        kwargs.update(self.user_cofig)

        # RAG
        messages_rag = copy.deepcopy(system_message + messages)
        if self._retrieve_config is not None:
            RAG_function: Callable = self._retrieve_config.get("RAG_function", None)
            if RAG_function is None:
                return True, "Error: RAG function is not set."
            RAG_config: Dict = self._retrieve_config.get("RAG_config", None)
            if RAG_config is None:
                return True, "Error: RAG config is not set."
            try:
                messages_rag: List[Dict] = RAG_function(messages_rag, RAG_config, **kwargs)
            except Exception as e:
                return True, f"Error: RAG function {RAG_function.__name__} failed with error {e}."

        
        # 调用worker接口
        if isinstance(self._worker_name, str):
            status, result = self.hepai_model_api(messages=messages_rag, function="interface", **kwargs)
        elif isinstance(self._worker_name, Dict):
            status, result = self.hepai_model_api_v2(messages=messages_rag, **kwargs)
        elif isinstance(self._worker_name, object):
            status, result = self.local_model_api(messages=messages_rag, **kwargs)
        else:
            return False, None

        if self._only_worker_reply:
            return True, result
        else:
            return status, result
    
