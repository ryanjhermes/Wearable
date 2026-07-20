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


async def find_device(timeout: float = 15.0):
    print(f"Scanning for {DEVICE_NAME} ({timeout:.0f}s)...")
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and DEVICE_NAME in d.name,
        timeout=timeout,
    )
    if device is None:
        raise RuntimeError(f"{DEVICE_NAME} not found — is firmware flashed and board powered?")
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


async def run(save_path: Path | None) -> None:
    device = await find_device()
    writer = None
    fp = None

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fp = save_path.open("w", newline="", encoding="utf-8")
        writer = csv.writer(fp)
        writer.writerow(FIELDS)
        fp.flush()
        print(f"Saving → {save_path.resolve()}")

    def on_telem(_handle: int, data: bytearray) -> None:
        line = data.decode("utf-8", errors="replace").strip()
        print(line)
        if writer:
            parts = line.split(",")
            if len(parts) == len(FIELDS):
                writer.writerow(parts)
                fp.flush()

    def on_hr(_handle: int, data: bytearray) -> None:
        bpm = parse_hr(data)
        if bpm is not None:
            print(f"[HR service] BPM={bpm}")

    async with BleakClient(device) as client:
        print("Connected. Waiting for 1 Hz notifications (Ctrl+C to stop)...")
        await client.start_notify(TELEM_CHAR, on_telem)
        await client.start_notify(HR_CHAR, on_hr)
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            await client.stop_notify(TELEM_CHAR)
            await client.stop_notify(HR_CHAR)

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
