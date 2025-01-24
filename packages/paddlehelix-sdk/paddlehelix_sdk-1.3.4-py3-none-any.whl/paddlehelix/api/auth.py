"""
PaddleHelix鉴权
"""
import hashlib
import hmac
import time
import urllib.parse

Host = "chpc.bj.baidubce.com"
Method = "POST"
Query = ""
SignedHeaders = "content-type;host;x-bce-date"
AuthExpireTime = 1800


class APIAuthUtil:
    def __init__(self, ak: str = "", sk: str = ""):
        self.__ak = ak
        self.__sk = sk

        assert len(self.__ak.strip()) > 0, "AK 为空"
        assert len(self.__sk.strip()) > 0, "SK 为空"

    def generate_header(self, uri: str = "", **kwargs) -> dict:
        assert len(uri) > 0, "uri 为空"
        x_bce_date = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        header = {
            "Host": Host,
            "content-type": "application/json;charset=utf-8",
            "x-bce-date": x_bce_date
        }
        result = []
        for key, value in header.items():
            temp_str = str(urllib.parse.quote(key.lower(), safe="")) + ":" + str(urllib.parse.quote(value, safe=""))
            result.append(temp_str)
        result.sort()
        canonical_request = "".join([Method, "\n", urllib.parse.quote(uri), "\n", Query, "\n", "\n".join(result)])
        auth_string_prefix = "".join(["bce-auth-v1", "/", self.__ak, "/", x_bce_date, "/", str(AuthExpireTime)])
        signing_key = hmac.new(self.__sk.encode('utf-8'), auth_string_prefix.encode('utf-8'), hashlib.sha256)
        signature = hmac.new((signing_key.hexdigest()).encode('utf-8'), canonical_request.encode('utf-8'), hashlib.sha256)
        header['Authorization'] = auth_string_prefix + "/" + SignedHeaders + "/" + signature.hexdigest()
        return header
