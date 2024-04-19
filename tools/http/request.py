# -*- coding: utf-8 -*-
import requests
import json
import re
from requests.exceptions import ConnectionError
from requests_toolbelt import MultipartEncoder
from copy import deepcopy


def serialization_obj(content, encoding='utf-8'):
    try:
        return json.dumps(content, encoding=encoding, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e.__str__())
        return str(content)


def form_data_post(url, data, headers):
    for key in list(data):
        data.update({key: json.dumps(data[key], ensure_ascii=False) if not isinstance(data[key], str) else data[key]})
    m = MultipartEncoder(data)
    headers['Content-Type'] = m.content_type
    resp = requests.post(url, headers=headers, data=m, timeout=10)
    return resp


def retry(times):
    global count
    count = 0

    def decorated(func):
        def wrapper(*args, **kwargs):
            global result
            try:
                result = func(*args, **kwargs)
            except ConnectionError as e:
                global count
                count += 1
                # print("This is count %s" % count)
                if count < times:
                    wrapper(*args, **kwargs)
                result = {"ret": str(e)}
            return result

        return wrapper

    return decorated



class ApiRequest:

    def api(self, req_url, req_method, params=None, files=None, headers=None, cookies=None, cert=None, timeout=100,
                log=None, verify=False):
        pattern = r"^http(s|)://[\w.]{1,100}:[\d]{1,2}443/[\w/]+$"
        if re.match(pattern, req_url) and re.match(pattern, req_url).group(0):
            req_url = req_url.replace("http", "https") if not req_url.startswith("https") else req_url
        method = req_method.upper()
        # 校验 headers 是否为中文格式
        name_pattern = re.compile(r'[^\x00-\xff]')
        if re.findall(name_pattern, str(headers)):
            if log:
                log.info(f"The server did not meet the expected request header field.\n{serialization_obj(headers)}")
            return {"status_code": 417, "ret": "The server did not meet the expected request header field."}
        ret = self.request_data(req_url, method, params, files=files, headers=headers, cookies=cookies, cert=cert,
                        allow_redirects=False, timeout=timeout, verify=verify)
        if log:
            log.info(f'{method} : {req_url}\n{serialization_obj(headers)}\n{serialization_obj(params)}\n{str(files)}\n'
                    f'{serialization_obj(ret)}')
            log.removeHandler(log.handlers)
        return ret

    
    @retry(5)
    def request_data(self, url, method, param, files, **kwargs):
        """
        :param url: 接口请求地址url
        :param method: 请求的方法（DEBUG或者MOCK，其中MOCK为自己构造的返回）
        :param param:  请求的参数
        :param files:  请求的文件
        :param kwargs: 其他需要的kwargs
        :return: 请求返回数据
        """
        ret = None
        if method == "POST":
            headers = kwargs.get("headers")
            if headers:
                content_type = headers.get("Content-Type")
                if content_type:
                    if "application/json" in content_type:
                        ret = requests.post(url, json=param, files=files, **kwargs)

                    if "x-www-form-urlencoded" in content_type:
                        ret = requests.post(url, data=param, files=files, **kwargs)

                    if "form-data" in content_type:
                        tmp = []
                        if param:
                            data = deepcopy(param)
                            if isinstance(data, dict):
                                for k,v in data.items():
                                    if isinstance(v, str):
                                        tmp.append((k, v))
                                    elif isinstance(v, list):
                                        for x in v:
                                            tmp.append((k, str(x)))
                                    else:
                                        tmp.append((k, json.dumps(v, ensure_ascii=False)))
                        if files:
                            for k, v in files.items():
                                tmp.append((k, v))
                        m = MultipartEncoder(tmp)
                        headers = kwargs.pop("headers")
                        headers['Content-Type'] = m.content_type
                        ret = requests.post(url, headers=headers, data=m, **kwargs)
            if ret is None:
                ret = requests.post(url, json=param, files=files, **kwargs)
        elif method == "GET":
            ret = requests.get(url, **kwargs)
        elif method == "DELETE":
            ret = requests.delete(url, json=param, **kwargs)
        elif method == "PUT":
            ret = requests.put(url, json=param, **kwargs)
        elif method == "PATCH":
            ret = requests.patch(url, json=param, **kwargs)
        try:
            ret_new = ret.json()
            if isinstance(ret_new, list) or isinstance(ret_new, int):
                ret_new = {"status_code": ret.status_code, "elapsed": ret.elapsed.microseconds / 1000, "ret": ret_new}
            elif isinstance(ret_new, str):
                ret_new = self.get_ret(ret)
                ret_new.update({"status_code": ret.status_code, "elapsed": ret.elapsed.microseconds / 1000})
            else:
                ret_new.update({"elapsed": ret.elapsed.microseconds / 1000})
                if not ret_new.get("status_code"):
                    ret_new.update({"status_code": ret.status_code})
            return ret_new
        except Exception as e:
            print(e.__str__())
            return {"status_code": ret.status_code, "ret": ret.text, "elapsed": ret.elapsed.microseconds / 1000}


    def get_ret(self, ret):
        try:
            ret_new = json.loads(str(ret.json()).encode('raw_unicode_escape').decode())
            return ret_new
        except Exception as e:
            print(e.__str__())
            return ret.text


