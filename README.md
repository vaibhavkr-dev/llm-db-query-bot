# LLM DB Query Bot  

This is a starter repository for an LLM-powered database query bot built with **FastAPI** and **LangChain**. The bot demonstrates how to use a language model to generate and execute queries against both MongoDB and SQL databases via an agent.  

## Features  

- **FastAPI** application providing an HTTP endpoint for query requests.  
- Integration with **LangChain** to create an agent that interprets user intents and formulates appropriate database queries.  
- Supports both **MongoDB** and **SQL** databases through simple connectors.  
- Basic tests to verify endpoint behaviour and agent responses.  

## Requirements  

- Python 3.9+  
- FastAPI  
- Uvicorn  
- LangChain  
- SQLAlchemy (for SQL DB access)  
- Motor (for MongoDB async access)  

Install dependencies with:  

```bash  
pip install -r requirements.txt  
```  

## Running the App  

Start the FastAPI server:  

```bash  
uvicorn app.main:app --reload  
```  

Then send POST requests to `/query` with a JSON payload containing the database type, collection/table, and user question.  

## Tests  

Basic tests live in the `tests` directory and can be run with:  

```bash  
pytest  
```  

## License  

This project is provided as a starting point and does not include production-ready error handling or security. Use it at your own risk.
