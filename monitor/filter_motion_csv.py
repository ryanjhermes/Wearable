# PlatformIO device-monitor filter: parse BMI160 logger lines → data/motion_*.csv
# Firmware emits:  M,<t_ms>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>
# Enable via monitor_filters in the bmi160_motion_log env. Transparent — serial still prints.

import csv
import os
from datetime import datetime

from platformio.public import DeviceMonitorFilterBase

CSV_FIELDS = ["t_s", "ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps"]


class MotionCsv(DeviceMonitorFilterBase):
    NAME = "motion_csv"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buf = ""
        self._fp = None
        self._writer = None
        self._t0_ms = None

    def __call__(self):
        data_dir = "data"
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        name = os.path.join(
            data_dir, "motion_%s.csv" % datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        # pylint: disable=consider-using-with
        self._fp = open(name, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._fp, fieldnames=CSV_FIELDS)
        self._writer.writeheader()
        self._fp.flush()
        print("--- motion capture → %s" % os.path.abspath(name))
        return self

    def __del__(self):
        if self._fp:
            self._fp.close()

    def rx(self, text):
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._handle_line(line.strip())
        return text

    def _handle_line(self, line):
        if not line.startswith("M,") or self._writer is None:
            return
        parts = line.split(",")
        if len(parts) != 8:
            return
        try:
            t_ms = int(parts[1])
            vals = [float(p) for p in parts[2:]]
        except ValueError:
            return

        if self._t0_ms is None:
            self._t0_ms = t_ms

        self._writer.writerow(
            {
                "t_s": f"{(t_ms - self._t0_ms) / 1000.0:.3f}",
                "ax_g": vals[0], "ay_g": vals[1], "az_g": vals[2],
                "gx_dps": vals[3], "gy_dps": vals[4], "gz_dps": vals[5],
            }
        )
        self._fp.flush()
