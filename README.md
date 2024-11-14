# NL2SQL Query Generator ⛁

A Streamlit-based web application that converts natural language questions into SQL queries using LangChain and OpenAI's GPT models. This tool allows users to interact with their PostgreSQL database using plain English questions, modify or directly run the Query to generate results from the Database.

## Features

- Natural language to SQL query conversion
- Interactive query modification interface
- Real-time query execution
- Database schema visualization
- Secure database connection handling
- Custom-styled user interface
- Query review and modification options

## Prerequisites

- Python 3.7+
- PostgreSQL database
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd nl2sql
```

2. Install required dependencies: (listed below)
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Required Dependencies

```
streamlit
langchain
langchain-openai
langchain-community
python-dotenv
openai
sqlalchemy
```

## Usage

1. Start the application:
```bash
streamlit run nlsql2.py
```

2. Access the web interface through your browser (typically http://localhost:8501)

3. In the sidebar, enter your PostgreSQL database URI in the format:
```
postgresql://username:password@host:port/database_name
```

4. Enter your question in natural language in the text area

5. Click "Generate SQL Query" to convert your question to SQL

6. Review, modify if needed, and execute the generated query

## Features Breakdown

### Database Connection
- Secure database URI input through sidebar
- Real-time connection testing
- Error handling for connection issues

### Query Generation
- Natural language processing using GPT-4
- Schema-aware query generation
- Query modification capabilities
- SQL syntax highlighting

### Query Management
- Option to modify generated queries
- Query execution with results display
- Option to cancel query execution
- Error handling for query execution

## Architecture

![Untitled-2024-11-14-1445](https://github.com/user-attachments/assets/562aaf21-5ef2-4c45-aee0-e3e26a19d9f5)

## UI Snapshots

<img width="955" alt="Screenshot 2024-11-14 145927" src="https://github.com/user-attachments/assets/d106b024-5aae-4d48-8750-5a30a2ba6cfe">
<img width="952" alt="Screenshot 2024-11-14 145950" src="https://github.com/user-attachments/assets/fdf40b07-47b9-4875-9cda-32dc12cdfca1">
<img width="955" alt="Screenshot 2024-11-14 145927" src="https://github.com/user-attachments/assets/283df30d-2acd-4474-9795-d4e81f928862">



## Security Notes

- Database credentials are handled securely through password-masked input
- Environment variables are used for API key management
- No credentials are stored in the application state

## Error Handling

The application includes comprehensive error handling for:
- Database connection issues
- Query generation failures
- Query execution errors
- Invalid input validation

## Contributing

Contributions are welcome! Please feel free to reach out to the below-mentioned email ID.

## License

© GrowthArc 2024. All rights reserved.

## Support

For support or questions, please contact - vaishak.bhuvan@growtharc.com
