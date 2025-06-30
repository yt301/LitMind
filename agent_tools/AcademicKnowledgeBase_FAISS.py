from langchain_community.vectorstores import FAISS  # 替换Chroma为FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from config import KNOWLEDGE_BASE_PATH, VECTOR_STORE_PATH
import os
from dotenv import load_dotenv

load_dotenv()  # OpenAIEmbeddings() 使用 OpenAI 的文本嵌入模型，需通过 API Key 验证。


# 知识库（采用FAISS向量数据库）
class AcademicKnowledgeBase:
    def __init__(self, knowledge_dir=KNOWLEDGE_BASE_PATH):
        self.embeddings = OpenAIEmbeddings()  # 初始化文本嵌入模型，用于将文本转换为向量表示。
        self.vectorstore = None  # 初始化一个占位变量，稍后用于存储 FAISS 向量数据库实例。
        self.knowledge_dir = os.path.join(knowledge_dir, "academic")  # 指定原始学术文档（如 PDF）的存储目录路径。
        self.persist_dir = os.path.join(VECTOR_STORE_PATH, "faiss_academic")  # 指定 FAISS 向量数据库的持久化存储目录。
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.persist_dir, exist_ok=True)
        self._initialize_knowledge_base()  # 在初始化时自动调用，完成知识库的加载或创建。

    def _load_pdf_documents(self):
        """使用PyPDF加载PDF文档"""
        from langchain.docstore.document import Document
        documents = []

        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith(".pdf"):
                filepath = os.path.join(self.knowledge_dir, filename)
                try:
                    reader = PdfReader(filepath)
                    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                    documents.append(Document(
                        page_content=text,
                        metadata={"source": filename}
                    ))
                except Exception as e:
                    print(f"加载 {filename} 失败: {str(e)}")
        return documents

    def _initialize_knowledge_base(self):
        index_file = os.path.join(self.persist_dir, "index.faiss")
        if os.path.exists(index_file):
            # 从磁盘加载现有向量库
            self.vectorstore = FAISS.load_local(
                folder_path=self.persist_dir,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            self._create_knowledge_base()

    def _create_knowledge_base(self):
        # 加载学术文档(新的PDF加载方法)
        documents = self._load_pdf_documents()

        if not documents:
            raise ValueError(f"未找到可用的PDF文件，请检查目录: {self.knowledge_dir}")

        # 分割文本
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(documents)

        # 创建FAISS向量存储
        self.vectorstore = FAISS.from_documents(
            documents=splits,
            embedding=self.embeddings
        )
        # 保存FAISS索引
        self.vectorstore.save_local(self.persist_dir)

        print(f"已加载 {len(documents)} 篇文档，分割为 {len(splits)} 个文本块。")
        print("向量化完成，持久化到:", self.persist_dir)

    def retrieve_relevant_info(self, query: str, k: int = 3):
        """检索与查询相关的学术信息"""
        if not self.vectorstore:
            return []

        # FAISS的相似度搜索
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def add_document(self, file_path: str):
        """添加单个PDF文档"""
        from langchain.docstore.document import Document
        try:
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() for page in reader.pages])
            doc = Document(
                page_content=text,
                metadata={"source": os.path.basename(file_path)}
            )
            self.vectorstore.add_documents([doc])
            # 保存更新后的索引
            self.vectorstore.save_local(self.persist_dir)
            print(f"✓ 已添加: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"添加文档失败: {str(e)}")