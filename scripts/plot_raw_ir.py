#!/usr/bin/env python3
"""Preview a raw-IR capture: waveform, extracted AC pulse, and HR-band FFT.

Reads a CSV from raw_ir_capture.py (recv_ts, t_ms, ir). Uses numpy + matplotlib
only (no scipy) so it runs against the existing venv.

Usage:
    python scripts/plot_raw_ir.py                 # newest data/raw_ir_*.csv
    python scripts/plot_raw_ir.py data/raw_ir_rest.csv
    python scripts/plot_raw_ir.py --window 20     # analyze a 20 s slice

What to look for: a clean, repeating pulse in the AC panel and a single sharp peak
in the FFT panel's 0.7-3.5 Hz (42-210 BPM) band = the signal is good enough for an
autocorrelation/FFT HR estimator. Noise mush = we need better contact or filtering.
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError:
    print("Needs numpy + matplotlib: pip install numpy matplotlib", file=sys.stderr)
    sys.exit(1)

HR_LO_HZ, HR_HI_HZ = 0.7, 3.5  # 42-210 BPM


def load(path: Path):
    t_ms, ir = [], []
    with path.open() as f:
        next(f, None)  # header
        for row in f:
            c = row.strip().split(",")
            if len(c) >= 3 and c[1].lstrip("-").isdigit():
                t_ms.append(int(c[1]))
                ir.append(int(c[2]))
    return np.array(t_ms, dtype=float), np.array(ir, dtype=float)


def moving_average(x: np.ndarray, n: int) -> np.ndarray:
    if n < 2:
        return x
    kernel = np.ones(n) / n
    return np.convolve(x, kernel, mode="same")


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot a raw-IR capture")
    ap.add_argument("csv", nargs="?", help="CSV path (default: newest data/raw_ir_*.csv)")
    ap.add_argument("--window", type=float, default=0, help="seconds to analyze (0 = all)")
    args = ap.parse_args()

    path = Path(args.csv) if args.csv else None
    if path is None:
        files = sorted(glob.glob("data/raw_ir_*.csv"))
        if not files:
            print("No data/raw_ir_*.csv found — capture one first.", file=sys.stderr)
            sys.exit(1)
        path = Path(files[-1])
    print(f"Loading {path}")

    t_ms, ir = load(path)
    if len(ir) < 50:
        print(f"Only {len(ir)} samples — capture longer.", file=sys.stderr)
        sys.exit(1)

    t = (t_ms - t_ms[0]) / 1000.0
    fs = (len(t) - 1) / (t[-1] - t[0]) if t[-1] > t[0] else 100.0
    print(f"{len(ir)} samples, ~{fs:.1f} Hz effective, {t[-1]:.1f} s")

    if args.window and args.window < t[-1]:
        mask = t <= args.window
        t, ir = t[mask], ir[mask]

    # AC pulse = IR minus a ~1 s moving-average baseline (removes DC drift).
    baseline = moving_average(ir, max(2, int(fs)))
    ac = ir - baseline

    # FFT of the AC signal, restricted to the HR band.
    ac_win = (ac - ac.mean()) * np.hanning(len(ac))
    spec = np.abs(np.fft.rfft(ac_win))
    freqs = np.fft.rfftfreq(len(ac_win), d=1.0 / fs)
    band = (freqs >= HR_LO_HZ) & (freqs <= HR_HI_HZ)
    peak_bpm = None
    if band.any():
        peak_hz = freqs[band][np.argmax(spec[band])]
        peak_bpm = peak_hz * 60
        print(f"Dominant HR-band peak: {peak_hz:.2f} Hz ≈ {peak_bpm:.0f} BPM")

    fig, ax = plt.subplots(3, 1, figsize=(11, 8))
    ax[0].plot(t, ir, lw=0.6)
    ax[0].set_title(f"Raw IR — {path.name}")
    ax[0].set_ylabel("IR (counts)")

    ax[1].plot(t, ac, lw=0.6, color="tab:orange")
    ax[1].set_title("AC pulse (IR − 1 s baseline)")
    ax[1].set_xlabel("time (s)")
    ax[1].set_ylabel("AC")

    ax[2].plot(freqs[band], spec[band], color="tab:green")
    if peak_bpm:
        ax[2].axvline(peak_bpm / 60, color="k", ls="--", lw=0.8,
                      label=f"{peak_bpm:.0f} BPM")
        ax[2].legend()
    ax[2].set_title("HR-band FFT (peak = estimated rate)")
    ax[2].set_xlabel("frequency (Hz)")
    ax[2].set_ylabel("magnitude")

    fig.tight_layout()
    out = path.with_suffix(".png")
    fig.savefig(out, dpi=110)
    print(f"Saved plot → {out}")
    plt.show()


if __name__ == "__main__":
    main()
