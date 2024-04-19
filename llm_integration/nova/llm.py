from .auth import get_auth_bearer, nova_llm_server
import requests


## https://platform.xxx.cn/#/doc?path=/chat/GetStarted/APIList.md


class Models(object):

    def models():
        # 查询模型清单（基模型、用户的微调模型、以及Embedding模型）
        return requests.get(nova_llm_server + '/v1/llm/models', headers=get_auth_bearer())
    
    def model_detail(model_id):
        # 通过模型ID获取模型详细信息
        return requests.get(nova_llm_server + f'/v1/llm/models/{model_id}', headers=get_auth_bearer())
    
    def model_delete(model_id):
        # 删除微调模型
        return requests.delete(nova_llm_server + f'/v1/llm/models/{model_id}', headers=get_auth_bearer())


class Completions(object):

    def completions(**kwargs):
        # 基于给定的聊天对话信息，创建模型响应
        """
        名称	                类型	    必须	 默认值	    可选值	                    描述
        model	                string	    是	    -	     参考查询模型列表	           模型ID
        n	                    int	        否	    1	     [1,4]	                    生成回复数量，响应参数中的index即为回复序号（在使用某些模型时不支持传入该参数，详情请参考模型清单）
        know_ids	            string[]	否	    -	     参考查询知识库列表	           检索的知识库列表（在使用某些模型时不支持传入该参数，参考模型清单）
        max_new_tokens	        int	        否	    1024	 [1,2048]	                期望模型生成的最大token数（不同模型支持的上下文长度不同，因此最大值也不同，参考模型清单）
        messages	            object[]	是	    -	      -	                        输入给模型的对话上下文，数组中的每个对象为聊天的上下文信息
        repetition_penalty	    float	    否	    1.05	  (0,2]	                    重复惩罚系数，1代表不惩罚，大于1倾向于生成不重复token，小于1倾向于生成重复token，推荐使用范围为[1,1.2]
        stream	                boolean	    否	    false	  开启：true关闭：false	      是否使用流式传输，如果开启，数据将按照data-only SSE（server-sent events）返回中间结果，并以 data: [DONE] 结束
        temperature	            float	    否	    0.8	      (0,2]	                    温度采样参数，大于1的值倾向于生成更加多样的回复，小于1倾向于生成更加稳定的回复
        top_p	                float	    否	    0.7	      (0,1)	                    核采样参数，解码生成token时，在概率和大于等于top_p的最小token集合中进行采样
        user	                string	    否	    -	        -	                    外部用户ID，应用开发者可将应用系统用户ID传入，方便追踪
        knowledge_config	    object	    否	    -	        -	                    知识配置（在使用某些模型时不支持传入该参数，参考模型清单）
        """
        return requests.post(nova_llm_server + f'/v1/llm/chat-completions', json=kwargs, headers=get_auth_bearer())


class Chat(object):

    def chat_session(**kwargs):
        # 创建有历史的会话
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        system_prompt	object[]	否	-	-	会话的系统提示词

        其中 system_prompt 部分参数如下：
        名称	类型	必须	默认值	可选值	                            描述
        role	string	是	    -	  枚举值 user, assistant,system	    消息作者的角色，枚举值
        content	string	是	    -	    -	                           消息的内容
        """
        return requests.post(nova_llm_server + f'/v1/llm/chat/sessions', json=kwargs, headers=get_auth_bearer())
    
    def chat_conversations(**kwargs):
        # 基于某个已经创建的会话，生成对话
        # 请注意，此接口会基于模型的上下文长度限制，携带会话历史进行对话生成（例如，nova-ptc-xl-v1目前限制的上下文长度为2k，则会携带不超过2k的会话历史进行对话，如果最新的一条会话加进会话历史之后总长度超出2k，会按照会话时间从早到晚开始遗忘）。

        """
        名称	类型	必须	默认值	可选值	描述
        action	string	否	next	正常进行下一轮对话：next
        在已有的某一轮对话里重新生成：regeneration	本次对话的行为
        content	string	是	-	-	消息的内容
        model	string	是	-	参考查询模型列表	模型ID
        session_id	string	是	-	-	此次对话的会话ID，通过创建会话接口获得
        stream	boolean	否	false	开启：true
        关闭：false	是否使用流式传输，如果开启，数据将按照data-only SSE（server-sent events）返回中间结果，并以 data: [DONE] 结束
        know_ids	string[]	否	-	参考查询知识库列表	检索的知识库列表
        knowledge_config	object	否	-	-	知识配置

        knowledge_config 部分参数如下：
        名称	类型	必须	默认值	可选值	描述
        control_level	string	否	normal	枚举值
        normal
        high	对知识库的控制力度
        normal：模型正常参考知识库内容进行回答
        high：模型强参考知识库内容进行回答（若您期望模型回答尽可能依赖知识库，不自由发散，推荐使用此值）
        knowledge_base_result	boolean	否	false	true
        false	是否返回本次请求查询的知识库检索结果
        true：返回
        false：不返回
        knowledge_base_configs	object[]	否	-	-	知识库配置

        knowledge_base_configs 部分参数如下：
        名称	类型	必须	默认值	可选值	描述
        know_id	string	是	-	本次请求检索的知识库ID（konw_ids中的知识库ID）	需要实现配置的知识库ID
        faq_threshold	float	是	-	(0,1)	知识库中的qa_lst精准命中程度的阈值配置，越高代表对该知识库中问答对的检索结果相似度要求越严格
        """
        return requests.post(nova_llm_server + f'/v1/llm/chat-conversations', json=kwargs, headers=get_auth_bearer())
    

# Sub Fine-Tune
class FineTuneDataSet(object):

    def datasets_new(**kwargs):
        # 创建数据集，用于模型微调
        """
        名称	类型	必须	默认值	可选值	描述
        description	string	否	-	-	    数据集描述 长度不超过256字符
        files	string[]	否	-	-	    文件管理模块对应的文件ID（注意，文件必须是微调数据集支持的格式）
                                            如果在这里传了文件列表，则无需再调用“给数据集添加文件”接口
        """
        return requests.post(nova_llm_server + f"/v1/llm/fine-tune/datasets", json=kwargs, headers=get_auth_bearer())
    

    def datasets_update(dateset_id, **kwargs):
        # 更新已有数据集
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        dateset_id	string	是	-	-	数据集ID

        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        description	string	否	-	-	    数据集描述 长度不超过256字符
        files	string[]	否	-	-	    文件管理模块对应的文件ID（注意，文件必须是微调数据集支持的格式）
                                            如果在这里传了文件列表，则无需再调用“给数据集添加文件”接口
        """
        return requests.post(nova_llm_server + f"/v1/llm/fine-tune/datasets/{dateset_id}", json=kwargs, headers=get_auth_bearer())
    

    def datasets_files_add(dateset_id, files):
        # 给数据集添加文件
        """
        请注意，此接口并非直接上传文件内容，而是会返回对象存储的文件上传地址，您需要在拿到上传地址后，再次调用对象存储的 PUT 方法上传真实文件。
        此接口将于2023年12月31日下线，推荐使用文件管理模块进行微调数据集文件管理。

        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        dateset_id	string	是	-	-	数据集ID

        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        description	string	否	-	-	    数据集描述 长度不超过256字符

        获取URL之后，可通过标准 S3 对象存储的 PUT 方法上传文件，示例如下：

        curl --request PUT '$url' \
        -H 'Content-Type: application/json' \
        -d @/path/to/your/json/file.json
        """
        ret =  requests.post(nova_llm_server + f"/v1/llm/fine-tune/datasets/{dateset_id}/files", headers=get_auth_bearer())
        put_url = ret.json().get('url')
        requests.put(url=put_url, files=files)

    
    def datasets_files_downlaod(dateset_id, file_id):
        # 下载数据集中的文件 
        # 请注意，此接口并非直接下载文件内容，而是会返回一个重定向的下载地址。
        # 此接口将于2023年12月31日下线，推荐使用文件管理模块进行微调数据集文件管理。
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        dateset_id	string	是	-	-	数据集ID
        file_id	string[]	否	-	-	    文件id
        """
        return requests.get(nova_llm_server + f"/v1/llm/fine-tune/datasets/{dateset_id}/files/{file_id}", headers=get_auth_bearer())
    
    def datasets_list():
        # 查询当前账户下存在的数据集列表 
        return requests.get(nova_llm_server + f"/v1/llm/fine-tune/datasets", headers=get_auth_bearer())
    

    def datasets_detail(dateset_id):
        # 通过数据集ID获取数据集详细信息 
        """     
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        dateset_id	string	是	-	-	数据集ID
        """

        return requests.get(nova_llm_server + f"/v1/llm/fine-tune/datasets/{dateset_id}", headers=get_auth_bearer())
    
    def datasets_delete(dateset_id):
        # 删除数据集 
        """     
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        dateset_id	string	是	-	-	数据集ID
        """

        return requests.delete(nova_llm_server + f"/v1/llm/fine-tune/datasets/{dateset_id}", headers=get_auth_bearer())


# Sub Fine-Tune
class FineTuneTask(object):
    def fine_tune_task_new(**kwargs):
        # 创建微调任务 
        """     
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        training_file	string	是	-	-	微调使用的数据集ID
        model	string	是	-	-	微调使用的基模型ID
        suffix	string	是	-	-	微调后的模型名称后缀
        模型名称命名规则为 {model}:{suffix}
        suffix 限制为：以小写英文字母开头，以小写英文字母/数字结尾，中间部分支持小写英文字母/数字/中划线，总长度不超过53个字符
        hyperparams	object	否	-	-	训练超参配置。不同模型 x 不同微调方法，对应的结构不同，具体见下方说明

        当【微调模型】为nova-ptc-xs-v1，【微调方法】为lora 时，hyperparams部分参数如下：
        名称	类型	必须	默认值	可选值	描述
        training	object	否	-	-	训练超参

        其中， training 部分参数如下：
        名称	类型	必须	默认值	可选值	描述
        max_steps	int	否	20000	-	训练的最大迭代次数
        method	string	否	lora	lora	训练方法，枚举值，当前仅支持 lora
        lr_scheduler_type	string	否	cosine	cosine	学习率调整策略，枚举值，当前仅支持 consine
        learning_rate	float	否	0.0001	-	学习率
        warmup_ratio	float	否	0.03	-	warmup迭代比例，指定从0到峰值学习率（通常就是 learning_rate指定的）的线性预热所使用的训练步占max_steps的比例
        weight_decay	float	否	0	-	正则化权重衰减系数
        save_steps	int	否	50000	-	权重保存迭代间隔
        modules_to_save	string	否	word_embeddings	word_embeddings	需要训练与保存的模块，枚举值，当前仅支持 word_embeddings
        lora	object	否	-	-	微调方法为 lora 时，对应的参数配置

        其中， lora 部分参数如下：
        名称	类型	必须	默认值	可选值	描述
        lora_rank	int	否	8	-	lora层的秩
        lora_dropout	float	否	0.05	-	lora层的dropout概率
        lora_alpha	int	否	32	-	lora层的正则化强度
        """
        """
        {
            "job": {
                "id": "string", 
                "object": "FINETUNE",
                "model": "string", 
                "fine_tuned_model": "string",
                "training_files": "string", 
                "status": "string", 
                "hyperparams": {
                "training": {
                    "max_steps": 20000,
                    "method": "lora",
                    "lr_scheduler_type": "cosine",
                    "learning_rate": 0.0001,
                    "warmup_ratio": 0.03,
                    "weight_decay": 0,
                    "save_steps": 50000,
                    "modules_to_save": "word_embeddings",
                    "lora":{
                        "lora_rank": 8,
                        "lora_dropout": 0.05,
                        "lora_alpha": 32
                    }
                }
                },
                "created_at": "2023-06-28T17:23:01.243566533Z",
                "updated_at": "2023-06-28T17:23:01.243566533Z"
            }
        }
        """

        return requests.post(nova_llm_server + f"/v1/llm/fine-tunes", json=kwargs, headers=get_auth_bearer())

    def fine_tune_task_list(**kwargs):
        # 查询微调任务列表 

        return requests.get(nova_llm_server + f"/v1/llm/fine-tunes", json=kwargs, headers=get_auth_bearer())


    def fine_tune_task_detail(fine_tune_id, **kwargs):
        # 通过任务ID查询微调任务详情 
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        fine_tune_id	string	是	-	-	微调任务ID
        """
        return requests.get(nova_llm_server + f"/v1/llm/fine-tunes/{fine_tune_id}", json=kwargs, headers=get_auth_bearer())

    def fine_tune_task_cancel(fine_tune_id, **kwargs):
        # 通过任务ID查询微调任务详情 
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        fine_tune_id	string	是	-	-	微调任务ID
        """
        return requests.post(nova_llm_server + f"/v1/llm/fine-tunes/{fine_tune_id}/cancel", json=kwargs, headers=get_auth_bearer())

    def fine_tune_task_delete(fine_tune_id, **kwargs):
        # 通过任务ID查询微调任务详情 
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        fine_tune_id	string	是	-	-	微调任务ID
        """
        return requests.delete(nova_llm_server + f"/v1/llm/fine-tunes/{fine_tune_id}", json=kwargs, headers=get_auth_bearer())


# Sub Fine-Tune
class FineTuneDeploy(object):

    def fine_tune_deploy_task_new(**kwargs):
        # 创建部署任务 
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        model	string	是	-	-	微调模型ID，参考查询模型列表
        config	object	是	-	-	部署任务配置
        config 部分参数如下：
        名称	类型	必须	默认值	可选值	描述
        run_time	int	是	60	[1,60]	指定运行时间, 单位为分钟
        sample:
        curl --request POST 'https://api.xxx.cn/v1/llm/fine-tune/servings' \
        -H 'Content-Type: application/json' \
        -H 'Authorization: Bearer $API_TOKEN' \
        -d '{
                "model": "string",
                "config": {
                    "run_time": 0
                }
        }'
        """
        return requests.post(nova_llm_server + f"/v1/llm/fine-tunes/servings", json=kwargs, headers=get_auth_bearer())

    def fine_tune_deploy_task_list(**kwargs):
        # 查询部署任务列表 
        return requests.get(nova_llm_server + f"/v1/llm/fine-tunes/servings", json=kwargs, headers=get_auth_bearer())


    def fine_tune_deploy_task_detail(serving_id, **kwargs):
        # 通过ID查询部署任务详情 
        return requests.get(nova_llm_server + f"/v1/llm/fine-tunes/servings/{serving_id}", json=kwargs, headers=get_auth_bearer())

    def fine_tune_deploy_task_cancel(serving_id, **kwargs):
        # 取消部署任务 
        return requests.post(nova_llm_server + f"/v1/llm/fine-tunes/servings/{serving_id}/cancel", json=kwargs, headers=get_auth_bearer())


    def fine_tune_deploy_task_relaunch(serving_id, **kwargs):
        # 重启部署任务 
        return requests.post(nova_llm_server + f"/v1/llm/fine-tunes/servings/{serving_id}/relaunch", json=kwargs, headers=get_auth_bearer())

    def fine_tune_deploy_task_delete(serving_id, **kwargs):
        # 删除部署任务 
        return requests.delete(nova_llm_server + f"/v1/llm/fine-tunes/servings/{serving_id}", json=kwargs, headers=get_auth_bearer())


class FineTune(FineTuneDataSet, FineTuneTask, FineTuneDeploy):
    pass


class KnowledgeBase(object):

    def knowledge_bases_new(**kwargs):
        # 创建知识库 
        # 请注意，当前版本（Beta），1个账号下最多只允许创建1个知识库，后续会逐步开放限制。
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        description	string	否	-	-	知识库描述
        长度不超过256字符
        files	string[]	否	-	-	文件管理模块对应的文件ID（注意，文件必须是知识库支持的格式）
        如果在这里传了文件列表，则无需再调用“给知识库添加文件”接口
        """
        """
        curl --request POST 'https://api.xxx.cn/v1/llm/knowledge-bases' \
            -H 'Content-Type: application/json' \
            -H 'Authorization: Bearer $API_TOKEN' \
            -d '{
                    "description": "string", 
                    "files":[
                    "string"
                    ]
            }'
        """
        return requests.post(nova_llm_server + f"/v1/llm/knowledge-bases", json=kwargs, headers=get_auth_bearer())

    def knowledge_bases_update(knowledge_base_id, **kwargs):
        # 更新知识库 
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        knowledge_base_id	string	是	-	-	知识库ID

        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        description	string	否	-	-	知识库描述
        长度不超过256字符
        files	string[]	否	-	-	文件管理模块对应的文件ID（注意，文件必须是知识库支持的格式）
        如果在这里传了文件列表，则无需再调用“给知识库添加文件”接口
        """
        """
        curl --request POST 'https://api.xxx.cn/v1/llm/knowledge-bases' \
            -H 'Content-Type: application/json' \
            -H 'Authorization: Bearer $API_TOKEN' \
            -d '{
                    "description": "string", 
                    "files":[
                    "string"
                    ]
            }'
        """
        return requests.put(nova_llm_server + f"/v1/llm/knowledge-bases/{knowledge_base_id}", json=kwargs, headers=get_auth_bearer())

    def knowledge_bases_files_add(knowledge_base_id, files, **kwargs):
        # 给知识库添加文件

        # 请注意，此接口并非直接上传文件内容，而是会返回对象存储的文件上传地址，您需要在拿到上传地址后，再次调用对象存储的 PUT 方法上传真实文件。
        # 此接口将于2023年12月31日下线，推荐使用文件管理模块进行知识库文件管理。 
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        knowledge_base_id	string	是	-	-	知识库ID

        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        description	string	否	-	-	知识库描述 长度不超过256字符
        """
        """
        curl --request POST 'https://api.xxx.cn/v1/llm/knowledge-bases/{knowledge_base_id}/files' \
            -H 'Content-Type: application/json' \
            -H 'Authorization: Bearer $API_TOKEN' \
            -d '{
                    "description": "string"
                    ]
            }'
        """
        """
        请注意，当前版本（Beta）限制

        对中文支持较好，其他语言的支持后续会逐步完善
        1个知识库只能上传1个文件
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
        """
        ret = requests.post(nova_llm_server + f"/v1/llm/knowledge-bases/{knowledge_base_id}/files", json=kwargs, headers=get_auth_bearer())
        url = ret.json().get('url')
        requests.put(url=url, files=files)

    def knowledge_bases_files_download(knowledge_base_id, file_id, **kwargs):
        # 下载知识库中的文件 
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        knowledge_base_id	string	是	-	-	知识库ID
        file_id	string	是	-	-	文件ID
        """
        return requests.get(nova_llm_server + f"/v1/llm/knowledge-bases/{knowledge_base_id}/files/{file_id}", json=kwargs, headers=get_auth_bearer())

    def knowledge_bases_files_delete(knowledge_base_id, file_id, **kwargs):
        # 删除知识库中的某一个文件 
        """
        请求参数（Path Parameters）
        名称	类型	必须	默认值	可选值	描述
        knowledge_base_id	string	是	-	-	知识库ID
        file_id	string	是	-	-	文件ID
        """
        return requests.delete(nova_llm_server + f"/v1/llm/knowledge-bases/{knowledge_base_id}/files/{file_id}", json=kwargs, headers=get_auth_bearer())

    def knowledge_bases_list(**kwargs):
        # 查询当前账户下存在的知识库列表 
        return requests.delete(nova_llm_server + f"/v1/llm/knowledge-bases", json=kwargs, headers=get_auth_bearer())

    def knowledge_bases_detail(knowledge_base_id, **kwargs):
        # 查询知识库详情 
        return requests.get(nova_llm_server + f"/v1/llm/knowledge-bases/{knowledge_base_id}", json=kwargs, headers=get_auth_bearer())

    def knowledge_bases_detail(knowledge_base_id, **kwargs):
        # 删除知识库 
        return requests.delete(nova_llm_server + f"/v1/llm/knowledge-bases/{knowledge_base_id}", json=kwargs, headers=get_auth_bearer())


class Embeddings(object):

    def embeddings(**kwargs):
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        model	string	是	-	-	Embedding模型ID，参考查询模型列表
        input	string[]	是	-	-	input中最多支持32条，每条长度不能超过512个token
        """
        """
        curl --request POST 'https://api.xxx.cn/v1/llm/embeddings' \
            -H 'Content-Type: application/json' \
            -H 'Authorization: Bearer $API_TOKEN' \
            -d '{
                    "model": "string",
                    "input": [
                    "string"
                    ]
            }'
        """
        return requests.post(nova_llm_server + f"/v1/llm/embeddings", json=kwargs, headers=get_auth_bearer())


class LLM(Models, Completions, Chat, FineTune, KnowledgeBase, Embeddings):
    pass
