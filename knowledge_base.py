"""
知识库
"""
import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
def check_md5(md5_str:str):
    """检查传入的md5字符串是否已经被处理过"""
    if not os.path.exists(config.md5_path):
        open(config.md5_path,'w',encoding="utf-8").close()
        return False#未处理过的md5 return False
    else:
        for line in open(config.md5_path,'r',encoding='utf-8').readlines():
            line=line.strip()#处理字符串空格与回车
            if line == md5_str:
                return True  #已经处理过

        return False


def save_md5(md5_str:str):
    """将传入的md5字符串记录到文件保存"""
    with open(config.md5_path,'a',encoding="utf-8") as f:
        f.write(md5_str+'\n')


def get_string_md5(input_str:str,encoding='utf-8'):
    """将传入的字符串转换为md5字符串"""
    #字符串转换为bytes字节数组
    str_bytes=input_str.encode(encoding=encoding)
    #创建md5对象
    md5_obj=hashlib.md5()
    #更新内容，传入要转换的字节数组
    md5_obj.update(str_bytes)
    #得到md5 16进制字符串
    md5_hex=md5_obj.hexdigest()
    return md5_hex

class KnowledgeBaseService(object):
    def __init__(self):
        os.makedirs(config.persist_directory,exist_ok=True)#确保文件夹存着
        self.chroma=Chroma(
            collection_name=config.collection_name ,#数据库表名
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory,
        )#向量存储实例 Chroma向量库对象
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,#分割后文本段最大长度
            chunk_overlap=config.chunk_overlap,#允许的字符重叠数
            separators=config.separators,#自然段落划分符号
            length_function=len #  Python自带len函数做长度统计依据

        )#文本分割器

    def upload_by_str(self,data:str,filename):
        """传入数据向量化存入向量数据库"""
        #传入字符串md5值
        md5_hex=get_string_md5(data)

        if check_md5(md5_hex):
            return "内容已经存在于知识库"

        if len(data)>config.max_split_char_number:
            knowledge_chunks:list[str]=self.spliter.split_text(data)
        else:
            knowledge_chunks=[data]
        metadata={
            "source":filename,
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"Aliya"
        }
        #内容加载到向量库
        self.chroma.add_texts(
            #iterable:list/tuple
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks],
        )

        save_md5(md5_hex)

        return "内容成功载入向量库"




