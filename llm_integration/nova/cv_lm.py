from .auth import get_auth_bearer, nova_llm_server
import requests


## https://platform.xxx.cn/#/doc?path=/xxx/GetStarted/APIList.md


class CVModels(object):

    def cv_models(model_type, **kwargs):
        # 查询模型清单
        """
        请求参数（Request Parameters）
        名称	类型	必须	默认值	可选值	描述
        type	string	否	all	-	模型类型，枚举值
        全部：all
        2d分类：2d_classify
        2d检测：2d_detect
        2d检测+分类：2d_detect_classify
        2d分割：2d_segment
        2d检测+分割：2d_detect_segment
        3d检测：3d_detect
        """
        return requests.get(nova_llm_server + '/v1/cv/models', data={"type": model_type}, headers=get_auth_bearer())
    
    def cv_model_detail(model_id):
        # 通过模型ID获取模型详细信息
        return requests.get(nova_llm_server + f'/v1/cv/models/{model_id}', headers=get_auth_bearer())
    

class CVAutoAnnotation(object):

    def cv_classify_2d(file_binary, **kwargs):
        """
        对2D图像中的物体进行类型识别
        """
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        model	string	是	-	-	模型ID，模型清单中类型为2d_classify的模型
        file	file	是	-	-	图片的二进制数据，支持jpg、png、jpeg格式，大小不超过7M
        """
        return requests.post(nova_llm_server + f'/v1/cv/2d_classify', json=kwargs, files=file_binary, headers=get_auth_bearer())
    
    def cv_detect_2d(file_binary, **kwargs):
        """
        检测2D图片中的物体
        """
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        model	string	是	-	-	模型ID，模型清单中类型为2d_detect的模型
        file	file	是	-	-	图片的二进制数据，支持jpg、png、jpeg格式，大小不超过7M
        """
        return requests.post(nova_llm_server + f'/v1/cv/2d_detect', json=kwargs, files=file_binary, headers=get_auth_bearer())
    
    def cv_detect_classify_2d(file_binary, **kwargs):
        """
        检测2D图片中的物体，并进行类型识别
        """
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        model	string	是	-	-	模型ID，模型清单中类型为2d_detect_classify的模型
        file	file	是	-	-	图片的二进制数据，支持jpg、png、jpeg格式，大小不超过7M
        """
        return requests.post(nova_llm_server + f'/v1/cv/2d_detect_classify', json=kwargs, files=file_binary, headers=get_auth_bearer())
    

    def cv_segment_2d(file_binary, **kwargs):
        """
        对2D图片进行全景分割
        """
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        model	string	是	-	-	模型ID，模型清单中类型为2d_segment的模型
        file	file	是	-	-	图片的二进制数据，支持jpg、png、jpeg格式，大小不超过7M
        """
        return requests.post(nova_llm_server + f'/v1/cv/2d_segment', json=kwargs, files=file_binary, headers=get_auth_bearer())
    
    def cv_detect_segment_2d(file_binary, **kwargs):
        """
        对2D图片进行目标检测和实例分割
        """
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        model	string	是	-	-	模型ID，模型清单中类型为2d_detect_segment的模型
        file	file	是	-	-	图片的二进制数据，支持jpg、png、jpeg格式，大小不超过7M
        """
        return requests.post(nova_llm_server + f'/v1/cv/2d_detect_segment', json=kwargs, files=file_binary, headers=get_auth_bearer())
    
    def cv_detect_3d(file_binary, **kwargs):
        """
        对2D图片进行目标检测和实例分割
        """
        """
        请求体（Request Body）
        名称	类型	必须	默认值	可选值	描述
        model	string	是	-	-	模型ID，模型清单中类型为3d_detect的模型
        file	file	是	-	-	图片的二进制数据，支持jpg、png、jpeg格式，大小不超过7M
        """
        return requests.post(nova_llm_server + f'/v1/cv/3d_detect', json=kwargs, files=file_binary, headers=get_auth_bearer())
    

class CV(CVModels, CVAutoAnnotation):
    pass