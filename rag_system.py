# rag_system.py

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

class ConsultingRAG:
    def __init__(self, knowledge_base_path="./knowledge_base"):
        self.knowledge_base_path = knowledge_base_path
        self.vectordb = None
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
    def build_knowledge_base(self):
        """Load all framework documents and create vector database"""
        
        print("📚 Loading framework documents...")
        
        # Fixed: Specify UTF-8 encoding for Windows
        loader = DirectoryLoader(
            self.knowledge_base_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}  # Added this line
        )
        documents = loader.load()
        
        print(f"✓ Loaded {len(documents)} documents")
        
        print("✂️ Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        
        print(f"✓ Created {len(chunks)} chunks")
        
        print("🔮 Creating vector database...")
        self.vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        
        print("✅ Knowledge base built successfully!")
        return self.vectordb
    
    def load_existing_db(self):
        """Load previously created vector database"""
        self.vectordb = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )
        return self.vectordb
    
    def get_relevant_frameworks(self, query, k=3):
        """
        Retrieve top K most relevant framework chunks for a given query
        """
        if self.vectordb is None:
            raise ValueError("Vector database not initialized.")
        
        relevant_docs = self.vectordb.similarity_search(query, k=k)
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        
        return context


def test_rag():
    """Test the RAG system"""
    
    print("\n🧪 Testing RAG System...\n")
    
    rag = ConsultingRAG()
    rag.build_knowledge_base()
    
    test_query = "How do I handle a post-merger integration?"
    print(f"\n📝 Test Query: {test_query}\n")
    
    context = rag.get_relevant_frameworks(test_query, k=2)
    
    print("🎯 Retrieved Frameworks:\n")
    print(context[:500] + "...\n")
    
    print("✅ Test complete!")


if __name__ == "__main__":
    test_rag()