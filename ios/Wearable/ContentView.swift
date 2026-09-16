import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var ble: BLEManager

    var body: some View {
        VStack(spacing: 32) {
            StatusPill(status: ble.status)

            BPMReadout(bpm: ble.bpm)

            if let t = ble.telemetry {
                SignalDetail(row: t)
            } else if ble.status == .connected {
                Text("Waiting for telemetry…")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            if let last = ble.lastUpdate {
                Text("Last update \(last.formatted(date: .omitted, time: .standard))")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
        }
        .padding(28)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .safeAreaPadding(.top, 24)
    }
}

private struct StatusPill: View {
    let status: BLEManager.Status

    private var tint: Color {
        switch status {
        case .connected:                 return .green
        case .scanning, .connecting:     return .orange
        case .bluetoothOff, .unauthorized: return .red
        case .disconnected:              return .secondary
        }
    }

    var body: some View {
        HStack(spacing: 8) {
            Circle().fill(tint).frame(width: 8, height: 8)
            Text(status.label).font(.subheadline.weight(.medium))
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(tint.opacity(0.12), in: Capsule())
    }
}

private struct BPMReadout: View {
    let bpm: Int?

    var body: some View {
        VStack(spacing: 4) {
            Text(bpm.map(String.init) ?? "––")
                .font(.system(size: 96, weight: .semibold, design: .rounded))
                .monospacedDigit()
                .contentTransition(.numericText())
                .animation(.snappy, value: bpm)
            Text("BPM")
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)
        }
    }
}

/// The firmware reports `avg_bpm` as 0 until it has seen two beats inside the
/// 30 s window, so a 0 here means "not enough beats yet", not a real reading.
private struct SignalDetail: View {
    let row: TelemetryRow

    var body: some View {
        VStack(spacing: 12) {
            HStack(spacing: 6) {
                Image(systemName: row.fingerPresent ? "hand.point.up.left.fill" : "hand.point.up.left")
                Text(row.fingerPresent ? "Contact detected" : "No contact")
            }
            .font(.subheadline)
            .foregroundStyle(row.fingerPresent ? .primary : .secondary)

            Grid(horizontalSpacing: 20, verticalSpacing: 6) {
                GridRow {
                    Text("Avg BPM").gridColumnAlignment(.trailing)
                    Text(row.avgBpm == 0 ? "—" : "\(row.avgBpm)")
                }
                GridRow {
                    Text("Last BPM")
                    Text(row.lastBpm == 0 ? "—" : "\(row.lastBpm)")
                }
                GridRow {
                    Text("Beats")
                    Text("\(row.beats)")
                }
                GridRow {
                    Text("IR")
                    Text("\(row.ir)")
                }
                GridRow {
                    Text("Uptime")
                    Text("\(row.tMs / 1000)s")
                }
            }
            .font(.caption.monospacedDigit())
            .foregroundStyle(.secondary)
        }
    }
}

#Preview {
    ContentView().environmentObject(BLEManager())
}
