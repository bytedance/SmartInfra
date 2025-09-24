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
