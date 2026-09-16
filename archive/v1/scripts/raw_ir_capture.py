#!/usr/bin/env python3
"""Capture the raw MAX30102 IR waveform streamed by the max30102_raw_ir firmware.

Subscribes to "Wearable-IR", expands each batched BLE notify into per-sample rows,
and saves data/raw_ir_*.csv (recv_ts, t_ms, ir). Auto-reconnects on link drops.

Usage (from repo root, venv active):
    pip install bleak
    python scripts/raw_ir_capture.py
    python scripts/raw_ir_capture.py --save data/raw_ir_rest.csv

Wear the device near the Mac and stay reasonably still for the cleanest signal,
then plot it: python scripts/plot_raw_ir.py
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

DEVICE_NAME = "Wearable-IR"
TELEM_CHAR = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

CSV_FIELDS = ["recv_ts", "t_ms", "ir"]


async def find_device(timeout: float = 15.0):
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and DEVICE_NAME in d.name,
        timeout=timeout,
    )
    if device is not None:
        print(f"Found {device.name} [{device.address}]")
    return device


async def stream_once(device, on_batch) -> None:
    async with BleakClient(device) as client:
        print("Connected. Capturing raw IR (Ctrl+C to stop)...")
        await client.start_notify(TELEM_CHAR, on_batch)
        while client.is_connected:
            await asyncio.sleep(1)
    print("Disconnected — re-scanning (a gap will appear in the capture).")


async def run(save_path: Path) -> None:
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fp = save_path.open("a", newline="", encoding="utf-8")
    writer = csv.writer(fp)
    if fp.tell() == 0:
        writer.writerow(CSV_FIELDS)
        fp.flush()
    print(f"Saving → {save_path.resolve()}")

    stats = {"rows": 0}

    def on_batch(_handle: int, data: bytearray) -> None:
        # "t_start_ms,hz,ir0,ir1,..." → one row per IR sample.
        line = data.decode("utf-8", errors="replace").strip()
        parts = line.split(",")
        if len(parts) < 3 or not parts[0].isdigit():
            return
        try:
            t_start = int(parts[0])
            hz = int(parts[1])
            irs = [int(x) for x in parts[2:]]
        except ValueError:
            return
        recv = datetime.now().isoformat(timespec="milliseconds")
        step = 1000.0 / hz if hz else 0
        for i, ir in enumerate(irs):
            writer.writerow([recv, round(t_start + i * step), ir])
        fp.flush()
        stats["rows"] += len(irs)
        # Compact live readout: last value + running count on one rewritten line.
        print(f"\rsamples={stats['rows']:>8}  last_ir={irs[-1]:>7}", end="", flush=True)

    print(f"Watching for {DEVICE_NAME} (Ctrl+C to stop)...")
    try:
        while True:
            device = await find_device()
            if device is None:
                print("Not in range — retrying...")
                await asyncio.sleep(3)
                continue
            try:
                await stream_once(device, on_batch)
            except Exception as exc:  # noqa: BLE001 — surface, then retry
                print(f"\nLink error ({exc}) — retrying...")
            await asyncio.sleep(2)
    finally:
        fp.close()
        print(f"\nSaved {stats['rows']} samples → {save_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture raw MAX30102 IR over BLE")
    parser.add_argument("--save", type=Path, help="CSV path (default: data/raw_ir_<ts>.csv)")
    args = parser.parse_args()

    save_path = args.save
    if save_path is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = Path("data") / f"raw_ir_{stamp}.csv"

    try:
        asyncio.run(run(save_path))
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
