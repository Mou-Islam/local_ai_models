# Local_ai_models
## Ollama API Gateway & Key Manager  

This project provides a secure, OpenAI-compatible API gateway that sits in front of local Ollama instance. It allows you to create and manage API keys, each scoped to a specific Ollama model, and then use those keys to interact with models through a standard OpenAI-compatible endpoint.
This is ideal for safely exposing local models to other applications or services without exposing the main Ollama API directly.  

## Key Features
- **Secure Key Management:** Create, view, and delete API keys through a simple and clean web interface.   
- **Model-Scoped Access:** Each API key is tied to a single Ollama model, preventing a key from accessing unauthorized models.    
- **Secure Proxy:** Acts as a lightweight, authenticating proxy to local Ollama server. The actual inference requests are streamed directly from Ollama for efficiency.   
- **Simple Web UI:** A straightforward frontend built with vanilla HTML, CSS, and JavaScript for managing keys.   
- **Example Client:** Includes a Python script (summarize.py) demonstrating how to use a generated API key to perform a task.   

## Getting Started  
Follow these steps to get the project running on local machine.  

## Prerequisites  
- Python 3.8+
- **Ollama:** Ensure you have Ollama installed(https://ollama.com/download/windows) and running.
- At least one model pulled (e.g., ollama pull llama3:8b).  

## Installation & Setup 
- Clone the repository (or create the project directory):
- git clone https://github.com/abirfan3724/local_ai_models.git
- cd local_ai_models 

## Create a Virtual Environment  
- It's highly recommended to use a virtual environment to manage dependencies.  
   python -m venv venv
  
**Activate it**:  
- **macOS/Linux**: source venv/bin/activate  
- **Windows:** .\venv\Scripts\activate  

## Install Dependencies

Install the required packages directly:
- pip install "fastapi[all]" sqlalchemy requests openai
- Run the Server: uvicorn main:app --reload
- The server will be available at http://localhost:8000.

## 1. Managing API Keys (Web Dashboard)  
- Once the server is running, you can manage API keys through the web interface.
- Open web browser and navigate to http://localhost:8000.
- You will see the API key management dashboard.
- Click the **"+ Create new secret key"** button.
- A modal will appear. The dropdown will be populated with all the models currently available in local Ollama instance.
- (Optional) Give key a descriptive name.
- Select a model from the dropdown.
- Click "Create secret key".
- A new modal will show generated API key. Copy and save this key somewhere safe, as you will not be able to see it again.
- Click "Done". New key will appear in the main table.
- Delete a key at any time by clicking the trash can icon (🗑️) in its row.

## 2. Using an API Key (Example Client)  
- The summarize.py script demonstrates how to use a generated API key with the OpenAI Python client.
- **Create an API Key:** Follow the steps above to create a key for a model you have, like llama3:8b.
- **Prepare the Input:** The project includes an input.txt file with sample text. You can use this or create own file.
- **Run the Script:** Open terminal and run the script, providing API key, the model name, and the input file.    
         - python summarize.py --key YOUR_COPIED_API_KEY --model llama3:8b --file input.txt
           (Replace YOUR_COPIED_API_KEY with the key you saved)

The script will connect to local gateway, authenticate with the key, send the text from **input.txt** to the specified model, and print the resulting summary.

## Project Structure  

├── frontend/  
│   ├── index.html            # Main HTML file for the dashboard  
│   ├── script.js             # JavaScript for dashboard interactivity (API calls, modals)  
│   └── style.css             # CSS for styling the dashboard   
├── database.py               # SQLAlchemy engine and database session setup  
├── main.py                   # The core FastAPI application (API endpoints, proxy logic)   
├── models.py                 # SQLAlchemy database models (APIKey table)   
├── requirements.txt          # Python package dependencies  
├── schemas.py                # Pydantic models for data validation and serialization   
├── summarize.py              # Example Python client to use the API gateway  
├── input.txt                 # Sample text file for the summarize.py script   
└── api_keys.db               # SQLite database file (will be created on first run)   
 
