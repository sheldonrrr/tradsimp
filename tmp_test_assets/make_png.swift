import AppKit
import Foundation

let outPath = CommandLine.arguments[1]
let text = CommandLine.arguments[2]
let size = AppKit.NSSize(width: 1200, height: 300)
let image = AppKit.NSImage(size: size)
image.lockFocus()
AppKit.NSColor.white.setFill()
Foundation.NSRect(x: 0, y: 0, width: size.width, height: size.height).fill()
let paragraph = NSMutableParagraphStyle()
paragraph.alignment = .left
let attrs: [NSAttributedString.Key: Any] = [.font: AppKit.NSFont.systemFont(ofSize: 96), .foregroundColor: AppKit.NSColor.black, .paragraphStyle: paragraph]
let ns = NSString(string: text)
ns.draw(in: Foundation.NSRect(x: 40, y: 90, width: 1100, height: 180), withAttributes: attrs)
image.unlockFocus()
if let tiff = image.tiffRepresentation, let rep = AppKit.NSBitmapImageRep(data: tiff), let png = rep.representation(using: .png, properties: [:]) { try png.write(to: URL(fileURLWithPath: outPath)) }
