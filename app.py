
import os
import tempfile
import hashlib

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

st.set_page_config(
    page_title="Chat with PDF | RAG",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Chat with Your PDF")
st.caption(
    "Ask questions about your PDF using RAG, embeddings, FAISS, and an LLM."
)


# --------------------------------------------------
# 1. Load the embedding model once
# --------------------------------------------------
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# --------------------------------------------------
# 2. Initialize Streamlit session state
# --------------------------------------------------
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

if "pdf_signature" not in st.session_state:
    st.session_state.pdf_signature = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 3. Sidebar configuration
# --------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    groq_api_key = st.text_input(
        "Groq API key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Enter your Groq API key. Keep it private.",
    )

    st.markdown("---")
    st.markdown("### RAG Pipeline")

    st.write("1. Extract text from PDF")
    st.write("2. Split text into chunks")
    st.write("3. Generate embeddings")
    st.write("4. Store vectors in FAISS")
    st.write("5. Retrieve relevant chunks")
    st.write("6. Generate an answer using Groq")


# --------------------------------------------------
# 4. Upload a PDF
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload your PDF document",
    type=["pdf"],
)

if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()

    # Identify the exact uploaded PDF.
    current_signature = (
        uploaded_file.name,
        hashlib.sha256(pdf_bytes).hexdigest(),
    )

    # Remove an old index if a different PDF is uploaded.
    if st.session_state.pdf_signature != current_signature:
        st.session_state.vector_store = None
        st.session_state.pdf_name = None
        st.session_state.pdf_signature = None
        st.session_state.messages = []

    st.info(f"Selected document: {uploaded_file.name}")

    if st.button("Process PDF", type="primary"):
        temp_path = None

        try:
            with st.spinner(
                "Extracting PDF text and building the vector store..."
            ):
                # Save the uploaded PDF temporarily.
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf",
                ) as temp_file:
                    temp_file.write(pdf_bytes)
                    temp_path = temp_file.name

                # Extract text from every PDF page.
                documents = PyPDFLoader(temp_path).load()

                if not documents or not any(
                    doc.page_content.strip() for doc in documents
                ):
                    st.error(
                        "No readable text was found in the PDF. "
                        "A scanned PDF may require OCR."
                    )
                    st.stop()

                # Split the text into smaller overlapping chunks.
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=700,
                    chunk_overlap=120,
                )

                chunks = splitter.split_documents(documents)

                if not chunks:
                    st.error("No text chunks could be created.")
                    st.stop()

                # Generate embeddings for the chunks.
                embeddings = load_embeddings()

                # Store the embeddings in FAISS.
                vector_store = FAISS.from_documents(
                    chunks,
                    embeddings,
                )

                # Save the processed document in session state.
                st.session_state.vector_store = vector_store
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.pdf_signature = current_signature
                st.session_state.messages = []

            st.success(
                f"PDF processed successfully! Created {len(chunks)} "
                f"chunks from {len(documents)} pages."
            )

        except Exception as exc:
            st.error(f"PDF processing failed: {exc}")

        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)


# --------------------------------------------------
# 5. Chat interface
# --------------------------------------------------
if st.session_state.vector_store is not None:
    st.divider()

    st.subheader(
        f"Ask questions about: {st.session_state.pdf_name}"
    )

    # Display previous messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("View retrieved source passages"):
                    for source in message["sources"]:
                        st.markdown(f"**Page {source['page']}**")
                        st.write(source["text"])

    # Accept the user's question.
    question = st.chat_input(
        "Ask something about your PDF..."
    )

    if question:
        if not groq_api_key.strip():
            st.warning(
                "Enter your Groq API key in the sidebar "
                "before asking a question."
            )

        else:
            # Display and save the question.
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            with st.chat_message("user"):
                st.markdown(question)

            try:
                with st.chat_message("assistant"):
                    with st.spinner(
                        "Searching the PDF and generating an answer..."
                    ):
                        # STEP 1: Retrieve relevant chunks from FAISS.
                        retrieved_docs = (
                            st.session_state.vector_store
                            .similarity_search(
                                question,
                                k=4,
                            )
                        )

                        # STEP 2: Build context and source information.
                        context_parts = []
                        sources = []

                        for doc in retrieved_docs:
                            # PyPDFLoader stores page numbers starting at 0.
                            page = doc.metadata.get("page", 0) + 1

                            context_parts.append(
                                f"[Page {page}]\n{doc.page_content}"
                            )

                            sources.append(
                                {
                                    "page": page,
                                    "text": doc.page_content,
                                }
                            )

                        context = "\n\n".join(context_parts)

                        # STEP 3: Create a prompt using retrieved text.
                        prompt = f"""Answer the question using only the
provided PDF context.

If the answer is not present in the context, say:
"I could not find the answer in the PDF."

Do not invent facts. Cite relevant page numbers when possible.

PDF CONTEXT:
{context}

QUESTION:
{question}
"""

                        # STEP 4: Connect to the Groq API.
                        client = Groq(
                            api_key=groq_api_key.strip()
                        )

                        # STEP 5: Generate the answer.
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are a helpful PDF assistant. "
                                        "Use only the PDF context supplied "
                                        "by the user. Do not invent facts."
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content": prompt,
                                },
                            ],
                            max_completion_tokens=600,
                        )

                        answer = (
                            response.choices[0].message.content
                            or "The model did not return an answer."
                        )

                        st.markdown(answer)

                        # Show the source passages used for retrieval.
                        with st.expander(
                            "View retrieved source passages"
                        ):
                            for source in sources:
                                st.markdown(
                                    f"**Page {source['page']}**"
                                )
                                st.write(source["text"])

                # Save the answer and its sources.
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as exc:
                st.error(
                    f"Could not generate the answer: {exc}\n\n"
                    "Check your Groq API key, model availability, "
                    "and API rate limits."
                )

else:
    st.info(
        "Upload a PDF and click Process PDF to start chatting."
    )
