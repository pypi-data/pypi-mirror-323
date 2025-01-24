"""
Client RPC Builder
"""
import inspect
import logging
import time
from typing import Any, Callable, Dict, Optional, Union

import httpx
import pydantic_core
from pydantic import BaseModel, create_model

from ..security import BASIC_AUTH_TOKEN
from ..exception import OBORPCBuildException, RPCCallException

# httpx log level
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


class ClientBuilder:
    """
    Client Builder
    """
    __registered_base = set()

    def __init__(
        self,
        host: str,
        port: Optional[Union[str, int]] = None,
        timeout: Optional[float] = None,
        retry: Optional[int] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        dynamic_headers_builder: Optional[Callable] = None,
    ): # pylint: disable=too-many-arguments,too-many-positional-arguments
        self.master_instances = []
        self.host = host
        self.port = port
        self.timeout = timeout or 1
        self.retry = retry or 0
        self.before_call_middleware = []
        self.after_call_middleware = []

        protocol = "http://"
        if self.check_has_protocol(host):
            protocol = ""

        self.base_url = f"{protocol}{host}"
        if port:
            self.base_url += f":{port}"

        # dynamic header
        self.dynamic_headers_builder = dynamic_headers_builder or (lambda: {})

        # static header
        headers = {
            "Authorization": f"Basic {BASIC_AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        if additional_headers:
            headers.update(additional_headers)
        self.headers = headers

        # request client
        self.request_client = httpx.Client(
            base_url=self.base_url,
            headers=headers
        )
        self.async_request_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers
        )

        # model map
        self.model_maps = {}

    def check_has_protocol(self, host: str):
        """
        Check whether the given host already defined with protocol or not
        """
        if host.startswith("http://"):
            return True
        if host.startswith("https://"):
            return True
        return False

    def check_registered_base(self, base: str):
        """
        Check whether the base RPC class is already built
        """
        ClientBuilder.__registered_base.add(base)

    def create_remote_caller(
        self,
        class_name: str,
        method_name: str,
        url_prefix: str,
        timeout: float = None,
        retry: int = None
    ): # pylint: disable=too-many-arguments,too-many-positional-arguments
        """
        create remote caller
        """
        def remote_call(*args, **kwargs):
            """
            remote call wrapper
            """
            start_time = time.time()
            try:
                url = f"{url_prefix}/{class_name}/{method_name}"
                headers = self.headers.copy()
                headers.update(self.dynamic_headers_builder())

                # apply middleware
                request_options = RequestOptions(
                    json=pydantic_core.to_jsonable_python({
                        "args": args[1:],
                        "kwargs": kwargs
                    }),
                    timeout=timeout if timeout is not None else self.timeout,
                    headers=headers
                )
                request_options = self.before_call_hook(request_options)

                # call procedure
                response = self.request_client.post(url=url, **vars(request_options))
                if not response:
                    msg = f"rpc call failed method={method_name}"
                    raise RPCCallException(msg)

                # apply middleware
                response = self.after_call_hook(response)

                # wrap result
                data = response.json().get("data")
                return self.convert_model_response(class_name, method_name, data)

            except Exception as e:
                _retry = retry if retry is not None else self.retry
                if _retry:
                    return remote_call(*args, **kwargs, retry=_retry-1)

                if isinstance(e, RPCCallException):
                    raise e
                msg = f"rpc call failed method={method_name} : {e}"
                raise RPCCallException(msg) from e

            finally:
                elapsed = f"{(time.time() - start_time) * 1000}:.2f"
                logging.debug("[RPC-Clientt] remote call take %s ms", elapsed)

        return remote_call

    def create_async_remote_caller(
        self,
        class_name: str,
        method_name: str,
        url_prefix: str,
        timeout: float = None,
        retry: int = None
    ): # pylint: disable=too-many-arguments,too-many-positional-arguments
        """
        create async remote caller
        """
        async def async_remote_call(*args, **kwargs):
            """
            async remote call wrapper
            """
            start_time = time.time()
            try:
                data = pydantic_core.to_jsonable_python({"args": args[1:], "kwargs": kwargs})
                url = f"{url_prefix}/{class_name}/{method_name}"
                headers = self.headers.copy()
                headers.update(self.dynamic_headers_builder())

                # apply middleware
                request_options = RequestOptions(
                    json=pydantic_core.to_jsonable_python({
                        "args": args[1:],
                        "kwargs": kwargs
                    }),
                    timeout=timeout if timeout is not None else self.timeout,
                    headers=headers
                )
                request_options = self.before_call_hook(request_options)

                # call procedure
                response = await self.async_request_client.post(url=url, **vars(request_options))
                if not response:
                    msg = f"rpc call failed method={method_name}"
                    raise RPCCallException(msg)

                # apply middleware
                response = self.after_call_hook(response)

                # wrap result
                data = response.json().get("data")
                return self.convert_model_response(class_name, method_name, data)

            except Exception as e:
                _retry = retry if retry is not None else self.retry
                if _retry:
                    return await async_remote_call(*args, **kwargs, retry=_retry-1)

                if isinstance(e, RPCCallException):
                    raise e
                msg = f"rpc call failed method={method_name} : {e}"
                raise RPCCallException(msg) from e

            finally:
                elapsed = f"{(time.time() - start_time) * 1000}:.2f"
                logging.debug("[RPC-Clientt] remote call take %s ms", elapsed)

        return async_remote_call

    def build_client_rpc(self, instance: object, url_prefix: str = ""):
        """
        Setup client rpc
        """
        _class = instance.__class__
        iterator_class = _class

        self.check_registered_base(_class)

        for (name, method) in inspect.getmembers(iterator_class, predicate=inspect.isfunction):
            if name not in iterator_class.__oborprocedures__:
                continue
            class_name = _class.__name__
            self.extract_models(class_name, name, method)
            setattr(_class, name, self.create_remote_caller(class_name, name, url_prefix))

    def build_async_client_rpc(self, instance: object, url_prefix: str = ""):
        """
        Setup async client rpc
        """
        _class = instance.__class__
        iterator_class = _class

        self.check_registered_base(_class)

        for (name, method) in inspect.getmembers(iterator_class, predicate=inspect.isfunction):
            if name not in iterator_class.__oborprocedures__:
                continue
            class_name = _class.__name__
            self.extract_models(class_name, name, method)
            setattr(_class, name, self.create_async_remote_caller(class_name, name, url_prefix))

    def extract_models(
        self,
        class_name: str,
        method_name: str,
        method: Callable
    ):
        """
        Extract pydantic model
        """
        if not class_name in self.model_maps:
            self.model_maps[class_name] = {}

        signature_params = inspect.signature(method).parameters
        params = {
            k: (
                v.annotation if v.annotation != inspect._empty else Any,
                v.default if v.default != inspect._empty else ...
            ) for k, v in signature_params.items()
        }

        signature_return = inspect.signature(method).return_annotation
        self.model_maps[class_name][method_name] = [
            create_model(f"{class_name}_{method_name}", **params),
            signature_return
        ]

    def convert_model_response(
        self,
        class_name: str,
        method_name: str,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert Pydantic Model Response
        """
        model, return_annotation = self.model_maps[class_name][method_name]
        try:
            if BaseModel.__subclasscheck__(return_annotation.__class__):
                return model.model_validate(response)
        except:
            pass
        return response

    def before_call(self, fun):
        """
        ```python
        @builder.before_call
        def my_before_call(options: RequestOptions) -> RequestOptions:
            ...
            return options
        ```
        """
        def wrapped(request_options: RequestOptions) -> RequestOptions:
            return fun(request_options)
        self.before_call_middleware.append(wrapped)
        return wrapped

    def after_call(self, fun):
        """
        ```python
        @builder.after_call
        def my_after_call(response: Response) -> Response:
            ...
            return response
        ```
        """
        def wrapped(response: httpx.Response) -> httpx.Response:
            return fun(response)
        self.after_call_middleware.append(wrapped)
        return wrapped

    def before_call_hook(self, request_options: "RequestOptions") -> "RequestOptions":
        for hook in self.before_call_middleware:
            request_options = hook(request_options)
        return request_options

    def after_call_hook(self, response: httpx.Response) -> httpx.Response:
        for hook in self.after_call_middleware:
            response = hook(response)
        return response


class RequestOptions:
    def __init__(
        self,
        content=None,
        data=None,
        files=None,
        json=None,
        params=None,
        headers=None,
        cookies=None,
        auth=httpx.USE_CLIENT_DEFAULT,
        follow_redirects=httpx.USE_CLIENT_DEFAULT,
        timeout=httpx.USE_CLIENT_DEFAULT,
        extensions=None,
    ) -> None:
        self.content = content
        self.data = data
        self.files = files
        self.json = json
        self.params = params
        self.headers = headers
        self.cookies = cookies
        self.auth = auth
        self.follow_redirects = follow_redirects
        self.timeout = timeout
        self.extensions = extensions
