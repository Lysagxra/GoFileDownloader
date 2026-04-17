import datetime
import time

from rich.align import Align
from rich.console import Group
from rich.live import Live
from rich.text import Text

from src.version import get_version_string

from .log_manager import LoggerTable
from .progress_manager import ProgressManager


class LiveManager:
    def __init__(
        self,
        progress_manager: ProgressManager,
        logger_table: LoggerTable,
        refresh_per_second: int = 10,
    ) -> None:
        self.progress_manager = progress_manager
        self.progress_table = self.progress_manager.create_progress_table()
        self.logger_table = logger_table
        self.live = Live(
            self._render_live_view(), refresh_per_second=refresh_per_second
        )
        self.start_time = time.time()
        self.update_log(event="Started", details="Script execution started")

    def add_overall_task(self, description: str, num_tasks: int) -> None:
        self.progress_manager.add_overall_task(description, num_tasks)

    def add_task(self, current_task: int = 0, total: int = 100) -> int:
        return self.progress_manager.add_task(current_task, total)

    def update_task(
        self,
        task_id: int,
        completed: int | None = None,
        advance: int = 0,
        *,
        visible: bool = True,
    ) -> None:
        self.progress_manager.update_task(task_id, completed, advance, visible=visible)

    def update_log(self, *, event: str, details: str) -> None:
        self.logger_table.log(event, details)
        self.live.update(self._render_live_view())

    def stop(self) -> None:
        elapsed = time.time() - self.start_time
        td = datetime.timedelta(seconds=elapsed)
        hrs, mins, secs = td.seconds // 3600, (td.seconds % 3600) // 60, td.seconds % 60
        self.update_log(
            event="Completed", details=f"Time: {hrs:02}:{mins:02}:{secs:02}"
        )
        self.live.stop()

    def _render_live_view(self) -> Group:
        panel_width = self.progress_manager.get_panel_width()
        footer = Align.left(Text(get_version_string(), style="dim"))
        return Group(
            self.progress_table,
            self.logger_table.render_log_panel(panel_width=2 * panel_width),
            footer,
        )
