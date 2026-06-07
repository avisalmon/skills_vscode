---
name: langchain-rag
description: >
  Build Retrieval-Augmented Generation (RAG) pipelines — load documents,
  split text, embed with Ollama or Azure OpenAI, store in a vector DB, and
  answer questions over your own data. TRIGGER: user says "RAG", "langchain",
  "retrieval augmented", "chat over my documents", "vector store", "embeddings
  pipeline", "PDF Q&A", or "semantic search over files".
---

# LangChain RAG — Chat Over Your Own Documents

> **Purpose**: Answer questions over private documents (PDFs, Word files,
> code, logs) using local or cloud LLMs. Keeps sensitive private data off
> external APIs when using Ollama.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Setup](#setup)
3. [Core RAG Pipeline](#core-rag-pipeline)
4. [Document Loaders](#document-loaders)
5. [Text Splitters](#text-splitters)
6. [Embeddings — Ollama vs Azure OpenAI](#embeddings--ollama-vs-azure-openai)
7. [Vector Stores](#vector-stores)
8. [Retrieval & QA Chain](#retrieval--qa-chain)
9. [Conversational RAG (Memory)](#conversational-rag-memory)
10. [Streaming Responses](#streaming-responses)
11. [Advanced: Custom Prompts](#advanced-custom-prompts)
12. [Evaluating RAG Quality](#evaluating-rag-quality)
13. [Lessons Learned](#lessons-learned)

---

## Quick Reference

```bash
# Minimal install
pip install langchain langchain-community langchain-ollama chromadb

# With Azure OpenAI
pip install langchain-openai

# With PDF support
pip install pypdf

# With Word support
pip install python-docx
```

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# 1. Load → 2. Split → 3. Embed → 4. Store → 5. Retrieve → 6. Generate
```

---

## Setup

```bash
# Minimal — local models via Ollama
pip install langchain langchain-community langchain-ollama chromadb pypdf

# With Azure OpenAI
pip install langchain langchain-openai chromadb pypdf

# Pull required Ollama models first
ollama pull nomic-embed-text   # for embeddings (fast, small)
ollama pull llama3.2           # for generation
```

---

## Core RAG Pipeline

The complete 6-step pipeline:

```python
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# ── Step 1: Load documents ────────────────────────────────────────────────────
loader = PyPDFLoader("my_document.pdf")
docs = loader.load()
print(f"Loaded {len(docs)} pages")

# ── Step 2: Split into chunks ─────────────────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
chunks = splitter.split_documents(docs)
print(f"Split into {len(chunks)} chunks")

# ── Step 3+4: Embed and store in vector DB ────────────────────────────────────
embeddings = OllamaEmbeddings(model="nomic-embed-text")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",    # saves to disk
)

# ── Step 5: Create retriever ──────────────────────────────────────────────────
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4},             # return top 4 chunks
)

# ── Step 6: QA chain ──────────────────────────────────────────────────────────
llm = ChatOllama(model="llama3.2", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
)

result = qa_chain.invoke({"query": "What are the key findings?"})
print(result["result"])
print("\nSources:")
for doc in result["source_documents"]:
    print(f"  - {doc.metadata}")
```

---

## Document Loaders

### Single files
```python
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
    JSONLoader,
)

# PDF (each page = one Document)
docs = PyPDFLoader("report.pdf").load()

# Word .docx
docs = Docx2txtLoader("spec.docx").load()

# Plain text
docs = TextLoader("notes.txt", encoding="utf-8").load()

# CSV (each row = one Document)
docs = CSVLoader("data.csv", source_column="title").load()

# Markdown
docs = UnstructuredMarkdownLoader("README.md").load()

# JSON with jq-style path
docs = JSONLoader("data.json", jq_schema=".[]", text_content=False).load()
```

### Directory of files
```python
from langchain_community.document_loaders import DirectoryLoader

# All PDFs in a folder
loader = DirectoryLoader("docs/", glob="**/*.pdf", loader_cls=PyPDFLoader)
docs = loader.load()

# All .md files
loader = DirectoryLoader("knowledge/", glob="**/*.md",
                          loader_cls=UnstructuredMarkdownLoader)
docs = loader.load()
```

### Web pages
```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader(["https://docs.example.com/page1",
                         "https://docs.example.com/page2"])
docs = loader.load()
```

---

## Text Splitters

```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
)

# Best general-purpose (tries to split on \n\n, \n, " ", then chars)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # target chars per chunk
    chunk_overlap=200,    # overlap between chunks (preserve context)
)

# For code (respects function/class boundaries)
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=2000,
    chunk_overlap=200,
)

# Token-aware (for LLM context window management)
splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)

chunks = splitter.split_documents(docs)
```

**Chunk size tuning:**
- Factual Q&A: `chunk_size=500, overlap=100`
- Technical docs / summaries: `chunk_size=1500, overlap=300`
- Code: `chunk_size=2000, overlap=200`

---

## Embeddings — Ollama vs Azure OpenAI

### Local (Ollama) — private, no API cost
```python
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
# Other good options: mxbai-embed-large, all-minilm
```

### Azure OpenAI — better quality, cloud
```python
from langchain_openai import AzureOpenAIEmbeddings
import os

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-15-preview",
)
```

### Test your embeddings
```python
vector = embeddings.embed_query("test sentence")
print(f"Embedding dimension: {len(vector)}")   # nomic: 768, ada-002: 1536
```

---

## Vector Stores

### Chroma (local, persistent, no server needed)
```python
from langchain_community.vectorstores import Chroma

# Build from documents
db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
)

# Load existing DB (no re-embedding)
db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
)
```

### FAISS (in-memory, fast)
```python
pip install faiss-cpu

from langchain_community.vectorstores import FAISS

db = FAISS.from_documents(chunks, embeddings)
db.save_local("faiss_index")                         # save to disk
db = FAISS.load_local("faiss_index", embeddings,     # load from disk
                       allow_dangerous_deserialization=True)
```

### Similarity search (direct, without chain)
```python
results = db.similarity_search("What is the package spec?", k=5)
for doc in results:
    print(doc.page_content[:200])
    print(doc.metadata)

# With scores
results = db.similarity_search_with_score("query", k=3)
for doc, score in results:
    print(f"Score: {score:.3f} | {doc.page_content[:100]}")
```

---

## Retrieval & QA Chain

### Simple QA (no memory)
```python
from langchain.chains import RetrievalQA
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2", temperature=0)

chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",              # "stuff" = put all chunks in one prompt
    retriever=db.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True,
)

result = chain.invoke({"query": "Summarize the design requirements"})
print(result["result"])
```

### MMR retriever (more diverse results)
```python
retriever = db.as_retriever(
    search_type="mmr",               # Maximum Marginal Relevance — reduces duplicates
    search_kwargs={"k": 6, "fetch_k": 20},
)
```

---

## Conversational RAG (Memory)

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2", temperature=0)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer",
)

chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=db.as_retriever(search_kwargs={"k": 4}),
    memory=memory,
    return_source_documents=True,
)

# Multi-turn conversation
r1 = chain.invoke({"question": "What are the main components?"})
print(r1["answer"])

r2 = chain.invoke({"question": "Which one handles the output stage?"})
print(r2["answer"])   # knows "one" refers to main components from r1
```

---

## Streaming Responses

```python
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate

llm = ChatOllama(model="llama3.2", temperature=0, streaming=True)

template = """Answer based only on the following context:
{context}

Question: {question}
Answer:"""

prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    {"context": db.as_retriever() | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Stream token by token
for token in chain.stream("What does section 3 say about power consumption?"):
    print(token, end="", flush=True)
```

---

## Advanced: Custom Prompts

```python
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

custom_prompt = PromptTemplate(
    template="""You are a helpful engineering assistant.
Use ONLY the following context to answer the question.
If the answer is not in the context, say "I don't have that information."

Context:
{context}

Question: {question}

Answer (be concise and cite section numbers when available):""",
    input_variables=["context", "question"],
)

chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": custom_prompt},
)
```

---

## Evaluating RAG Quality

```python
# Quick manual test — check retrieval is hitting the right chunks
def test_retrieval(query: str, db, k=4):
    docs = db.similarity_search(query, k=k)
    print(f"\nQuery: {query}")
    print(f"Retrieved {len(docs)} chunks:")
    for i, doc in enumerate(docs, 1):
        print(f"\n[{i}] {doc.metadata}")
        print(doc.page_content[:300])

test_retrieval("What is the maximum operating temperature?", db)

# Check if answer is grounded (no hallucination)
def check_grounding(answer: str, source_docs: list) -> bool:
    context = " ".join(d.page_content for d in source_docs)
    # Simple check: key phrases from answer appear in context
    words = [w for w in answer.split() if len(w) > 5]
    hits = sum(1 for w in words if w.lower() in context.lower())
    return hits / len(words) > 0.3 if words else False
```

**Signs of poor RAG quality and fixes:**
| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Wrong answer | Bad retrieval | Reduce chunk size, increase k |
| "I don't know" for info that exists | Embedding mismatch | Try different embedding model |
| Slow | Large chunk size × many docs | Use FAISS over Chroma for large sets |
| Duplicate content | Similar chunks retrieved | Use MMR retriever |

---

## Lessons Learned

- **Chunk overlap is critical**: Without overlap (200-300 chars), sentences
  at chunk boundaries are cut — causing missed answers.
- **Re-embed when you change models**: Chroma will silently return bad results
  if you change the embedding model without deleting and rebuilding the DB.
- **`temperature=0` for factual QA**: Higher temperature leads to hallucinated
  citations. Use 0 for retrieval-grounded answers.
- **Ollama embeddings are slow on CPU**: `nomic-embed-text` on CPU takes ~1s per
  chunk. For 500+ docs, pre-build the vector DB once and save it.
- **Azure OpenAI embeddings are much better quality** than local models for
  technical/domain-specific text. Use Ollama for privacy, Azure for accuracy.
- **`return_source_documents=True`**: Always enable this in production so users
  can verify answers against source material.
- **`stuff` chain type fails for large contexts**: If you have >10 chunks × 1000
  chars, switch to `map_reduce` or `refine` chain type.
- **corporate proxy**: Set `HTTPS_PROXY` if using Azure OpenAI API or downloading
  LangChain extensions on a corporate network.
