import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import re
import os
from langchain_openai import ChatOpenAI
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor

from dotenv import load_dotenv
load_dotenv()

from langchain_community.agent_toolkits import SQLDatabaseToolkit

llmoai = ChatOpenAI(model='gpt-4o-mini')


def extract_sql_query(text):
    pattern = r"```sql\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None

def main():
    st.markdown('<h1 class="custom-header">NL-2-SQL ⛁</h1>', unsafe_allow_html=True)
    st.markdown(
    """
    <style>
     body {
         color: #1E3C53;
    }

    .custom-header {
        font-family: "EB Garamond"; /* Change to your desired font */
        color: black; /* Custom color for the header */
        font-size: 3em; /* Change font size */
        text-align: center; /* Left align text */
        padding-bottom: 10px; /* Space below header */
        padding-top: 1px;
    }
    .subtitle{
    color: ##acc384; 
    border:1px;
    }
    .st-emotion-cache-bm2z3a {
        background: #FFFCF2;
    }
    .st-emotion-cache-1ny7cjd {
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    font-weight: 300;
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    min-height: 2.5rem;
    margin: 0px;
    line-height: 1.6;
    color: inherit;
    width: auto;
    user-select: none;
    border-radius: 20px;
    background-color: #ACC384;
    /* background-color: rgb(249, 249, 251); */
    border: 1px solid rgba(49, 51, 63, 0.2);
}
.st-emotion-cache-1gwvy71 h2 {
    font-weight: 400;
    font-family: "EB Garamond";
    color: black;
    text-align: left;
    padding-bottom: 10px;
}
.st-emotion-cache-1v7f65g .e1b2p2ww15 {
background:#ACC384;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}
.st-emotion-cache-1ny7cjd:hover {
    background-color: black;
    color: white;
}
.st-emotion-cache-1gwvy71 {
    background: #EAF4DB;
    padding: 0px 1.5rem 6rem;
}
.st-emotion-cache-12fmjuu{
background: #FFFCF2;
}
.st-emotion-cache-1mi2ry5{
background:#EAF4DB;
}

    </style>
    """,
    unsafe_allow_html=True
)
    

    
    # Initialize session state variables
    if 'generated_query' not in st.session_state:
        st.session_state.generated_query = None
    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = None
    if 'query_generated' not in st.session_state:
        st.session_state.query_generated = False
    if 'modified_query' not in st.session_state:
        st.session_state.modified_query = None
    if 'is_modifying' not in st.session_state:
        st.session_state.is_modifying = False
    
    # Sidebar for database connection
    with st.sidebar:
        st.header("Database Configuration")
        db_uri = st.text_input("Enter Database URI:", type="password")
        if db_uri:
            try:
                st.session_state.db_connection = SQLDatabase.from_uri(db_uri)
                st.success("Database connected successfully!")
            except Exception as e:
                st.error(f"Error connecting to database: {str(e)}")
                return
    
    # Main content
    if st.session_state.db_connection:

        # Create the prompt template
        toolkit = SQLDatabaseToolkit(db=st.session_state.db_connection, llm=llmoai)
        tools = toolkit.get_tools()
        tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
        schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
        tools = [tables_tool, schema_tool]
        llm = llmoai.bind_tools(tools)

        prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system",
            """You are helpful assitant who retrieves the schemas and demo data of tables relevant to the query from a postgresql database 
               using the tables and schema tool. 
               Do not write the SQL queries just retrieve the schemas and demo data.
            """,
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
    )
        
        agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm
    | OpenAIToolsAgentOutputParser()
)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        # Generate Query button

        user_question = st.text_area("Enter your question:", height=100)
        if st.button("Generate SQL Query"):
            with st.spinner("Generating SQL query..."):
                try:
                    response = list(agent_executor.stream({"input": user_question}))
                    table_info = response[-1]['messages'][0].content
                    query_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are helpful PostgreSQL Query Generator who can write excellent queries using the table schema and demo data provided.
               The query should be precise and should be able to retrieve the data so that it answers the users question propely.
               Table Info: {tableinfo}

               Just output the SQL Query and nothing else.
            """,
        ),
        ("user", "{input}")
    ]
)
                    chain = query_prompt | llmoai
                    query = chain.invoke({
                        'tableinfo': table_info,
                         'input':user_question
                    })

                    st.session_state.generated_query = extract_sql_query(query.content)
                    st.session_state.modified_query = st.session_state.generated_query
                    st.session_state.query_generated = True
                    st.session_state.is_modifying = False
                except Exception as e:
                    st.error(f"Error generating SQL query: {str(e)}")
        
        if st.session_state.query_generated:
            st.subheader("Generated SQL Query:")
            
            if st.session_state.is_modifying:
                modified_query = st.text_area("Modify your query:", 
                                            value=st.session_state.modified_query, 
                                            height=150)
                st.session_state.modified_query = modified_query

                if st.button("Save Changes"):
                    st.session_state.is_modifying = False
            else:
                st.code(st.session_state.modified_query, language="sql")

            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Run Query"):
                    with st.spinner("Executing query..."):
                        try:
                            query_result = st.session_state.db_connection.run(st.session_state.modified_query)
                            st.subheader("Query Results:")
                            st.write(query_result)
                        except Exception as e:
                            st.error(f"Error executing query: {str(e)}")

            with col2:
                if st.button("Modify Query"):
                    st.session_state.is_modifying = True

            with col3:
                if st.button("Don't Run"):
                    st.info("Query not executed. You can modify your question and try again.")
                    st.session_state.query_generated = False
                    st.session_state.generated_query = None
                    st.session_state.modified_query = None
                    st.session_state.is_modifying = False


st.markdown("""
<div style="position: fixed; bottom: 0; left: 0; width: 100%; background : linear-gradient(to bottom right, rgb(219, 198, 171) 100%, rgb(0, 0, 0) 5%); 
padding: 4px; text-align: center;">
<p class="text-4 opcty-6">©&nbsp;GrowthArc&nbsp;2024. All rights reserved.</p>  <a href="https://www.growtharc.com/" target="_blank"></a>
</div> """,unsafe_allow_html=True)


if __name__ == "__main__":
    main()