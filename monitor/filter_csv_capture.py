# PlatformIO device-monitor filter: parse combined_hr_temp lines → data/run_*.csv
# Enabled via monitor_filters in platformio.ini. Transparent — serial still prints normally.

import csv
import os
import re
import time
from datetime import datetime

from platformio.public import DeviceMonitorFilterBase

LINE_RE = re.compile(
    r"Avg BPM=(?P<bpm>--|[\d.]+)"
    r"(?:.*?IR=(?P<ir>\d+))?"
    r".*?\|\s*"
    r"Ambient=(?P<ambient>[\d.]+)\s*C,\s*"
    r"Object=(?P<object>[\d.]+)\s*C"
)
LAST_RE = re.compile(r"last=([\d.]+)")
BEATS_RE = re.compile(r"beats=(\d+)")

CSV_FIELDS = [
    "t_s",
    "bpm_avg",
    "bpm_last",
    "beats",
    "ir",
    "ambient_c",
    "object_c",
    "finger",
]


class CsvCapture(DeviceMonitorFilterBase):
    NAME = "csv_capture"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buf = ""
        self._fp = None
        self._writer = None
        self._n = 0
        self._t0 = None

    def __call__(self):
        data_dir = "data"
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        name = os.path.join(
            data_dir, "run_%s.csv" % datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        # pylint: disable=consider-using-with
        self._fp = open(name, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._fp, fieldnames=CSV_FIELDS)
        self._writer.writeheader()
        self._fp.flush()
        print("--- CSV capture → %s" % os.path.abspath(name))
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
        if not line or self._writer is None:
            return
        m = LINE_RE.search(line)
        if not m:
            return

        now = time.time()
        if self._t0 is None:
            self._t0 = now

        bpm_raw = m.group("bpm")
        finger = bpm_raw != "--"
        last_m = LAST_RE.search(line)
        beats_m = BEATS_RE.search(line)

        self._writer.writerow(
            {
                "t_s": f"{now - self._t0:.2f}",
                "bpm_avg": "" if not finger else bpm_raw,
                "bpm_last": last_m.group(1) if last_m else "",
                "beats": beats_m.group(1) if beats_m else "",
                "ir": m.group("ir") or "",
                "ambient_c": m.group("ambient"),
                "object_c": m.group("object"),
                "finger": "1" if finger else "0",
            }
        )
        self._fp.flush()
        self._n += 1
