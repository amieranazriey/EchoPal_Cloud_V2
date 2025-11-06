# admin_interface.py = provides the admin interface for EchoPal, allowing administrators to upload, view,
# and delete policy documents while managing their embeddings in the knowledge base.

import streamlit as st
import os
from embedding_manager import EmbeddingManager

# Directory to store uploaded PDFs
UPLOAD_FOLDER = "knowledge_base"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_manager():
    if "manager" not in st.session_state:
        st.session_state.manager = EmbeddingManager()
    return st.session_state.manager

def admin_interface():
    # Initialize the embedding manager
    manager = get_manager()

    st.title("🔐 EchoPal Admin Panel")
    st.write("Upload or manage policy documents for the EchoPal knowledge base.")

    # --- File Upload Section ---
    st.subheader("📤 Upload New Policy Document")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

        # Save uploaded file locally
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")

        # Process and embed the uploaded file
        with st.spinner("Processing and embedding the document..."):
            manager.add_pdf_to_collection(file_path)
        st.success("Document added to EchoPal knowledge base!")

    # --- Display Existing Files ---
    st.subheader("📚 Existing Knowledge Base Documents")

    # --- Refresh Button ---
    if st.button("🔄 Refresh Document List"):
        st.rerun()  # rerun the script to refresh the file list

    files = os.listdir(UPLOAD_FOLDER)
    if files:
        for file in files:
            st.write(f"📘 {file}")
    else:
        st.info("No documents found in the knowledge base yet.")

    # --- Delete Section ---
    st.subheader("🗑️ Delete a Document")

    delete_choice = st.selectbox("Select a file to delete", [""] + files)
    if delete_choice:
        if st.button(f"Delete '{delete_choice}'"):
            file_path = os.path.join(UPLOAD_FOLDER, delete_choice)

            # Remove file from local folder
            if os.path.exists(file_path):
                os.remove(file_path)
                st.success(f"✅ '{delete_choice}' removed from local folder.")

            # Remove chunks from vector DB using the new method
            try:
                manager.remove_pdf_from_collection(delete_choice)
            except Exception as e:
                st.error(f"Error removing from vector DB: {e}")
            else:
                st.success(f"🗑️ '{delete_choice}' removed from vector DB.")