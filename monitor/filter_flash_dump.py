# PlatformIO monitor filter: capture ---FLASH_DUMP_BEGIN--- … END--- → data/hr_flash_*.csv
# Enabled via monitor_filters on the max30102_hr_log env.

import os
from datetime import datetime

from platformio.public import DeviceMonitorFilterBase


class FlashDump(DeviceMonitorFilterBase):
    NAME = "flash_dump"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buf = ""
        self._capturing = False
        self._fp = None
        self._n = 0

    def __call__(self):
        return self

    def __del__(self):
        if self._fp:
            self._fp.close()

    def rx(self, text):
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._handle_line(line.rstrip("\r"))
        return text

    def _handle_line(self, line):
        if line.strip() == "---FLASH_DUMP_BEGIN---":
            data_dir = "data"
            if not os.path.isdir(data_dir):
                os.makedirs(data_dir)
            name = os.path.join(
                data_dir,
                "hr_flash_%s.csv" % datetime.now().strftime("%Y%m%d_%H%M%S"),
            )
            if self._fp:
                self._fp.close()
            # pylint: disable=consider-using-with
            self._fp = open(name, "w", encoding="utf-8")
            self._capturing = True
            self._n = 0
            print("--- Flash dump → %s" % os.path.abspath(name))
            return

        if line.strip() == "---FLASH_DUMP_END---":
            if self._fp:
                self._fp.flush()
                self._fp.close()
                self._fp = None
            self._capturing = False
            print("--- Flash dump done (%d lines)" % self._n)
            return

        if self._capturing and self._fp:
            self._fp.write(line + "\n")
            self._n += 1
