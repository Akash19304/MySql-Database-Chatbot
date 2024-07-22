from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from functools import lru_cache
import asyncio

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(db_uri, poolclass=QueuePool, pool_size=10, max_overflow=20)
    return SQLDatabase(engine)

@lru_cache(maxsize=32)
def get_schema(db: SQLDatabase):
    return db.get_table_info()

def get_sql_chain(db, schema):
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
    For example:
    Question: which 3 artists have the most tracks?
    SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
    Question: Name 10 artists
    SQL Query: SELECT Name FROM Artist LIMIT 10;
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(temperature=0, model="mixtral-8x7b-32768")
    return RunnablePassthrough().assign(schema=lambda _: schema) | prompt | llm | StrOutputParser()

def get_response(user_query: str, db: SQLDatabase, chat_history: list, schema: str):
    try:
        sql_chain = get_sql_chain(db, schema)
        template = """
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, question, sql query, and sql response, write a natural language response.
        <SCHEMA>{schema}</SCHEMA>
    
        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        User question: {question}
        SQL Response: {response}
        """
        prompt = ChatPromptTemplate.from_template(template)
        llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
    
        chain = (
            RunnablePassthrough()
            .assign(query=lambda vars: sql_chain.invoke(vars))
            .assign(schema=lambda _: schema)
            .assign(response=lambda vars: db.run(vars["query"]))
            | prompt
            | llm
            | StrOutputParser()
        )
    
        return chain.invoke({"question": user_query, "chat_history": chat_history})
    except Exception as e:
        return f"An error occurred: {e}"

async def async_get_response(user_query: str, db: SQLDatabase, chat_history: list, schema: str):
    return await asyncio.to_thread(get_response, user_query, db, chat_history, schema)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [AIMessage(content="Hi, I'm a MySQL Assistant. How can I help you?")]

st.set_page_config(page_title="MySQL Chatbot", page_icon=":clipboard:")
st.header("Chat with MySQL :robot_face:")

with st.sidebar:
    st.subheader("Settings")
    st.write("Connect with Database!")

    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", key="User")
    st.text_input("Password", type="password", key="Password")
    st.text_input("Database", value="world", key="Database")

    if st.button("Connect"):
        with st.spinner("Connecting..."):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            st.session_state.db = db
            st.session_state.schema = get_schema(db)
            st.success("Connected to Database!")

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Enter your message: ")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = asyncio.run(async_get_response(user_query, st.session_state.db, st.session_state.chat_history, st.session_state.schema))
        st.markdown(response)

    st.session_state.chat_history.append(AIMessage(content=response))
