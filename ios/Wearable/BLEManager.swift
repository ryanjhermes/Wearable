import Foundation
import CoreBluetooth

/// BLE client for the `Wearable-HR` firmware (`src/max30102_hr_ble_log/`).
///
/// The device exposes two services:
///   * Standard Heart Rate (0x180D) → Heart Rate Measurement (0x2A37), 2-byte packet.
///   * Nordic-UART-shaped telemetry → one CSV line per notify.
///
/// v1 is read-only: it displays live values and does not persist anything.
/// Session capture and breathalyzer labeling are deliberately out of scope.
final class BLEManager: NSObject, ObservableObject {

    // MARK: - UUIDs (must match the firmware — see ios/README.md)

    static let hrService    = CBUUID(string: "180D")
    static let hrMeasChar   = CBUUID(string: "2A37")
    static let telemService = CBUUID(string: "6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    static let telemChar    = CBUUID(string: "6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
    static let deviceName   = "Wearable-HR"

    // MARK: - Published state

    enum Status: Equatable {
        case bluetoothOff
        case unauthorized
        case scanning
        case connecting
        case connected
        case disconnected

        var label: String {
            switch self {
            case .bluetoothOff: return "Bluetooth off"
            case .unauthorized: return "Bluetooth not permitted"
            case .scanning:     return "Scanning…"
            case .connecting:   return "Connecting…"
            case .connected:    return "Connected"
            case .disconnected: return "Disconnected"
            }
        }
    }

    @Published private(set) var status: Status = .disconnected
    /// BPM from the standard Heart Rate Measurement characteristic.
    @Published private(set) var bpm: Int?
    /// Latest parsed telemetry row, or nil if none received this connection.
    @Published private(set) var telemetry: TelemetryRow?
    /// Device uptime in ms reported by the `#now` clock anchor on connect.
    @Published private(set) var deviceUptimeMs: UInt64?
    @Published private(set) var lastUpdate: Date?

    // MARK: - Internals

    private var central: CBCentralManager!
    /// Must be retained — CoreBluetooth does not hold a strong reference for us.
    private var peripheral: CBPeripheral?

    override init() {
        super.init()
        central = CBCentralManager(delegate: self, queue: .main)
    }

    private func startScan() {
        guard central.state == .poweredOn else { return }
        status = .scanning
        // Scan by the 16-bit HR service rather than nil: it is the one UUID the
        // firmware reliably fits in the advertising packet (see README).
        central.scanForPeripherals(withServices: [Self.hrService])
    }

    private func resetReadings() {
        bpm = nil
        telemetry = nil
        deviceUptimeMs = nil
    }
}

// MARK: - Central delegate

extension BLEManager: CBCentralManagerDelegate {

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .poweredOn:
            startScan()
        case .unauthorized:
            status = .unauthorized
        default:
            status = .bluetoothOff
            resetReadings()
        }
    }

    func centralManager(_ central: CBCentralManager,
                        didDiscover peripheral: CBPeripheral,
                        advertisementData: [String: Any],
                        rssi RSSI: NSNumber) {
        // The service filter already narrowed this, but the name check keeps us
        // off any other 0x180D device in range (a chest strap, a watch).
        let advName = advertisementData[CBAdvertisementDataLocalNameKey] as? String
        guard advName == Self.deviceName || peripheral.name == Self.deviceName else { return }

        central.stopScan()
        self.peripheral = peripheral
        peripheral.delegate = self
        status = .connecting
        central.connect(peripheral)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        status = .connected
        resetReadings()
        peripheral.discoverServices([Self.hrService, Self.telemService])
    }

    func centralManager(_ central: CBCentralManager,
                        didFailToConnect peripheral: CBPeripheral,
                        error: Error?) {
        self.peripheral = nil
        startScan()
    }

    func centralManager(_ central: CBCentralManager,
                        didDisconnectPeripheral peripheral: CBPeripheral,
                        error: Error?) {
        self.peripheral = nil
        status = .disconnected
        resetReadings()
        // The prototype drops the link often (missing U.FL antenna). Re-scan
        // immediately rather than making the user retry by hand.
        startScan()
    }
}

// MARK: - Peripheral delegate

extension BLEManager: CBPeripheralDelegate {

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        for service in peripheral.services ?? [] {
            let wanted = service.uuid == Self.hrService ? Self.hrMeasChar : Self.telemChar
            peripheral.discoverCharacteristics([wanted], for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral,
                    didDiscoverCharacteristicsFor service: CBService,
                    error: Error?) {
        for characteristic in service.characteristics ?? []
        where characteristic.properties.contains(.notify) {
            peripheral.setNotifyValue(true, for: characteristic)
        }
    }

    func peripheral(_ peripheral: CBPeripheral,
                    didUpdateValueFor characteristic: CBCharacteristic,
                    error: Error?) {
        guard let data = characteristic.value else { return }

        switch characteristic.uuid {
        case Self.hrMeasChar:
            if let value = Self.parseHeartRateMeasurement(data) {
                bpm = value
                lastUpdate = Date()
            }

        case Self.telemChar:
            guard let line = String(data: data, encoding: .utf8)?
                .trimmingCharacters(in: .whitespacesAndNewlines),
                  !line.isEmpty else { return }

            if line.hasPrefix("#now,") {
                deviceUptimeMs = UInt64(line.dropFirst("#now,".count))
            } else if let row = TelemetryRow(csvLine: line) {
                telemetry = row
                lastUpdate = Date()
            }
            // Anything else is the CSV header that leads a back-fill burst.

        default:
            break
        }
    }

    /// Bluetooth SIG Heart Rate Measurement (0x2A37).
    /// Bit 0 of the flags byte selects uint8 vs uint16 BPM. The firmware always
    /// sends uint8, but parsing the flag keeps this spec-correct.
    static func parseHeartRateMeasurement(_ data: Data) -> Int? {
        guard let flags = data.first else { return nil }
        let isUInt16 = flags & 0x01 != 0

        if isUInt16 {
            guard data.count >= 3 else { return nil }
            return Int(UInt16(data[1]) | UInt16(data[2]) << 8)
        } else {
            guard data.count >= 2 else { return nil }
            return Int(data[1])
        }
    }
}

// MARK: - Telemetry

/// One line of the custom telemetry stream:
/// `t_ms,avg_bpm,last_bpm,beats,ir,finger`
struct TelemetryRow: Equatable {
    let tMs: UInt64
    let avgBpm: Int
    let lastBpm: Int
    let beats: Int
    let ir: Int
    let fingerPresent: Bool

    init?(csvLine: String) {
        let f = csvLine.split(separator: ",", omittingEmptySubsequences: false)
        guard f.count >= 6,
              let tMs     = UInt64(f[0]),
              let avgBpm  = Int(f[1]),
              let lastBpm = Int(f[2]),
              let beats   = Int(f[3]),
              let ir      = Int(f[4]),
              let finger  = Int(f[5])
        else { return nil }

        self.tMs = tMs
        self.avgBpm = avgBpm
        self.lastBpm = lastBpm
        self.beats = beats
        self.ir = ir
        self.fingerPresent = finger != 0
    }
}
