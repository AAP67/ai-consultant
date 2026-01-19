# AI Consultant

AI-powered Strategy & Operations consultant that uses proven consulting frameworks to analyze business challenges.

## Features
- 5 engagement types (Strategy, Process Improvement, M&A, etc.)
- RAG-based framework retrieval
- Powered by Claude AI
- Professional strategy brief generation

## Tech Stack
- Streamlit
- Anthropic Claude API
- LangChain + ChromaDB (RAG)
- HuggingFace Embeddings

## Local Setup
```bash
pip install -r requirements.txt
streamlit run app.py
```
```

### **B) Create `.gitignore`**
```
# Environment
.env
*.pyc
__pycache__/

# Vector database
chroma_db/

# Streamlit
.streamlit/

# OS
.DS_Store
Thumbs.db