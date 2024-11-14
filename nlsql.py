import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import re
from langchain.chains import create_sql_query_chain
import os
from langchain.chains import create_sql_query_chain
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
from dotenv import load_dotenv
load_dotenv()

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
        text_to_sql_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             """You are an expert SQL query generator, for the question asked, output only the sql query and nothing else.
             Do not output anything else, strictly output the query only.
             Return {top_k} rows only.
             Here is the table info {table_info}
             """),
            ("human", "{input}"),
        ])
        
        # Initialize Google AI model
        llmgem = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-001",
            temperature=0.3
        )
        
        # Create SQL chain
        sql_chain = create_sql_query_chain(llmgem, st.session_state.db_connection, text_to_sql_prompt)
        
        # User input
        user_question = st.text_area("Enter your question:", height=100)
        
        # Generate Query button
        if st.button("Generate SQL Query"):
            with st.spinner("Generating SQL query..."):
                try:
                    response = sql_chain.invoke({"question": user_question})
                    st.session_state.generated_query = extract_sql_query(response)
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