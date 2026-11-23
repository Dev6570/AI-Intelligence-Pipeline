# AI Intelligence Pipeline
## 1. Project Overview
The AI Intelligence Pipeline is a Python-based
system designed to collect, extract, process,
resolve and store intelligence data from
multiple sources.
It uses web scraping, Large Language Models,
entity resolution and MongoDB to organize
unstructured information into structured data.
## 2. Objectives
- Collect information from multiple data sources.
- Extract structured information using LLMs.
- Identify duplicate entities.
- Generate canonical entity identifiers.
- Store processed information in MongoDB.
- Provide API access to stored intelligence data.
## 3. Technology Stack
- Python
- MongoDB
- MongoDB Compass
- Large Language Models
- Pydantic
- RapidFuzz
- FastAPI
- Uvicorn
- Git and GitHub
## 4. Project Architecture
Data Collection
       |
       v
LLM-based Extraction
       |
       v
Entity Resolution
       |
       v
MongoDB Storage
       |
       v
FastAPI Backend
       |
       v
Data Retrieval
## 5. Project Structure
- src/scrapers: Data collection
- src/llm: LLM-based extraction
- src/resolver: Entity resolution
- src/database: Database integration
- src/production: API and production utilities
- tests: Automated tests
- data: Project datasets
- logs: Execution logs
## 6. Installation
Clone the repository:
git clone YOUR_GITHUB_REPOSITORY_URL
Move into the project directory:
cd AI-Intelligence-Pipeline
Create a virtual environment:
python -m venv .venv
Activate it on Windows:
.venv\Scripts\Activate.ps1
Install dependencies:
pip install -r requirements.txt
## 7. Environment Configuration
Create a .env file using .env.example
as a reference.
Configure your LLM API keys and MongoDB URI.
## 8. Running the Project
Run entity resolution:
python -m src.resolver.entity_resolution
Run database storage:
python -m src.database.pipeline_storage
Start the API:
uvicorn src.production.api:app --reload
## 9. API Documentation
After starting the API, open:
http://127.0.0.1:8000/docs
## 10. Testing
Run the tests:
python -m tests.test_entity_resolution
python -m tests.test_database
python -m tests.test_production
## 11. Future Enhancements
- Real-time data collection
- Advanced entity matching
- Distributed task processing
- Dashboard integration
- Improved monitoring and analytics