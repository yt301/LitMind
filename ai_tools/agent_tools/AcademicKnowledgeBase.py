from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
load_dotenv()  # OpenAIEmbeddings() 使用 OpenAI 的文本嵌入模型，需通过 API Key 验证。

# 知识库（采用Chroma向量数据库）
class AcademicKnowledgeBase:
    def __init__(self, knowledge_dir="knowledge_base/academic"):
        self.embeddings = OpenAIEmbeddings()  # 初始化文本嵌入模型，用于将文本转换为向量表示。
        self.vectorstore = None  # 初始化一个占位变量，稍后用于存储 Chroma 向量数据库实例。
        self.knowledge_dir = knowledge_dir  # 指定原始学术文档（如 PDF）的存储目录路径。
        self.persist_dir = "vectorstore/chroma_academic"  # 指定 Chroma 向量数据库的持久化存储目录。
        self._initialize_knowledge_base()  # 在初始化时自动调用，完成知识库的加载或创建。

    def _initialize_knowledge_base(self):
        # Chroma会自动检查持久化目录，无需手动判断
        if os.path.exists(self.persist_dir) and os.listdir(self.persist_dir):
            # 从磁盘加载现有向量库
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        else:
            self._create_knowledge_base()

    def _create_knowledge_base(self):
        # 加载学术文档
        loader = DirectoryLoader(
            self.knowledge_dir,
            glob="**/*.pdf"  # 支持PDF文件
        )
        documents = loader.load()

        # 分割文本
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)

        # 创建Chroma向量存储
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        # Chroma会自动持久化，无需手动保存

    def retrieve_relevant_info(self, query: str, k: int = 3):
        """检索与查询相关的学术信息"""
        if not self.vectorstore:
            return []

        # Chroma的相似度搜索
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def add_document(self, file_path: str):
        """动态添加单个文档到知识库"""
        from langchain.document_loaders import PyPDFLoader

        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

        # 添加到现有集合
        self.vectorstore.add_documents(pages)
        print(f"已成功添加文档: {os.path.basename(file_path)}")

