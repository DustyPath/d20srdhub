import Foundation
import PDFKit

struct PageText: Codable {
    let page: Int
    let text: String
}

guard CommandLine.arguments.count == 2 else {
    FileHandle.standardError.write(
        Data("Usage: swift extract_pdf.swift /path/to/book.pdf\n".utf8)
    )
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1])

guard let document = PDFDocument(url: inputURL) else {
    FileHandle.standardError.write(
        Data("Could not open PDF: \(inputURL.path)\n".utf8)
    )
    exit(1)
}

var pages: [PageText] = []

for index in 0..<document.pageCount {
    pages.append(
        PageText(
            page: index + 1,
            text: document.page(at: index)?.string ?? ""
        )
    )
}

let encoder = JSONEncoder()
encoder.outputFormatting = [.withoutEscapingSlashes]
FileHandle.standardOutput.write(try encoder.encode(pages))
