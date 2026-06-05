import Foundation
import Vision
import AppKit

if CommandLine.arguments.count < 2 {
    fputs("usage: vision_ocr.swift image1 [image2 ...]\n", stderr)
    exit(1)
}

for imagePath in CommandLine.arguments.dropFirst() {
    guard let image = NSImage(contentsOfFile: imagePath),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("\(imagePath)\tERROR\tcould not load image")
        continue
    }

    let request = VNRecognizeTextRequest { request, error in
        if let error = error {
            print("\(imagePath)\tERROR\t\(error.localizedDescription)")
            return
        }
        let observations = request.results as? [VNRecognizedTextObservation] ?? []
        for observation in observations {
            guard let candidate = observation.topCandidates(1).first else { continue }
            let box = observation.boundingBox
            let text = candidate.string.replacingOccurrences(of: "\n", with: " ")
            print("\(URL(fileURLWithPath: imagePath).lastPathComponent)\t\(String(format: "%.3f", candidate.confidence))\t\(String(format: "%.3f", box.minX))\t\(String(format: "%.3f", box.minY))\t\(String(format: "%.3f", box.width))\t\(String(format: "%.3f", box.height))\t\(text)")
        }
    }

    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["it-IT", "en-US"]

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([request])
    } catch {
        print("\(imagePath)\tERROR\t\(error.localizedDescription)")
    }
}
