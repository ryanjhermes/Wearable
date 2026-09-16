# iOS companion app

SwiftUI + CoreBluetooth client for the wearable. **v1 scope: live heart-rate readout only.**
Scan → connect → subscribe → display. It does not persist, export, or label anything.

Session capture and breathalyzer labeling are deliberately out of scope for v1 — see
[Roadmap](#roadmap).

## Build

### Prerequisites — not currently installed on this machine

Checked 2026-09-15: this Mac has **Command Line Tools only** (`xcode-select -p` →
`/Library/Developer/CommandLineTools`). There is no `Xcode.app`, no iOS SDK, and no `xcodegen`.
**None of this can be built or run until full Xcode is installed** from the App Store (~10 GB),
followed by `sudo xcode-select -s /Applications/Xcode.app` and `xcodegen` via Homebrew.

The Swift sources type-check clean against the macOS SDK, so the code itself is sound — but that
is a proxy check, not a real iOS build.

The `.xcodeproj` is **generated, not committed**. Both it and `Wearable/Info.plist` are
gitignored; `project.yml` is the source of truth.

```bash
brew install xcodegen
cd ios
xcodegen              # writes Wearable.xcodeproj + Wearable/Info.plist
open Wearable.xcodeproj
```

Re-run `xcodegen` after adding a file or changing `project.yml`. New `.swift` files under
`ios/Wearable/` are picked up automatically — no need to edit `project.yml` for those.

### You cannot test this in the Simulator

CoreBluetooth has no Simulator support. The app builds there but `CBCentralManager` never
reaches `.poweredOn`, so it sits on "Bluetooth off" forever. **A physical iPhone is required.**

Signing: set your team in Xcode (target → Signing & Capabilities → Automatically manage
signing). A free Apple ID works; builds expire after 7 days and need a re-install.
`PRODUCT_BUNDLE_IDENTIFIER` in `project.yml` may need changing if the default is taken.

## BLE contract

Matches `src/max30102_hr_ble_log/main.cpp` exactly. **If the firmware UUIDs change, change
[`BLEManager.swift`](Wearable/BLEManager.swift) to match** — nothing enforces this at build time.

| | UUID | Payload |
|---|---|---|
| Advertised name | `Wearable-HR` | — |
| Heart Rate service | `0x180D` | standard |
| ↳ HR Measurement | `0x2A37` | 2 bytes: flags `0x00`, then uint8 BPM |
| Telemetry service | `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` | Nordic-UART shaped |
| ↳ Telemetry notify | `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` | one UTF-8 CSV line per notify |

Telemetry line format: `t_ms,avg_bpm,last_bpm,beats,ir,finger`

Three line types arrive on that characteristic:
- `#now,<millis>` — clock anchor, sent as the **first** notify of every connection.
- `t_ms,avg_bpm,...` — the CSV header, sent at the head of a back-fill burst. Ignored.
- data rows.

## Gotchas

**The app can be working perfectly and still show nothing.** Check these before debugging Swift:

- **Range is ~1–2 ft.** The prototype's U.FL antenna has never been installed, so it radiates
  from a bare stub. Keep the phone touching the device. Drops every ~40–90 s are expected and
  the app re-scans automatically.
- **The device may be running the wrong firmware.** Per `CLAUDE.md`, the last confirmed flash
  left `RED_PULSE_AMPLITUDE` at the bad `0x1F`, which flattens the AC pulse ripple that beat
  detection needs → `beats` ≈ 0 and `avg_bpm` = 0 forever. That is a firmware fault, not an app
  bug. The fix is to reflash the `0x0A` build.
- **`avg_bpm` is 0 until two beats land in the 30 s window**, and clears on finger-lift. The UI
  shows `—` rather than `0` for this reason.
- **Back-fill bursts arrive at ~10 lines/sec** with `t_ms` stepping ~3000 per line. That is the
  device draining its offline buffer, not a glitch. v1 displays these as they stream past.
- **The advertising packet is over budget.** The firmware advertises the name plus *both* a
  16-bit and a 128-bit service UUID — roughly 38 bytes into a 31-byte payload. The 128-bit
  Nordic UUID is the likely casualty, so this app scans for `0x180D` only and filters by name.
  Do not "fix" it by scanning for the telemetry service.

## Roadmap

v1 is intentionally the smallest thing that proves the BLE path works on iOS. The app's real
job, once that is confirmed, is the one thing nothing else in this project does:

1. **Session capture** — persist rows, honour the `#now` anchor so back-filled samples get true
   timestamps instead of receive times (`scripts/ble_hr_stream.py` already implements this logic
   in Python; port it).
2. **Breathalyzer labeling** — timestamped BAC entry. No model trains without labels.
3. Export for training.

Note that v1 receives `#now` and stores it in `deviceUptimeMs`, but does not yet use it to map
`t_ms` → wall clock. That mapping is step 1.

## Files

| File | Role |
|---|---|
| [`project.yml`](project.yml) | XcodeGen spec — deployment target, bundle ID, Info.plist keys |
| [`Wearable/WearableApp.swift`](Wearable/WearableApp.swift) | App entry point, owns the `BLEManager` |
| [`Wearable/BLEManager.swift`](Wearable/BLEManager.swift) | Scan/connect/subscribe, packet + CSV parsing |
| [`Wearable/ContentView.swift`](Wearable/ContentView.swift) | Readout UI |
