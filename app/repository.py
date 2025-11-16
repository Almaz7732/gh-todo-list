import json
from datetime import datetime

from app.models import Task


class TaskRepository:
    def __init__(self, file_path = 'tasks.json'):
        self.tasks = []
        self.file_path = file_path
        self._load()

    def _load(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.tasks = [Task(**task) for task in json.load(f)]
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None

    def _save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            tasks_dict = [task.model_dump() for task in self.tasks]
            json.dump(tasks_dict, f, ensure_ascii=False, indent=2, default=str)

    def get_all(self):
        return self.tasks

    def _get_max(self):
        if self.tasks:
            return max(task.id for task in self.tasks) + 1
        else:
            return 1

    def create(self, task):
        new_id = self._get_max()

        new_task = Task(
            id=new_id,
            title=task.title,
            description=task.description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.tasks.append(new_task)
        self._save()
        return new_task

    def update(self, task_id, task_request):
        for task in self.tasks:
            if task.id == task_id:
                if task_request.title is not None:
                    task.title = task_request.title
                if task_request.description is not None:
                    task.description = task_request.description

                task.updated_at = datetime.now()
                self._save()
                return task

    def delete(self, task_id):
        status = False
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                self._save()
                status = True

        return status