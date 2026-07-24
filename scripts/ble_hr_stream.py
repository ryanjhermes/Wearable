#!/usr/bin/env python3
"""Subscribe to Wearable-HR BLE telemetry and print/save CSV lines.

Usage (from repo root, venv active):
    pip install bleak
    python scripts/ble_hr_stream.py

Optional: python scripts/ble_hr_stream.py --save data/ble_hr_live.csv
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from datetime import datetime
from pathlib import Path

try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    print("Install bleak first: pip install bleak", file=sys.stderr)
    sys.exit(1)

DEVICE_NAME = "Wearable-HR"
TELEM_SERVICE = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
TELEM_CHAR = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
HR_SERVICE = "0000180d-0000-1000-8000-00805f9b34fb"
HR_CHAR = "00002a37-0000-1000-8000-00805f9b34fb"

FIELDS = ["t_ms", "avg_bpm", "last_bpm", "beats", "ir", "finger"]
# recv_ts = wall-clock time the Mac received the line. Accurate for LIVE data;
# for a back-fill burst it's the drain time, not the original sample time (use
# the device's t_ms for relative sample timing).
CSV_FIELDS = ["recv_ts"] + FIELDS


async def find_device(timeout: float = 15.0):
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and DEVICE_NAME in d.name,
        timeout=timeout,
    )
    if device is not None:
        print(f"Found {device.name} [{device.address}]")
    return device


def parse_hr(data: bytearray) -> int | None:
    if not data:
        return None
    flags = data[0]
    if flags & 0x01:
        if len(data) >= 3:
            return int(data[1]) | (int(data[2]) << 8)
        return None
    if len(data) >= 2:
        return int(data[1])
    return None


async def stream_once(device, on_telem, on_hr) -> None:
    """Connect and stream until the link drops. Returns on disconnect."""
    async with BleakClient(device) as client:
        print("Connected. Streaming (back-fill first, then 1 Hz)...")
        await client.start_notify(TELEM_CHAR, on_telem)
        await client.start_notify(HR_CHAR, on_hr)
        # Poll the link; when we walk out of range this flips False and we return
        # to the reconnect loop. The device keeps buffering to flash meanwhile.
        while client.is_connected:
            await asyncio.sleep(1)
    print("Disconnected — will re-scan and reconnect; buffered data back-fills on return.")


async def run(save_path: Path | None) -> None:
    writer = None
    fp = None

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        # Append across reconnects so one file spans the whole session.
        fp = save_path.open("a", newline="", encoding="utf-8")
        writer = csv.writer(fp)
        if fp.tell() == 0:
            writer.writerow(CSV_FIELDS)
            fp.flush()
        print(f"Saving → {save_path.resolve()}")

    def on_telem(_handle: int, data: bytearray) -> None:
        now = datetime.now()
        line = data.decode("utf-8", errors="replace").strip()
        print(f"{now:%H:%M:%S}  {line}")
        if writer:
            parts = line.split(",")
            # Skip the CSV header that leads a store-and-forward back-fill burst.
            if len(parts) == len(FIELDS) and parts[0].isdigit():
                writer.writerow([now.isoformat(timespec="seconds")] + parts)
                fp.flush()

    def on_hr(_handle: int, data: bytearray) -> None:
        bpm = parse_hr(data)
        if bpm is not None:
            print(f"[HR service] BPM={bpm}")

    # Reconnect loop: keep trying forever so temporary drops (out of range, board
    # reset) resume on their own. Ctrl+C to stop.
    print(f"Watching for {DEVICE_NAME} (Ctrl+C to stop)...")
    while True:
        device = await find_device()
        if device is None:
            print("Not in range — retrying...")
            await asyncio.sleep(3)
            continue
        try:
            await stream_once(device, on_telem, on_hr)
        except Exception as exc:  # noqa: BLE001 — surface, then retry
            print(f"Link error ({exc}) — retrying...")
        await asyncio.sleep(2)

    if fp:
        fp.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream Wearable-HR over BLE")
    parser.add_argument(
        "--save",
        type=Path,
        help="Optional CSV path (default: data/ble_hr_YYYYMMDD_HHMMSS.csv)",
    )
    args = parser.parse_args()

    save_path = args.save
    if save_path is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = Path("data") / f"ble_hr_{stamp}.csv"

    try:
        asyncio.run(run(save_path))
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
