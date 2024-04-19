from .auth import get_auth_bearer, nova_llm_server
import requests


## https://platform.xxx.cn/#/doc?path=/file/GetStarted/APIList.md


class FileManager(object):

    def files_new(file, **kwargs):
        # 文件管理模块方便各个模块调用，通过创建并上传文件（二进制上传），实现文件的复用
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        description	string	否	-	-	文件描述
        长度不超过256字符
        scheme	string	是	-	枚举值，类型如下：
        1.微调数据集文件：FINE_TUNE_1
        2.知识库Json文件：KNOWLEDGE_BASE_1
        3.知识库其余格式文件：KNOWLEDGE_BASE_2	文件格式
        file	file	是	-	-	文件的二进制数据
        """
        """
        FINE_TUNE_1 当前版本（Beta）格式限制：

        文件大小不能超过200M
        文件格式为 .json
        编码格式为 UTF-8
        内容需遵循以下格式
        [
        {
            "instruction": "", //指令
            "input": "", //输入
            "output": "" //输出
        },
        {
            "instruction": "", //指令
            "input": "", //输入
            "output": "" //输出
        }
        ]

        KNOWLEDGE_BASE_1 当前版本（Beta）格式限制：

        文件大小不能超过20M
        文件格式为 .json
        编码格式为 UTF-8
        内容需遵循以下格式
        {
            "qa_lst": [ //问答对知识
                {
                    "std_q": "xxx", //问题描述
                    "simi_qs": ["xxx", "xxx"], //相似问题描述
                    "answer": "xxx" //答案描述
                },
                {
                    "std_q": "xxx", //问题描述
                    "simi_qs": ["xxx", "xxx"], //相似问题描述
                    "answer": "xxx" //答案描述
                }
            ],
            "text_lst": [ //文本知识，纯文本数据（当前版本（Beta），建议每条数据尽量是一个独立的语义主题，便于提升检索效率和效果）
                "xxx",
                "xxx"
            ]
        }
        其中，text_lst 每条数据不能超过5000个字符


        KNOWLEDGE_BASE_2 当前版本（Beta）格式限制：

        文件格式目前仅支持 .pdf
        PDF文件页数不能超过50页，PDF文件大小不能超过20M
        在上传文件成功且通过格式校验后，您可使用此文件创建知识库。
        在创建知识库时，系统会自动识别转换文件内容。目前支持文本、表格内容的识别转换。
        """
        return requests.post(nova_llm_server + '/v1/files', json=kwargs,  headers=get_auth_bearer())
    
    def files_list(**kwargs):
        # 查询文件列表
        return requests.get(nova_llm_server + '/v1/files', headers=get_auth_bearer())
    
    def files_detail(file_id, **kwargs):
        # 查询文件详情
        return requests.get(nova_llm_server + f'/v1/files/{file_id}', headers=get_auth_bearer())
    
    def files_content(file_id, **kwargs):
        # 查询文件详情
        return requests.get(nova_llm_server + f'/v1/files/{file_id}/content', headers=get_auth_bearer())
    
    def files_detail(file_id, **kwargs):
        # 删除文件
        return requests.delete(nova_llm_server + f'/v1/files/{file_id}', headers=get_auth_bearer())
    
