import shutil
from collections import deque
from datetime import UTC, datetime
from typing import Any, cast

from rich.box import SIMPLE
from rich.panel import Panel
from rich.table import Table

from src.config import LOG_MANAGER_CONFIG


class LoggerTable:
    def __init__(self, max_rows: int = 4) -> None:
        self.row_buffer: deque[tuple[str, str, str]] = deque(maxlen=max_rows)
        colors = cast(dict[str, str], LOG_MANAGER_CONFIG["colors"])
        self.title_color: str = colors["title_color"]
        self.border_style: str = colors["border_color"]
        self.table = self._create_table()

    def log(self, event: str, details: str) -> None:
        timestamp = datetime.now(UTC).strftime("%H:%M:%S")
        self.row_buffer.append((timestamp, event, details))

    def render_log_panel(self, panel_width: int = 40) -> Panel:
        log_table = self._render_table()
        return Panel.fit(
            log_table,
            title=f"[bold {self.title_color}]Log Messages",
            border_style=self.border_style,
            width=2 * panel_width,
        )

    def _calculate_column_widths(
        self, min_column_widths: dict[str, Any], padding: int = 10
    ) -> dict[str, int]:
        terminal_width, _ = shutil.get_terminal_size()
        available_width = terminal_width - padding
        total_min_width = sum(min_column_widths.values())

        if available_width < total_min_width:
            return {k: int(v) for k, v in min_column_widths.items()}

        remaining_width = available_width - total_min_width
        return {
            column: int(min_width) + remaining_width // len(min_column_widths)
            for column, min_width in min_column_widths.items()
        }

    def _create_table(self) -> Table:
        min_column_widths = cast(
            dict[str, Any], LOG_MANAGER_CONFIG["min_column_widths"]
        )
        column_widths = self._calculate_column_widths(min_column_widths)
        column_styles = cast(dict[str, Any], LOG_MANAGER_CONFIG["column_styles"])
        column_names = ["Timestamp", "Event", "Details"]

        new_table = Table(
            box=SIMPLE,
            show_header=True,
            show_edge=True,
            show_lines=False,
            border_style=self.title_color,
        )

        for name in column_names:
            new_table.add_column(
                f"[{self.title_color}]{name}",
                style=str(column_styles[name]),
                width=column_widths[name],
            )

        return new_table

    def _render_table(self) -> Table:
        new_table = self._create_table()
        for row in self.row_buffer:
            new_table.add_row(*row)
        return new_table
