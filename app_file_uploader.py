import time

import streamlit as st
from knowledge_base import KnowledgeBaseService
#添加网页标题
#Web页面元素发生变化，代码重新执行一遍，可能会导致状态丢失
st.title("知识库服务更新")

uploader_file=st.file_uploader(
    "请上传文件",
    type=['txt','png','jpg','jpeg','gif','bmp',"doc","docx"],
    accept_multiple_files=False,
)

#session_state是一个字典对象，可以在不同的函数之间共享数据，保持状态
if "service" not in st.session_state:
    st.session_state["service"]=KnowledgeBaseService()
if uploader_file is not None:
    #提取文件信息
    file_name=uploader_file.name
    file_type=uploader_file.type
    file_size=uploader_file.size/1024


    st.subheader(f"文件名:{file_name}")
    st.write(f"格式:{file_type}|大小:{file_size:.2f}KB")
    #获取文件内容
    text=uploader_file.getvalue().decode("utf-8")
with st.spinner("载入知识库中...."):#转圈动画
    time.sleep(1)
    result=st.session_state["service"].upload_by_str(text,file_name)
    st.write(result)