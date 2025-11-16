from fastapi import FastAPI, Depends, HTTPException
from app.models import Task, TaskCreate, TaskUpdate
from app.repository import TaskRepository
app = FastAPI()

repository = TaskRepository()

def get_repository():
    return repository

@app.get('/tasks', response_model=list[Task], status_code=200)
async def get_tasks(rep: TaskRepository = Depends(get_repository)):
    return rep.get_all()

@app.post('/tasks', response_model=Task, status_code=201)
async def create_task(task: TaskCreate, rep: TaskRepository = Depends(get_repository)):
    return rep.create(task)

@app.put('/tasks/{id}', response_model=Task, status_code=200)
async def update_task(*, id: int, task_request: TaskUpdate, rep: TaskRepository = Depends(get_repository)):
    return rep.update(id, task_request)

@app.delete('/tasks/{id}', status_code=204, response_description='Task deleted')
async def delete_task(*, id: int, rep: TaskRepository = Depends(get_repository)):
    status = rep.delete(id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")