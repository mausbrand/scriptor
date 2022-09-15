"""
WARNING! THIS SCRIPT IS USED IN A SANDBOX SO ALL DEPENDENCIES SHOULD BE HANDLED HERE!
"""

import csv as _csv
import json as _json
import pyodide as _pyodide

from urllib.parse import urlencode as _urlencode
from js import self as _self, Blob, FormData, URL, XMLHttpRequest
from io import StringIO


class _Request:
    def __init__(self, method, url, params=None):
        super().__init__()
        self.status = None
        self.result = None

        self.method = method.upper()
        assert self.method in ("POST", "GET")

        if not url.startswith("/"):
            url = "/" + url

        if self.method == "GET" and params:
            url += "?" + _urlencode(params)
            self.send = None
        else:
            self.send = FormData.new()

            if params:
                for k, v in params.items():
                    self.send.append(k, v)

        self.url = "/vi" + url
        self.request = XMLHttpRequest.new()
        # self.request.onreadystatechange = self.readystatechange
        self.readystatechange_proxy = _pyodide.create_proxy(self.readystatechange)
        self.request.onreadystatechange = self.readystatechange_proxy

        self.request.open(method, self.url, False)

    def readystatechange(self, *args, **kwargs):
        # print("readystatechange", self.request.readyState)
        match self.request.readyState:
            case 1:
                if self.method == "POST" and self.send:
                    self.request.send(self.send)
                else:
                    self.request.send()

            case 4:
                self.status = self.request.status

                if 200 <= self.status < 300:
                    self.result = _json.loads(self.request.responseText)

    def __del__(self):
        self.readystatechange_proxy.destroy()

    @staticmethod
    def get(*args, **kwargs):
        return _Request("GET", *args, **kwargs).result

    @staticmethod
    def post(*args, **kwargs):
        return _Request("POST", *args, **kwargs).result


class viur:

    @staticmethod
    def view(*args, **kwargs):
        if not (ret := _Request.get(*args, **kwargs)):
            return ret

        return ret["values"]

    class list:
        """
        Fetches a list from a VIUR module
        """

        def __init__(self, url, params=None):
            self.url = url
            self.params = params or {}

            self.batch = []
            self.cursor = None
            self.fetched = False

        def __iter__(self):
            self.cursor = None
            self.fetched = False
            return self

        def __next__(self):
            if self.batch:
                return self.batch.pop()

            if self.fetched and not self.cursor:
                raise StopIteration

            if self.cursor:
                self.params["cursor"] = self.cursor

            ret = _Request.get(self.url, self.params)
            self.fetched = True

            if not ret:
                raise StopIteration

            self.batch = ret["skellist"]
            self.cursor = ret["cursor"]

            if not self.batch:
                self.cursor = None

            return next(self)


class csvwriter:
    """
    Writer for CSV exports
    """

    def __init__(self, *args, delimiter=";"):
        super().__init__()
        self.file = StringIO()
        self.file.write("\ufeff")  # excel needs this for right utf-8 decoding
        self.lines = 0

        if args:
            self.writer = _csv.DictWriter(
                self.file,
                fieldnames=args,
                extrasaction="ignore",
                delimiter=delimiter,
                dialect="excel",
                quoting=_csv.QUOTE_ALL
            )
            self.writer.writeheader()
        else:
            self.writer = _csv.writer(
                self.file,
                delimiter=delimiter,
                dialect="excel",
                quoting=_csv.QUOTE_ALL
            )

    def fmt(self, value):
        if isinstance(value, list):
            return ", ".join([self.fmt(v) for v in value])
        elif isinstance(value, dict):
            return _json.dumps(value, sort_keys=True)

        return str(value)

    def write(self, values):
        if isinstance(values, dict):
            assert isinstance(self.writer, _csv.DictWriter)
            self.writer.writerow({k: self.fmt(v) for k, v in values.items() if k in self.writer.fieldnames})
            self.lines += 1
        elif isinstance(values, list):
            if isinstance(self.writer, _csv.DictWriter):
                for row in values:
                    self.write(row)
            else:
                self.writer.writerow([self.fmt(v) for v in values])
                self.lines += 1
        else:
            raise NotImplementedError(f"Don't know what to do with {repr(values)}")

    def download(self, name="export.csv"):
        blob = Blob.new([str(self)], **{
            "type":"application/csv;charset=utf-8;"
        })

        #send blob to app
        _self.postMessage(type="download", blob=blob, filename=name)

    def __str__(self):
        return self.file.getvalue()

    def __len__(self):
        return self.lines


class Logging():

    @staticmethod
    def print(*args, level=None):
        items = []

        # Either convert to JSON, fallback to string.
        for item in args:
            if not isinstance(item, (str, int, float, bool)):
                try:
                    item = _json.dumps(item, indent=4, skipkeys=True, sort_keys=True)
                except TypeError:
                    item = str(item)

            items.append(item)

        _self.postMessage(type="print", items=_pyodide.ffi.to_js(items), level=level or "")

    @staticmethod
    def debug(*args):
        Logging.print(*args, level="debug")

    @staticmethod
    def info(*args):
        Logging.print(*args, level="info")

    @staticmethod
    def warning(*args):
        Logging.print(*args, level="warning")

    @staticmethod
    def error(*args):
        Logging.print(*args, level="error")


logging = Logging()


def exit():
    _self.postMessage(type="exit")


def print(*args):
   logging.print(*args)
