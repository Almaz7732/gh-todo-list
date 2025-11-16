# Todo List

Python and FastApi are used

## Features 
- RESTful API: Create, list, update, and delete tasks
- Fully tested with `pytest`

## Local Setup

```bash
git clone https://github.com/Almaz7732/gh-todo-list.git

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## Running the API
uvicorn app.main:app --reload
API will be available at http://127.0.0.1:8000 

## Running test
pytest test/test_main.py -v
```

