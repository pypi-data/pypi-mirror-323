from dataclasses import dataclass
from typing import Any

import pandas as pd
from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.widgets import DataTable
from textual.widgets.data_table import ColumnKey, CellKey


SORT_INDICATOR_UP = ' \u25b4'
SORT_INDICATOR_DOWN = ' \u25be'


@dataclass
class Sort:
    key: ColumnKey | None = None
    label: str = ''
    direction: bool = False

    def reverse(self) -> None:
        self.direction = not self.direction

    @property
    def indicator(self) -> str:
        return SORT_INDICATOR_UP if self.direction else SORT_INDICATOR_DOWN


class SortableDataTable(DataTable):
    BINDINGS = [
        Binding('z', 'toggle_zebra', 'Toggle Zebra'),
        Binding('ctrl+r', 'show_row_labels', 'Toggle Row labels')
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._sort = Sort()
        self.cursor_type = 'row'  # type: ignore
        self.data: pd.DataFrame | None = None

    def set_data(self, data: pd.DataFrame) -> None:
        self.data = data
        self.clear(columns=True)
        self._sort = Sort()

        if data is None or len(data) == 0:
            self.border_title = 'Results (0 rows)'
            return

        self.border_title = f'Results ({len(data)} rows)'
        self.add_columns(*data.columns.values.tolist())
        data = data.itertuples(index=False, name=None)
        for index, row in enumerate(data, 1):
            label = Text(str(index), style='#B0FC38 italic')
            self.add_row(*row, label=label)

    @on(DataTable.HeaderSelected)
    def header_clicked(self, header: DataTable.HeaderSelected) -> None:
        if self._sort.key is not None:
            column = self.columns[self._sort.key]
            column.label.remove_suffix(self._sort.indicator)
            self._update_column_width(self._sort.key)

        sort_value = Sort(header.column_key)
        if self._sort.key == sort_value.key:
            sort_value = self._sort
            sort_value.reverse()

        assert sort_value.key
        self.columns[header.column_key].label += sort_value.indicator
        self._update_column_width(header.column_key)

        self.sort(sort_value.key, reverse=sort_value.direction)
        self._sort = sort_value

    def _update_column_width(self, key: ColumnKey) -> None:
        self._update_column_widths({CellKey(row_key=next(iter(self.rows)), column_key=key)})

    def action_toggle_zebra(self) -> None:
        self.zebra_stripes = not self.zebra_stripes

    def action_show_row_labels(self) -> None:
        self.show_row_labels = not self.show_row_labels
