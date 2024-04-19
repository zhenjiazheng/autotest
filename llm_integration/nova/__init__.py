
from .cv_lm import CV
from .llm import LLM
from .file_manage import FileManager

class CVLM_LLM_FLM(CV, LLM, FileManager):
    pass


__all__ = ['CVLM_LLM_FLM']

