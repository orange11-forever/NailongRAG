import time
from rag import RagService
import streamlit as st
import config_data as config
#标题
st.title("奶龙保护组织智能小助手")
st.divider()#分隔符

if"message"not in st.session_state:
    st.session_state["message"]=[{"role":"assistant","content":"我是奶龙保护组织的小助手，有什么问题就来问我吧😊"}]
if"rag"not in st.session_state:
    st.session_state["rag"]=RagService()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])
#用户输入框
prompt=st.chat_input()
if prompt:
    #展示用户输入
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})
    #展示AI回复
    ai_res_list=[]
    with st.spinner("AI思考中"):
     res_stream=st.session_state["rag"].chain.stream({"input":prompt},config.session_config)
     def capture(generator,cache_list):
         for chunk in generator:
             cache_list.append(chunk)
             yield  chunk
     st.chat_message("assistant").write_stream(capture(res_stream,ai_res_list))
     st.session_state["message"].append({"role":"assistant","content":"".join(ai_res_list)})
