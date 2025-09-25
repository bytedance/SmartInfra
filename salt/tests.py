from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader

# 1. 加载文档
loader = TextLoader("dc.txt", encoding="utf-8")
documents = loader.load()

# 2. 文本切片
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# 3. 向量化
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. 建立向量数据库
db = FAISS.from_documents(chunks, embedding)

# 5. 保存数据库
db.save_local("vectorstore")

---
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import openai

# 创建客户端
client = openai.Client(
    base_url="http://127.0.0.1:30000/v1",  # 对应你的 sgllang 服务地址
    api_key="EMPTY"  # 占位，sglang 不校验
)

# 初始化对话历史
conversation = [
    {"role": "system", "content": "You are a helpful AI assistant."},
]

# 加载向量库
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local("vectorstore", embedding, allow_dangerous_deserialization=True)

# 多轮对话循环
while True:
    user_input = input("User: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        break

    # 1. 检索相关内容
    results = db.similarity_search(user_input, k=3)
    context_texts = "\n".join([doc.page_content for doc in results])

    # 2. 构造 prompt
    if not user_input:
        prompt = user_input
    else:
        prompt = f"""以下是���关资料片段：
        {context_texts}

        根据上述资料，回答以下问题：
        {user_input}
        """
    # 添加用户输入到消息列表
    conversation.append({"role": "user", "content": prompt})

    # 发起请求
    response = client.chat.completions.create(
        model="default",
        messages=conversation,
        temperature=1.0,
        max_tokens=512,
    )

    # 取出回复内容
    assistant_reply = response.choices[0].message.content.strip()
    print(f"Assistant: {assistant_reply}")

    # 添加 AI 回复到对话历史
    conversation.append({"role": "assistant", "content": assistant_reply})

---
LInux下策略路由配置：

期望：
实现网卡流量的分离，原进原出
有托底路由设置。当从本机主动访问外部时可联通
因为是容器环境，存在多个网桥，每个网桥又关联一个物理网卡，实现互联互通

原理：
iface bond4 inet static
    address 10.9.3.1
    netmask 255.255.255.224
    gateway 10.9.3.9	#托底路由。非匹配路由策略流量
    post-up ip rule add from 10.9.13.8/27 table 101    #根据来源ip分配流量到指定路由表中
    post-up ip rule add from 172.17.0.0/16 table 101       #根据来源ip分配流量到指定路由表中
    post-up ip route add default via 10.9.83.9 dev bond4 table 101    #在指定路由表中使用缺省路由

流量路径：（容器流量是首先路由再nat）
进流量所经过端点： 客户端 -路由- 服务器ip -nat- 容器         #路由是由广域网提供。nat是在桥接模式下由容器实现
回程流量： 容器 -nat- 服务器ip -路由- 客户端               #选择从那个路由表回，客户端看到的ip就是哪个服务器ip。但是在本机上看到是容器ip地址


