from typing import List, Dict

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


def build_series(records: List[Dict[str, float | str]]) -> List[tuple[str, float]]:
    series: List[tuple[str, float]] = []
    for row in records:
        if row.get("date"):
            series.append((str(row["date"]), float(row["balance"])))
    return series


class BalanceChartCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None) -> None:
        self.figure = Figure(figsize=(5, 3))
        super().__init__(self.figure)
        self.setParent(parent)
        self.axes = self.figure.add_subplot(111)

    def render_records(self, records: List[Dict[str, float | str]]) -> None:
        self.axes.clear()
        series = build_series(records)
        if not series:
            self.axes.text(0.5, 0.5, "No data", ha="center", va="center")
            self.axes.set_axis_off()
            self.draw()
            return

        dates = [item[0] for item in series]
        balances = [item[1] for item in series]
        self.axes.bar(dates, balances, color="#4f8cff")
        self.axes.set_title("Balance over time")
        self.axes.set_ylabel("Balance")
        self.axes.tick_params(axis="x", rotation=45)
        self.figure.tight_layout()
        self.draw()
