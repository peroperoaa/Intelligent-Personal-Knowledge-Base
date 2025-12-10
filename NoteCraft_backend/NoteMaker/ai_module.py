import os
import tempfile
import requests
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from django.conf import settings

load_dotenv()

# Define DB directory
DB_DIR = os.path.join(settings.BASE_DIR, "db_chroma")

def get_vector_db():
    """
    Get the ChromaDB instance
    """
    # Use local embeddings (free, no API key required)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return vectordb

def process_pdf_from_url(pdf_url: str):
    """
    Downloads PDF from URL, processes it, and stores in vector DB
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            response = requests.get(pdf_url)
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Process the temporary file
        process_pdf_to_vector_db(temp_file_path)

        # Clean up
        os.remove(temp_file_path)
        return True
    except Exception as e:
        print(f"Error processing PDF from URL: {e}")
        return False

def process_pdf_to_vector_db(pdf_path: str):
    """
    Reads PDF, splits text, and stores in vector DB
    """
    try:
        # 1. Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # 2. Split Text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)

        # 3. Vectorize and Store
        # Use local embeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        vectordb = Chroma.from_documents(
            documents=texts, 
            embedding=embeddings,
            persist_directory=DB_DIR
        )
        # Chroma 0.4.x automatically persists, but explicit call doesn't hurt if older version
        # vectordb.persist() 
        print(f"Successfully added {pdf_path} to knowledge base")
        return True
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise e

def query_ai(query: str):
    """
    Queries the AI with the given question using RAG
    """
    try:
        vectordb = get_vector_db()
        
        # Initialize LLM with OpenRouter
        open_router_key = os.getenv("OPEN_ROUTER_API_KEY")
        if not open_router_key:
            print("Error: OPEN_ROUTER_API_KEY is missing.")
            raise ValueError("OPEN_ROUTER_API_KEY not found in environment variables")

        print(f"Initializing ChatOpenAI with model: meta-llama/llama-3.3-70b-instruct:free")
        
        llm = ChatOpenAI(
            model="meta-llama/llama-3.3-70b-instruct:free", 
            api_key=open_router_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0
        )

        # Build QA Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )

        # Custom Prompt to give it the "Golden Spatula" persona
        from langchain.prompts import PromptTemplate
        
        template = """
        你是一个《金铲铲之战》（Teamfight Tactics）的高手教练和智能助手。
        请根据下方的【参考资料】回答用户的问题。
        如果资料里没有提到，就诚实地说不知道，不要编造羁绊或装备数据。
        
        【参考资料】：
        {context}
        
        用户问题：{question}
        
        回答：
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        qa_chain.combine_documents_chain.llm_chain.prompt = prompt
        
        result = qa_chain.invoke({"query": query})
        
        return {
            "answer": result["result"],
            "sources": [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
        }
    except Exception as e:
        print(f"AI Query Error: {e}")
        raise e
