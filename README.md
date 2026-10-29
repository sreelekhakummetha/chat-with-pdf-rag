# 📚 Chat with Your PDF — RAG Application

A Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions about their content. The application retrieves relevant passages from the PDF using semantic similarity search and generates context-aware answers using a Large Language Model (LLM) through the Groq API.

## 🚀 Features

- **PDF Upload:** Upload PDF documents directly through the Streamlit interface.
- **Text Extraction:** Extract text from PDF pages using PyPDF.
- **Text Chunking:** Split documents into smaller, overlapping chunks for effective retrieval.
- **Embeddings:** Convert text chunks into numerical vector representations using Sentence Transformers.
- **Vector Database:** Store and search embeddings using FAISS.
- **Semantic Search:** Retrieve the most relevant PDF passages for a user's question.
- **AI-Powered Answers:** Generate answers using the Groq API.
- **Source References:** Display retrieved passages with their PDF page numbers.
- **Chat Interface:** Ask multiple questions about the uploaded document.
- **Session Management:** Maintain conversation history during the current Streamlit session.

## 🧠 What Is RAG?

Retrieval-Augmented Generation (RAG) combines information retrieval with text generation.

Instead of relying only on the LLM's existing knowledge, the application retrieves relevant information from the uploaded PDF and supplies it as context to the model.

### RAG Workflow

```text
                Upload PDF
                    |
                    v
             Extract PDF Text
                    |
                    v
             Split into Chunks
                    |
                    v
            Generate Embeddings
                    |
                    v
              Store in FAISS
                    |
                    v
             User Asks Question
                    |
                    v
          Retrieve Relevant Chunks
                    |
                    v
          Build Contextual Prompt
                    |
                    v
              Groq LLM API
                    |
                    v
              Generate Answer
                    |
                    v
           Display Answer and Sources
```

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| LangChain | Document processing and vector-store integration |
| PyPDF | Extract text from PDF documents |
| Sentence Transformers | Generate text embeddings |
| FAISS | Store vectors and perform similarity search |
| Groq API | Generate answers using an LLM |
| Hugging Face | Host and provide the embedding model |
| python-dotenv | Load environment variables securely |

## 📁 Project Structure

```text
chat-with-pdf/
│
├── app.py              # Main Streamlit application
├── .env                # API key configuration (private)
├── .gitignore          # Files excluded from Git
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd chat-with-pdf
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your repository URL.

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux or macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

If you have not created `requirements.txt`, create one with:

```text
streamlit
python-dotenv
groq
langchain-community
langchain-huggingface
langchain-text-splitters
faiss-cpu
pypdf
sentence-transformers
```

Install the packages:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create an API key through the [Groq Console](https://console.groq.com/keys).

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_actual_groq_api_key
```

Replace the placeholder with your actual API key.

**Security note:** Never share your API key or commit your `.env` file to GitHub.

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## 📖 How to Use

1. Start the Streamlit application.
2. Enter your Groq API key in the sidebar, or configure it in `.env`.
3. Upload a PDF document.
4. Click **Process PDF**.
5. Wait for the application to extract text, create chunks, generate embeddings, and build the FAISS index.
6. Enter a question in the chat box.
7. View the generated answer.
8. Expand **View retrieved source passages** to inspect the relevant PDF text and page numbers.
9. Continue asking questions about the same document.

## 🔍 Understanding the Main Components

### 1. Text Chunking

The application uses `RecursiveCharacterTextSplitter` to split extracted text into manageable pieces.

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=120,
)
```

- `chunk_size=700`: Targets chunks of approximately 700 characters.
- `chunk_overlap=120`: Repeats some text between consecutive chunks to preserve context.

### 2. Embeddings

The application uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embedding model converts text into numerical vectors. Similar meanings tend to have nearby vector representations, enabling semantic search.

### 3. FAISS Vector Store

```python
vector_store = FAISS.from_documents(
    chunks,
    embeddings,
)
```

FAISS stores and searches the document embeddings so that relevant chunks can be retrieved for a question.

### 4. Retrieval

```python
retrieved_docs = vector_store.similarity_search(
    question,
    k=4,
)
```

The application retrieves up to four relevant chunks for the question.

### 5. LLM Answer Generation

The retrieved text is included in a prompt and sent to the Groq API. The model generates an answer using that context.

The application instructs the model not to invent facts and to say when the answer cannot be found in the supplied context.

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used to authenticate requests to Groq |

Keep secrets in environment variables rather than hardcoding them into your Python source code.

## ⚠️ Troubleshooting

**PDF processing fails**
- Confirm that the file is a valid PDF.
- If the PDF contains scanned images rather than selectable text, OCR may be necessary.
- Check that all dependencies are installed in the active virtual environment.

**Groq API authentication error**
- Verify that your API key is correct.
- Confirm that the key has not been revoked.
- Check the Groq Console for account restrictions.

**Model or rate-limit error**
- Confirm that the selected model is available to your account.
- Check current model availability, usage limits, and pricing in the Groq Console.

**Module not found**
- Activate your virtual environment.
- Run `python -m pip install -r requirements.txt`.

**Streamlit command not recognized**

Use:

```powershell
python -m streamlit run app.py
```

## 🔮 Future Enhancements

- Support multiple PDF documents.
- Add conversation memory across sessions.
- Implement OCR for scanned documents.
- Allow users to download chat history.
- Add streaming responses.
- Improve source citations and relevance scoring.
- Persist vector indexes between application restarts.
- Deploy the application to a cloud hosting platform.

## 🎯 Learning Outcomes

This project demonstrates practical implementation of:

- Retrieval-Augmented Generation (RAG)
- Document loading and text splitting
- Text embeddings and semantic search
- Vector databases using FAISS
- LLM API integration
- Prompt engineering and context grounding
- Building interactive AI applications with Streamlit

## 📄 License

This project is available for educational and personal learning purposes. Add a license file if you intend to distribute it under specific licensing terms.

---

**Built with Python, Streamlit, LangChain, FAISS, Sentence Transformers, and Groq.**
