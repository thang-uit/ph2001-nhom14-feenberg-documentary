import CoreAudio
import Foundation

enum DeviceError: Error, CustomStringConvertible {
    case coreAudio(OSStatus, String)
    case notFound(String)

    var description: String {
        switch self {
        case let .coreAudio(status, operation):
            return "\(operation) failed with OSStatus \(status)"
        case let .notFound(name):
            return "Audio device not found: \(name)"
        }
    }
}

func checked(_ status: OSStatus, _ operation: String) throws {
    guard status == noErr else { throw DeviceError.coreAudio(status, operation) }
}

func deviceIDs() throws -> [AudioDeviceID] {
    var address = AudioObjectPropertyAddress(
        mSelector: kAudioHardwarePropertyDevices,
        mScope: kAudioObjectPropertyScopeGlobal,
        mElement: kAudioObjectPropertyElementMain
    )
    var size: UInt32 = 0
    try checked(
        AudioObjectGetPropertyDataSize(AudioObjectID(kAudioObjectSystemObject), &address, 0, nil, &size),
        "Get audio-device list size"
    )
    var devices = [AudioDeviceID](
        repeating: 0,
        count: Int(size) / MemoryLayout<AudioDeviceID>.size
    )
    try checked(
        AudioObjectGetPropertyData(
            AudioObjectID(kAudioObjectSystemObject), &address, 0, nil, &size, &devices
        ),
        "Get audio-device list"
    )
    return devices
}

func deviceName(_ id: AudioDeviceID) throws -> String {
    var address = AudioObjectPropertyAddress(
        mSelector: kAudioObjectPropertyName,
        mScope: kAudioObjectPropertyScopeGlobal,
        mElement: kAudioObjectPropertyElementMain
    )
    var value: CFString = "" as CFString
    var size = UInt32(MemoryLayout<CFString>.size)
    try checked(
        withUnsafeMutablePointer(to: &value) { pointer in
            AudioObjectGetPropertyData(id, &address, 0, nil, &size, pointer)
        },
        "Get device name"
    )
    return value as String
}

func defaultDevice(selector: AudioObjectPropertySelector) throws -> AudioDeviceID {
    var address = AudioObjectPropertyAddress(
        mSelector: selector,
        mScope: kAudioObjectPropertyScopeGlobal,
        mElement: kAudioObjectPropertyElementMain
    )
    var value = AudioDeviceID(0)
    var size = UInt32(MemoryLayout<AudioDeviceID>.size)
    try checked(
        AudioObjectGetPropertyData(
            AudioObjectID(kAudioObjectSystemObject), &address, 0, nil, &size, &value
        ),
        "Get default audio device"
    )
    return value
}

func setDefaultDevice(_ id: AudioDeviceID, selector: AudioObjectPropertySelector) throws {
    var address = AudioObjectPropertyAddress(
        mSelector: selector,
        mScope: kAudioObjectPropertyScopeGlobal,
        mElement: kAudioObjectPropertyElementMain
    )
    var value = id
    let size = UInt32(MemoryLayout<AudioDeviceID>.size)
    try checked(
        AudioObjectSetPropertyData(
            AudioObjectID(kAudioObjectSystemObject), &address, 0, nil, size, &value
        ),
        "Set default audio device"
    )
}

func findDevice(named requestedName: String) throws -> AudioDeviceID {
    for id in try deviceIDs() where try deviceName(id) == requestedName {
        return id
    }
    throw DeviceError.notFound(requestedName)
}

do {
    let arguments = CommandLine.arguments
    guard arguments.count >= 2 else {
        print("Usage: coreaudio_device list | current | set-output <exact device name>")
        exit(2)
    }

    switch arguments[1] {
    case "list":
        for id in try deviceIDs() {
            print("\(id)\t\(try deviceName(id))")
        }
    case "current":
        let normal = try defaultDevice(selector: kAudioHardwarePropertyDefaultOutputDevice)
        let system = try defaultDevice(selector: kAudioHardwarePropertyDefaultSystemOutputDevice)
        print("default-output\t\(normal)\t\(try deviceName(normal))")
        print("system-output\t\(system)\t\(try deviceName(system))")
    case "set-output":
        guard arguments.count == 3 else {
            print("set-output requires one exact device name")
            exit(2)
        }
        let id = try findDevice(named: arguments[2])
        try setDefaultDevice(id, selector: kAudioHardwarePropertyDefaultOutputDevice)
        try setDefaultDevice(id, selector: kAudioHardwarePropertyDefaultSystemOutputDevice)
        print("output-set\t\(id)\t\(try deviceName(id))")
    default:
        print("Unknown command: \(arguments[1])")
        exit(2)
    }
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
