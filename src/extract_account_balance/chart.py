from typing import List, Dict

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter


def build_series(records: List[Dict[str, float | str]]) -> List[tuple[str, float]]:
    series: List[tuple[str, float]] = []
    for row in records:
        label = row.get("month", row.get("date"))
        if label:
            series.append((str(label), float(row["balance"])))
    return series


def _currency_tick(value: float, _position: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


class BalanceChartCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None) -> None:
        self.figure = Figure(figsize=(5, 3))
        super().__init__(self.figure)
        self.setParent(parent)
        self.axes = self.figure.add_subplot(111)

    def render_records(self, records: List[Dict[str, float | str]]) -> None:
        self._render(records, include_rolling_average=True)

    def render_transactions(self, records: List[Dict[str, float | str]]) -> None:
        self._render(
            records,
            include_rolling_average=False,
            title="All transaction balances",
        )

    def _render(
        self,
        records: List[Dict[str, float | str]],
        include_rolling_average: bool,
        title: str = "Daily end-of-day account balance",
    ) -> None:
        self.axes.clear()
        self.axes.set_axis_on()
        series = build_series(records)
        if not series:
            self.axes.text(0.5, 0.5, "No data", ha="center", va="center")
            self.axes.set_axis_off()
            self.draw()
            return

        dates = [item[0] for item in series]
        balances = [item[1] for item in series]
        positions = list(range(len(dates)))
        self.axes.bar(positions, balances, color="#4f8cff")
        self.axes.set_xticks(positions, dates)
        rolling = [
            float(row["rolling_average"])
            for row in records
            if row.get("date") and "rolling_average" in row
        ] if include_rolling_average else []
        if len(rolling) == len(dates):
            self.axes.plot(
                positions,
                rolling,
                color="#d62728",
                linewidth=2.5,
                label="Rolling average",
                zorder=3,
            )
            self.axes.legend()
        self.axes.set_title(title)
        self.axes.set_ylabel("Balance")
        self.axes.yaxis.set_major_formatter(FuncFormatter(_currency_tick))
        self.axes.tick_params(axis="x", rotation=45)
        self.figure.tight_layout()
        self.draw()
