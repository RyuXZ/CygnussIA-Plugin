"""
CygnussIA Plugin v2
Task Queue

Author: CygnussIA Project
License: MIT
"""

from __future__ import annotations

import asyncio
import traceback
import uuid

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Awaitable, Callable, Dict, Optional, Any

from logger import get_logger
from config import config

logger = get_logger(__name__)


# ============================================================
# Task Status
# ============================================================

class TaskStatus(str, Enum):

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ============================================================
# Task
# ============================================================

@dataclass
class Task:

    id: str

    name: str

    coroutine: Callable[..., Awaitable]

    kwargs: Dict[str, Any]

    created: datetime = field(default_factory=datetime.utcnow)

    started: Optional[datetime] = None

    finished: Optional[datetime] = None

    progress: int = 0

    status: TaskStatus = TaskStatus.PENDING

    result: Any = None

    error: Optional[str] = None

    cancelled: bool = False


# ============================================================
# Queue
# ============================================================

class TaskQueue:

    def __init__(self):

        self.queue = asyncio.Queue()

        self.tasks: Dict[str, Task] = {}

        self.workers = []

        self.worker_count = config.get("workers", 2)

        self.running = False

    # --------------------------------------------------------

    async def start(self):

        if self.running:

            return

        self.running = True

        logger.info("Starting %s workers", self.worker_count)

        for i in range(self.worker_count):

            worker = asyncio.create_task(

                self.worker_loop(i)

            )

            self.workers.append(worker)

    # --------------------------------------------------------

    async def stop(self):

        self.running = False

        for worker in self.workers:

            worker.cancel()

        self.workers.clear()

    # --------------------------------------------------------

    async def worker_loop(self, worker_id: int):

        logger.info("Worker %s started", worker_id)

        while self.running:

            task = await self.queue.get()

            if task.cancelled:

                task.status = TaskStatus.CANCELLED

                self.queue.task_done()

                continue

            task.started = datetime.utcnow()

            task.status = TaskStatus.RUNNING

            logger.info(

                "[%s] Started %s",

                worker_id,

                task.name

            )

            try:

                result = await task.coroutine(

                    **task.kwargs

                )

                task.result = result

                task.progress = 100

                task.status = TaskStatus.COMPLETED

            except asyncio.CancelledError:

                task.status = TaskStatus.CANCELLED

            except Exception as e:

                logger.error(traceback.format_exc())

                task.error = str(e)

                task.status = TaskStatus.FAILED

            finally:

                task.finished = datetime.utcnow()

                self.queue.task_done()

    # --------------------------------------------------------

    async def submit(

        self,

        name: str,

        coroutine,

        **kwargs

    ) -> str:

        task_id = str(uuid.uuid4())

        task = Task(

            id=task_id,

            name=name,

            coroutine=coroutine,

            kwargs=kwargs

        )

        self.tasks[task_id] = task

        await self.queue.put(task)

        logger.info(

            "Queued task %s",

            task_id

        )

        return task_id

    # --------------------------------------------------------

    def cancel(self, task_id: str):

        task = self.tasks.get(task_id)

        if task:

            task.cancelled = True

            task.status = TaskStatus.CANCELLED

            logger.info(

                "Cancelled %s",

                task_id

            )

    # --------------------------------------------------------

    def update_progress(

        self,

        task_id: str,

        value: int

    ):

        task = self.tasks.get(task_id)

        if task:

            task.progress = max(

                0,

                min(100, value)

            )

    # --------------------------------------------------------

    def get(self, task_id: str):

        return self.tasks.get(task_id)

    # --------------------------------------------------------

    def list(self):

        return list(self.tasks.values())

    # --------------------------------------------------------

    def clear_finished(self):

        remove = []

        for tid, task in self.tasks.items():

            if task.status in (

                TaskStatus.COMPLETED,

                TaskStatus.FAILED,

                TaskStatus.CANCELLED

            ):

                remove.append(tid)

        for tid in remove:

            del self.tasks[tid]


task_queue = TaskQueue()