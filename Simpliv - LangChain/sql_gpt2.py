# Now we will create a application that can take the user query and query the database and get the output

# For this we need to create a UI to take in the Database Connection details.

# And then we can use the sql agent from langchain to query the database.

# Import the libraries we need
import streamlit as st
import os
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI

# Title
st.title("Query Database using GPT-3")

# Setting the open AI key
os.environ["OPENAI_API_KEY"] = "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"

# Create a dictionary of which database to use
db_products_dict = {
    "Sample DB": ["sqlite", "sqlite+pysqlite"],
    'Postgres': ['postgres', 'postgresql+psycopg2'],
    'SQL Server': ['mssql', 'mssql+pyodbc'],
    'Oracle': ['oracle', 'oracle+cx_oracle'],
    'MySQL': ['mysql', 'mysql+pymysql'],

}

# Create a sidebar to let the user select the database
with st.sidebar:
    st.write('Pick your DB connection:')
    db_type = st.selectbox('DB connection', db_products_dict.keys())

    # If the user selects a database type apart from the default one, ask them to enter connection details
    if db_type != 'Sample DB':
        db_host = st.text_input('Enter DB host')
        db_port = st.text_input('Enter DB port')
        db_user = st.text_input('Enter DB user')
        db_password = st.text_input('Enter DB password')
        db_name = st.text_input('Enter DB name')

    if st.button("Connect"):
        st.session_state['db_connection'] = True

if st.session_state.get('db_connection'):
    if db_type != 'Sample DB':
        # check if the user has entered a database credentials
        if not db_host or not db_user or not db_password or not db_name or not db_port:
            st.error('Please enter the database credentials')
            st.stop()

    # try to connect to the database
    try:
        if db_type != 'Sample DB':
            # Create a URI to connect to the database
            uri = f'{db_products_dict[db_type][1]}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

        else:
            # Create a URI to connect to the sample database
            uri = 'sqlite:///employee_data.db'

        # Create a connection
        db = SQLDatabase.from_uri(uri)

    except Exception as e:
        st.error(f'Could not connect to the database. Error: {e}')
        st.stop()

# If the database connection is successful, then we can create the agent
if "db_connection" not in st.session_state:
    st.stop()

# Lets define our chat model
llm = ChatOpenAI(temperature=0)

# defining the toolkit and passing the database and llm
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Finally we will define our agent and pass the toolkit and llm

sql_agent = create_sql_agent(
    llm=OpenAI(temperature=0),
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# Now we will get the user input and query the database
# Creating the ChatBot on the Main Page
# Initialize chat history
# Note: The history here is only for the display purpose on the screen, we are not using or passing it to the LLM
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Query your database here..."):

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        with st.spinner("Thinking..."):
            # Query the DB
            response = sql_agent.run(prompt)

            # Add the response to the chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Display the response
            message_placeholder.markdown(response)

