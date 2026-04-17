import shutil
from collections import deque

from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from src.config import PROGRESS_COLUMNS_SEPARATOR, PROGRESS_MANAGER_COLORS


class ProgressManager:
    def __init__(self, task_name: str, item_description: str) -> None:
        self.task_name = task_name
        self.item_description = item_description
        self.color = "light_cyan3"
        self.panel_width = 40
        self.overall_buffer = deque(maxlen=5)
        self.overall_progress = self._create_progress_bar()
        self.task_progress = self._create_progress_bar(show_time=True)
        self.num_tasks = 0

    def get_panel_width(self) -> int:
        return self.panel_width

    def add_overall_task(self, description: str, num_tasks: int) -> None:
        self.num_tasks = num_tasks
        desc = description[:8] + "..." if len(description) > 8 else description
        self.overall_progress.add_task(f"[{self.color}]{desc}", total=num_tasks, completed=0)

    def add_task(self, current_task: int = 0, total: int = 100) -> int:
        desc = f"[{self.color}]{self.item_description} {current_task + 1}/{self.num_tasks}"
        return self.task_progress.add_task(desc, total=total)

    def update_task(self, task_id: int, completed: int | None = None, advance: int = 0, *, visible: bool = True) -> None:
        self.task_progress.update(
            task_id,
            completed=completed if completed is not None else None,
            advance=advance if completed is None else None,
            visible=visible,
        )
        self._update_overall_task(task_id)

    def create_progress_table(self, min_panel_width: int = 30) -> Table:
        terminal_width, _ = shutil.get_terminal_size()
        panel_width = max(min_panel_width, terminal_width // 2)

        progress_table = Table.grid()
        progress_table.add_row(
            Panel.fit(
                self.overall_progress,
                title=f"[bold {self.color}]Overall Progress",
                border_style=PROGRESS_MANAGER_COLORS["overall_border_color"],
                padding=(1, 1),
                width=panel_width,
            ),
            Panel.fit(
                self.task_progress,
                title=f"[bold {self.color}]{self.task_name} Progress",
                border_style=PROGRESS_MANAGER_COLORS["task_border_color"],
                padding=(1, 1),
                width=panel_width,
            ),
        )
        return progress_table

    def _update_overall_task(self, task_id: int) -> None:
        current_overall_task = self.overall_progress.tasks[-1]

        if self.task_progress.tasks[task_id].finished:
            self.overall_progress.advance(current_overall_task.id)
            self.task_progress.update(task_id, visible=False)

        if current_overall_task.finished:
            self.overall_buffer.append(current_overall_task)

        if len(self.overall_buffer) == self.overall_buffer.maxlen:
            self.overall_progress.remove_task(self.overall_buffer.popleft().id)

    def _create_progress_bar(self, *, show_time: bool = False) -> Progress:
        columns = [SpinnerColumn(), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%")]
        if show_time:
            columns += [PROGRESS_COLUMNS_SEPARATOR, TimeRemainingColumn()]
        return Progress("{task.description}", *columns)
