import os,json
from typing import Sequence
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
#message_to_dict:单个消息对象(BaseMessage类实例)->字典
#messages_fron_dict:[字典，字典]->[消息，消息]
class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self,session_id,storage_path):
        self.session_id = session_id #会话id
        self.storage_path = storage_path #不同会话id存储文件的文件夹路径
        self.file_path=os.path.join(self.storage_path,self.session_id)#完整文件路径
        #确保文件夹存在
        os.makedirs(os.path.dirname(self.file_path),exist_ok=True)
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages=list(self.messages)#已有消息列表
        all_messages.extend(messages)#新的和已有的融合成一个list
        #数据同步写入本地文件
        #类对象写入会变成二进制可以将消息转化为字典，以json字符串写入文件
        new_messages=[]
        for message in all_messages:
            d= message_to_dict(message)
            new_messages.append(d)
        #数据写入文件
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(new_messages,f)
    @property#装饰器将messages方法变成成员属性
    def messages(self)->list[BaseMessage]:
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                 messages_data=json.load(f)
                 return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
    def clear(self) -> None:
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump([],f)




model =ChatTongyi(model="qwen3-max")
# prompt = PromptTemplate.from_template(
#     "你需要根据历史会话回答用户的问题。对话历史{chat_history}，用户提问:{input}，请回答"
# )
prompt=ChatPromptTemplate.from_messages(
    [
        ("system","你需要根据会话历史回应用户消息。对话历史:"),
        MessagesPlaceholder("chat_history"),
        ("human","请回答如下问题{input}")
    ]
)
str_parser = StrOutputParser()
def print_prompt(full_prompt):
    print("="*20,full_prompt.to_string(),"="*20)
    return full_prompt
base_chain=prompt|print_prompt|model|str_parser

#通过回话id获得InMemoryChatMessageHistory对象
def get_history(session_id):
   return FileChatMessageHistory(session_id,"./chat_history")
#创建一个新的链，对原有链增强功能:自动附加历史消息
conversation_chain=RunnableWithMessageHistory(
    base_chain,#被增强的原有链
    get_history,#通过回话id获得InMemoryChatMessageHistory对象
    input_messages_key="input", #用户输入在模板里的占位符
    history_messages_key="chat_history"
)
# if __name__=='__main__':
#     #固定格式添加langchain配置，为当前程序配置所属id
#     session_config={
#         "configurable":{
#             "session_id":"user_001"
#         }
#     }
#     # res=conversation_chain.invoke({"input":"小明有2个猫"},session_config)
#     # print("第一次执行",res)
#     # res=conversation_chain.invoke({"input":"小明有1个狗",},session_config)
#     # print("第二次执行",res)
#     res=conversation_chain.invoke({"input":"小明有几只宠物"},session_config)
#     print("第三次执行",res)
