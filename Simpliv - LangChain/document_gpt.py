## Document GPT


# First we will develop a application that can take documents and then we can Query over those document

# We will be using the CSV Loader, PDF Loader, WEB Page Loader that we have used above
# to query the document and website respectively.

# We will create a Front End that can Upload Csv and PDF files and take Web page url


import streamlit as st # Streamlit is a Python library that makes it easy to build beautiful apps for machine learning.
from langchain.chat_models import ChatOpenAI
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import CSVLoader
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.document_loaders import PyPDFLoader, WebBaseLoader
from tempfile import NamedTemporaryFile

# Setting the open AI key

import os

os.environ["OPENAI_API_KEY"] = "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"

# Create a Streamlit application

# Title of the application
st.title("Document GPT")

# Create a sidebar
with st.sidebar:
    # Create a radio button to select the document type
    document_type = st.radio("Select Document Type", ("CSV", "PDF", "Web Page"))

    # Create a file uploader for CSV files
    if document_type == "CSV":
        file = st.file_uploader("Upload a CSV file", type=["csv"])
        if file is not None:
            # create a temporary file to store the uploaded file
            with NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                temp_file.write(file.getvalue())
                temp_path = temp_file.name

            csv_loader = CSVLoader(file_path=temp_path)
            st.session_state['loader'] = csv_loader

    # Create a file uploader for PDF files
    elif document_type == "PDF":
        file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if file is not None:
            with NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file.getvalue())
                temp_path = temp_file.name

            pdf_loader = PyPDFLoader(file_path=temp_path)
            st.session_state['loader'] = pdf_loader

    # Create a text box to enter the URL of the web page
    elif document_type == "Web Page":
        url = st.text_input("Enter the URL of the web page")
        if url is not None:
            webpage_loader = WebBaseLoader(url)
            st.session_state['loader'] = webpage_loader

    # Create a button to load the document
    if st.button("Load Document"):

        if st.session_state['loader']:
            # Create a index
            index = VectorstoreIndexCreator(
                vectorstore_cls=DocArrayInMemorySearch
            ).from_loaders(
                loaders=[st.session_state['loader']]
            )

            # Save the index in the session state
            st.session_state['index'] = index

            # Setting index created to True in the session state
            st.session_state['index_created'] = True
        else:
            st.error("Please upload a document first")

if "index_created" not in st.session_state:
    st.stop()

# Creating the ChatBot on the Main Page
# Initialize chat history
# Note: The history here is only for the display purpose on the screen, we are not using or passing it to the LLM
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask a question about your document here..."):
    # Add user message to chat history

    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            # Query the Index
            response = st.session_state['index'].query(prompt)

            # Add the response to the chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Display the response
            message_placeholder.markdown(response)




