# MySQL-Database-Chatbot

MySQL-Database-Chatbot is a Streamlit based application that allows users to interact with a MySQL database through natural language queries. It uses the `langchain` and `langchain_groq` libraries to convert user queries into SQL, execute them on the database, and return results in natural language.

## Features

- Connect to a MySQL database
- Ask natural language questions about the database
- Get SQL queries generated and executed based on your questions
- Receive results in natural language

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/mysql-chatbot.git
    cd mysql-chatbot
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory of your project and add your `groq` api key:

    ```plaintext
    GROQ_API_KEY=<your_groq_api_key>
    
    ```

## Usage

1. Run the Streamlit application:

    ```bash
    streamlit run app.py
    ```

2. Open your web browser and go to `http://localhost:8501`.

3. In the sidebar, enter your MySQL database connection details and click `Connect`.

4. Once connected, you can start asking questions about your database.

## Code Overview

### `app.py`

This is the main file of the application. It contains the following key functions:

- `init_database`: Initializes the database connection using provided credentials.
- `get_sql_chain`: Sets up the SQL query generation chain using `langchain`.
- `get_response`: Generates a natural language response based on the SQL query and its result.

The main Streamlit application interface is also defined in this file, including the sidebar for database connection and the main chat interface.

### Dependencies

- `dotenv`: For loading environment variables from a `.env` file.
- `langchain_core`, `langchain_community`, `langchain_groq`: For setting up the language model and processing natural language queries.
- `streamlit`: For creating the web interface.

