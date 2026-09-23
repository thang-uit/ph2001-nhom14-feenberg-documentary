import AVFoundation
import CoreMedia
import Foundation
import ScreenCaptureKit

enum CaptureError: Error, CustomStringConvertible {
    case noDisplay
    case cannotAddInput
    case writerFailed(String)

    var description: String {
        switch self {
        case .noDisplay:
            return "No display is available for ScreenCaptureKit."
        case .cannotAddInput:
            return "Cannot add the AAC audio input to AVAssetWriter."
        case let .writerFailed(message):
            return "Audio writer failed: \(message)"
        }
    }
}

final class SystemAudioRecorder: NSObject, SCStreamOutput, SCStreamDelegate {
    private let outputURL: URL
    private let duration: TimeInterval
    private let sourceBundleIdentifier: String?
    private let stopFileURL: URL?
    private let writer: AVAssetWriter
    private let audioInput: AVAssetWriterInput
    private var stream: SCStream?
    private var didStartSession = false
    private var firstTimestamp: CMTime?
    private var lastTimestamp: CMTime?
    private var captureError: Error?

    init(
        outputURL: URL,
        duration: TimeInterval,
        sourceBundleIdentifier: String?,
        stopFileURL: URL?
    ) throws {
        self.outputURL = outputURL
        self.duration = duration
        self.sourceBundleIdentifier = sourceBundleIdentifier
        self.stopFileURL = stopFileURL
        try? FileManager.default.removeItem(at: outputURL)
        writer = try AVAssetWriter(outputURL: outputURL, fileType: .m4a)
        audioInput = AVAssetWriterInput(
            mediaType: .audio,
            outputSettings: [
                AVFormatIDKey: kAudioFormatMPEG4AAC,
                AVSampleRateKey: 48_000,
                AVNumberOfChannelsKey: 2,
                AVEncoderBitRateKey: 256_000,
            ]
        )
        audioInput.expectsMediaDataInRealTime = true
        guard writer.canAdd(audioInput) else { throw CaptureError.cannotAddInput }
        writer.add(audioInput)
        super.init()
    }

    func record() async throws {
        let content = try await SCShareableContent.excludingDesktopWindows(
            false,
            onScreenWindowsOnly: true
        )
        guard let display = content.displays.first else { throw CaptureError.noDisplay }

        let filter: SCContentFilter
        if let sourceBundleIdentifier {
            guard let application = content.applications.first(where: {
                $0.bundleIdentifier == sourceBundleIdentifier
            }) else {
                throw CaptureError.writerFailed(
                    "application is not running: \(sourceBundleIdentifier)"
                )
            }
            filter = SCContentFilter(
                display: display,
                including: [application],
                exceptingWindows: []
            )
        } else {
            filter = SCContentFilter(
                display: display,
                excludingApplications: [],
                exceptingWindows: []
            )
        }
        let configuration = SCStreamConfiguration()
        configuration.width = 2
        configuration.height = 2
        configuration.minimumFrameInterval = CMTime(value: 1, timescale: 1)
        configuration.queueDepth = 3
        configuration.capturesAudio = true
        configuration.excludesCurrentProcessAudio = true
        configuration.sampleRate = 48_000
        configuration.channelCount = 2

        guard writer.startWriting() else {
            throw CaptureError.writerFailed(writer.error?.localizedDescription ?? "unknown error")
        }

        let stream = SCStream(filter: filter, configuration: configuration, delegate: self)
        self.stream = stream
        let queue = DispatchQueue(label: "vn.edu.uit.feenberg.system-audio")
        try stream.addStreamOutput(self, type: .audio, sampleHandlerQueue: queue)
        try await stream.startCapture()

        let startedAt = ContinuousClock.now
        while startedAt.duration(to: .now) < .seconds(duration) {
            if let stopFileURL, FileManager.default.fileExists(atPath: stopFileURL.path) {
                break
            }
            try await Task.sleep(for: .milliseconds(100))
        }
        try await stream.stopCapture()
        audioInput.markAsFinished()
        await writer.finishWriting()

        if let captureError { throw captureError }
        guard didStartSession, writer.status == .completed else {
            throw CaptureError.writerFailed(
                writer.error?.localizedDescription ?? "no system-audio samples were captured"
            )
        }
        if let firstTimestamp, let lastTimestamp {
            let captured = CMTimeGetSeconds(lastTimestamp - firstTimestamp)
            print(String(format: "captured_seconds=%.3f", captured))
        }
        print("output=\(outputURL.path)")
    }

    func stream(
        _ stream: SCStream,
        didOutputSampleBuffer sampleBuffer: CMSampleBuffer,
        of outputType: SCStreamOutputType
    ) {
        guard outputType == .audio, sampleBuffer.isValid, sampleBuffer.numSamples > 0 else {
            return
        }
        let timestamp = sampleBuffer.presentationTimeStamp
        if !didStartSession {
            writer.startSession(atSourceTime: timestamp)
            firstTimestamp = timestamp
            didStartSession = true
        }
        lastTimestamp = timestamp
        if audioInput.isReadyForMoreMediaData, !audioInput.append(sampleBuffer) {
            captureError = writer.error ?? CaptureError.writerFailed("append failed")
        }
    }

    func stream(_ stream: SCStream, didStopWithError error: Error) {
        captureError = error
    }
}

@main
struct CaptureSystemAudio {
    static func main() async {
        do {
            let arguments = CommandLine.arguments
            guard arguments.count >= 3,
                  let duration = TimeInterval(arguments[2]),
                  duration > 0
            else {
                fputs(
                    "Usage: capture_system_audio.swift OUTPUT.m4a DURATION_SECONDS " +
                    "[SOURCE_BUNDLE_ID|-] [STOP_FILE|-]\n",
                    stderr
                )
                exit(2)
            }
            let outputURL = URL(fileURLWithPath: arguments[1]).standardizedFileURL
            let sourceBundleIdentifier = arguments.count >= 4 && arguments[3] != "-"
                ? arguments[3]
                : nil
            let stopFileURL = arguments.count >= 5 && arguments[4] != "-"
                ? URL(fileURLWithPath: arguments[4]).standardizedFileURL
                : nil
            if let stopFileURL {
                try? FileManager.default.removeItem(at: stopFileURL)
            }
            let recorder = try SystemAudioRecorder(
                outputURL: outputURL,
                duration: duration,
                sourceBundleIdentifier: sourceBundleIdentifier,
                stopFileURL: stopFileURL
            )
            try await recorder.record()
        } catch {
            fputs("\(error)\n", stderr)
            exit(1)
        }
    }
}
