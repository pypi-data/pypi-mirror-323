
import os, sys
import copy
from typing import Any, Dict, List, Optional, Tuple, Union, Generator
import uuid
from DrSai.apis.autogen_api import OpenAIWrapper, PlaceHolderClient, OpenAIClient, ModelClient
from DrSai.apis.autogen_api import logging_enabled, log_new_client, get_current_ts, log_chat_completion
from flaml.automl.logger import logger_formatter
import logging
import ast
import time
import json
from openai import APITimeoutError, APIError, Stream

from .hepai_client import HepAIInheritedFromOpenAI, HepAIClient


logger = logging.getLogger(__name__)
if not logger.handlers:
    # Add the console handler.
    _ch = logging.StreamHandler(stream=sys.stdout)
    _ch.setFormatter(logger_formatter)
    logger.addHandler(_ch)


class HepAIWrapper(OpenAIWrapper):
    def __init__(self, *, config_list: Optional[List[Dict[str, Any]]] = None, **base_config: Any):
        super().__init__(config_list=config_list, **base_config)

    def __repr__(self) -> str:
        return f'HepAIWrapper(config_list={self._clients})'

    def _register_default_client(self, config: Dict[str, Any], openai_config: Dict[str, Any]) -> None:
        """(Hai Rewrite) Create a client with the given config to override openai_config,
        after removing extra kwargs.

        For Azure models/deployment names there's a convenience modification of model removing dots in
        the it's value (Azure deploment names can't have dots). I.e. if you have Azure deployment name
        "gpt-35-turbo" and define model "gpt-3.5-turbo" in the config the function will remove the dot
        from the name and create a client that connects to "gpt-35-turbo" Azure deployment.
        """
        openai_config = {**openai_config, **{k: v for k, v in config.items() if k in self.openai_kwargs}}
        api_type = config.get("api_type", None)

        if api_type == 'hepai':
            proxy = config.get("proxy", None)
            hepai_config = copy.deepcopy(openai_config)
            hepai_config = {**hepai_config, **{"proxy": proxy}}
            client = HepAIInheritedFromOpenAI(**hepai_config)
            # self._clients.append(OpenAIClient(client))
            self._clients.append(HepAIClient(client))
            if logging_enabled():
                log_new_client(client, self, openai_config)
            return
        
        super()._register_default_client(config, openai_config)

    
    def _separate_create_config(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        create_config, extra_config = super()._separate_create_config(config)
        create_config.pop("proxy", None)  # proxy已经在初始化Client时使用了，不需要再传给completion.create
        return create_config, extra_config
    
    def create(self, **config: Any) -> ModelClient.ModelClientResponseProtocol:
        need_steam_obj = config.get("need_stream_obj", False)
        sse_format = config.get("sse_format", False)

        n = config.get("n", 1)
        if need_steam_obj:
            stream_obj = self.create_stream_obj(config)  # openai Stream
            if sse_format:
                generator: Generator = self.oai_stream2generator(stream_obj, n=n)
                return generator
            else:
                return stream_obj
        return super().create(**config)
    
    
    def create_stream_obj(self, config: Any) -> Stream:
        # if ERROR:
            # raise ERROR
        request_model = config.pop("model", None)
        request_temperature = config.pop("temperature", None)

        invocation_id = str(uuid.uuid4())
        last = len(self._clients) - 1
        # Check if all configs in config list are activated
        non_activated = [
            client.config["model_client_cls"] for client in self._clients if isinstance(client, PlaceHolderClient)
        ]
        if non_activated:
            raise RuntimeError(
                f"Model client(s) {non_activated} are not activated. Please register the custom model clients using `register_model_client` or filter them out form the config list."
            )
        for i, client in enumerate(self._clients):
            # merge the input config with the i-th config in the config list
            config_list = self._config_list[i]
            if request_model:  # 外部请求了这个模型，就判断是否配置了这个模型
                if request_model != config_list['model']:  # 外部请求了这个模型，但并未配置
                    continue
            if request_temperature is not None:
                config_list = config_list.copy()
                config_list['temperature'] = request_temperature
            full_config = {**config, **config_list}
            # full_config = {**config, **self._config_list[i]}
            # separate the config into create_config and extra_kwargs
            create_config, extra_kwargs = self._separate_create_config(full_config)
            api_type = extra_kwargs.get("api_type")
            if api_type and api_type.startswith("azure") and "model" in create_config:
                create_config["model"] = create_config["model"].replace(".", "")
            # construct the create params
            params = self._construct_create_params(create_config, extra_kwargs)
            # get the cache_seed, filter_func and context
            try:
                request_ts = get_current_ts()
                response = client.create(params)
                pass
            except APITimeoutError as err:
                logger.debug(f"config {i} timed out", exc_info=True)
                if i == last:
                    raise TimeoutError(
                        "OpenAI API call timed out. This could be due to congestion or too small a timeout value. The timeout can be specified by setting the 'timeout' value (in seconds) in the llm_config (if you are using agents) or the OpenAIWrapper constructor (if you are using the OpenAIWrapper directly)."
                    ) from err
            except APIError as err:
                error_code = getattr(err, "code", None)
                if logging_enabled():
                    log_chat_completion(
                        invocation_id=invocation_id,
                        client_id=id(client),
                        wrapper_id=id(self),
                        request=params,
                        response=f"error_code:{error_code}, config {i} failed",
                        is_cached=0,
                        cost=0,
                        start_time=request_ts,
                    )

                if error_code == "content_filter":
                    # raise the error for content_filter
                    raise
                logger.debug(f"config {i} failed", exc_info=True)
                if i == last:
                    raise
            return response
        raise ValueError(f'Model "{request_model}" is not found in the config list.')


    @classmethod
    def extract_text_or_completion_object(
        cls, response: ModelClient.ModelClientResponseProtocol
    ) -> Union[List[str], List[ModelClient.ModelClientResponseProtocol.Choice.Message]]:
        response = super().extract_text_or_completion_object(response)
        # 解析字符串表示的字典
        # new_response = []
        # for res in response:
        #     if isinstance(res, str):
        #         try:
        #             new_res = ast.literal_eval(res)
        #             new_response.append(new_res)
        #         except:
        #             new_response.append(res)
        #     else:
        #         new_response.append(res)
        # return new_response
        return response
    
    def oai_stream2generator(self, stream: Stream, n=1) -> Generator:
        """将openai.Stream转为generator"""
        assert n == 1, "n > 1 is not supported yet."
        # 转换一个一个chunk
        for chunk in stream:
            chunk_dict = chunk.__dict__
            if chunk.choices:
                choices_list = []
                for choice in chunk.choices:
                    choice_dict = choice.__dict__
                    # 转换delta
                    choice_dict["delta"] = choice_dict["delta"].__dict__

                    choices_list.append(choice_dict)
                chunk_dict["choices"] = choices_list

            # yield f"{json.dumps(chunk_dict)}\n"
            yield f"data: {json.dumps(chunk_dict)}\n\n"
    

