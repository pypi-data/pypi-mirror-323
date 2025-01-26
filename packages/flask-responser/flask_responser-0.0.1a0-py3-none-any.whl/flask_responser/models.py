import json
from flask import Response

from .utils import is_empty

class Response:
    __doc__ = """
        :param status_code: HTTP status code
        :param ext_mes: External message
        :param int_mes: Internal message
        :param int_code: Internal status code
        :param data: Data
        
        `status_code` is shown to the browser, like 200/500.
        `ext_mes` is shown to the user(js script can print it out originally to users), like "Login success".
        `int_mes` is shown to the front-end developers(FEDS), in order to debug in their developments. With `dev` set to True and `int_mes` not set, it will automatically set to the same as `ext_mes`.
        `int_code` is used to distinguish different error types for FEDS. With `dev` set to True and `int_code` not set, it will automatically set to the same as `status_code`.
        `data` is the necessary data that need to be returned to the front-end.
        
        If `dev` is set to False, `int_mes` and `int_code` will be ignored if they are not set.
    """
    def __init__(self, 
                 status_code: int=200, 
                 ext_mes: str="", int_mes: str="", 
                 int_code: int=0,
                 data: dict=None,
                 dev: bool=True,
                 **kwargs):
        """
        :param status_code: HTTP status code
        :param ext_mes: External message
        :param int_mes: Internal message
        :param int_code: Internal status code
        :param data: Data
        
        `status_code` is shown to the browser, like 200/500.
        `ext_mes` is shown to the user(js script can print it out originally to users), like "Login success".
        `int_mes` is shown to the front-end developers(FEDS), in order to debug in their developments. With `dev` set to True and `int_mes` not set, it will automatically set to the same as `ext_mes`.
        `int_code` is used to distinguish different error types for FEDS. With `dev` set to True and `int_code` not set, it will automatically set to the same as `status_code`.
        `data` is the necessary data that need to be returned to the front-end.
        
        If `dev` is set to False, `int_mes` and `int_code` will be ignored if they are not set.
        """
        self.ext_code = status_code
        self.ext_mes = ext_mes
        if is_empty(int_mes):
            if dev:
                self.int_mes = ext_mes
            else:
                self.int_mes = int_mes
        else:
            self.int_mes = int_mes
        if is_empty(int_code):
            if dev:
                self.int_code = status_code
            else:
                self.int_code = int_code
        else:
            self.int_code = int_code
        self._data = data
        self.dev = dev
        self.kwargs = kwargs
        
    def _predeal(self):
        self.data = {}
        if not is_empty(self.int_code): self.data["code"] = self.int_code
        if not is_empty(self.ext_mes): self.data["mes"] = self.ext_mes
        if not is_empty(self.int_mes): self.data["data"]["mes"] = self.int_mes
        if not is_empty(self._data): self.data["data"]["data"] = self._data
        
    def make(self):
        self._predeal()
        response = Response(
            response=json.dumps(self.data),
            status=self.ext_code,
            mimetype='application/json'
        )
        for k,v in self.kwargs.items():
            response.headers[k] = v
        return response