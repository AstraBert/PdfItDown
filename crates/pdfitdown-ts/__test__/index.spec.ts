import test from 'ava'

import { PdfItDownConverter } from '../index'
import fs from 'fs'

function cleanupFile(path: string) {
  fs.unlinkSync(path)
}

function isPdf(file: string | Buffer): boolean {
  let fd: Buffer
  if (typeof file === 'string') {
    fd = fs.readFileSync(file)
  } else {
    fd = file
  } // or read just the first 4 bytes with a file handle
  return (
    fd[0] === 0x25 && // %
    fd[1] === 0x50 && // P
    fd[2] === 0x44 && // D
    fd[3] === 0x46 // F
  )
}

test('test conversion from DOCX', (t) => {
  const inputFile = './data/office1.docx'
  const outputFile = './data/office1.pdf'
  const converter = new PdfItDownConverter()
  converter.convertFile(inputFile, outputFile, true)
  t.true(fs.existsSync(outputFile))
  t.true(isPdf(outputFile))

  cleanupFile(outputFile)
})

test('test conversion from PPTX', (t) => {
  const inputFile = './data/office2.pptx'
  const outputFile = './data/office2.pdf'
  const converter = new PdfItDownConverter()
  converter.convertFile(inputFile, outputFile, true)
  t.true(fs.existsSync(outputFile))
  t.true(isPdf(outputFile))

  cleanupFile(outputFile)
})

test('test conversion from XLSX', (t) => {
  const inputFile = './data/office3.xlsx'
  const outputFile = './data/office3.pdf'
  const converter = new PdfItDownConverter()
  converter.convertFile(inputFile, outputFile, true)
  t.true(fs.existsSync(outputFile))
  t.true(isPdf(outputFile))

  cleanupFile(outputFile)
})

test('test conversion from HTML', (t) => {
  const inputFile = './data/markup1.html'
  const outputFile = './data/markup1.pdf'
  const converter = new PdfItDownConverter()
  converter.convertFile(inputFile, outputFile, true)
  t.true(fs.existsSync(outputFile))
  t.true(isPdf(outputFile))

  cleanupFile(outputFile)
})

test('test conversion from Markdown', (t) => {
  const inputFile = './data/markup2.md'
  const outputFile = './data/markup2.pdf'
  const converter = new PdfItDownConverter()
  converter.convertFile(inputFile, outputFile, true)
  t.true(fs.existsSync(outputFile))
  t.true(isPdf(outputFile))

  cleanupFile(outputFile)
})

test('test conversion from image', (t) => {
  const inputFile = './data/image.webp'
  const outputFile = './data/image.pdf'
  const converter = new PdfItDownConverter()
  converter.convertFile(inputFile, outputFile, true)
  t.true(fs.existsSync(outputFile))
  t.true(isPdf(outputFile))

  cleanupFile(outputFile)
})

test('test conversion from text', (t) => {
  const inputFile = './data/text.txt'
  const outputFile = './data/text.pdf'
  const converter = new PdfItDownConverter()
  converter.convertFile(inputFile, outputFile, true)
  t.true(fs.existsSync(outputFile))
  t.true(isPdf(outputFile))

  cleanupFile(outputFile)
})

test('test convert multiple files', (t) => {
  const inputFiles = ['./data/text.txt', './data/image.webp', './data/office1.docx', './data/markup2.md']
  const outputFiles = ['./data/text.pdf', './data/image.pdf', './data/office1.pdf', './data/markup2.pdf']
  const converter = new PdfItDownConverter()
  converter.convertMultipleFiles(inputFiles, outputFiles, true)
  for (const outputFile of outputFiles) {
    t.true(fs.existsSync(outputFile))
    t.true(isPdf(outputFile))

    cleanupFile(outputFile)
  }
})

test('test convert directory', (t) => {
  const outputFiles = [
    './data/text.pdf',
    './data/image.pdf',
    './data/office1.pdf',
    './data/office2.pdf',
    './data/office3.pdf',
    './data/markup1.pdf',
    './data/markup2.pdf',
  ]
  const converter = new PdfItDownConverter()
  converter.convertDirectory('./data', true, true)
  for (const outputFile of outputFiles) {
    t.true(fs.existsSync(outputFile))
    t.true(isPdf(outputFile))

    cleanupFile(outputFile)
  }
})

test('test convert bytes office', (t) => {
  const bts = fs.readFileSync('./data/office1.docx')
  const converter = new PdfItDownConverter()
  const result = converter.convertBytes(bts)

  t.true(isPdf(result))
})

test('test convert bytes text', (t) => {
  const bts = fs.readFileSync('./data/text.txt')
  const converter = new PdfItDownConverter()
  const result = converter.convertBytes(bts)

  t.true(isPdf(result))
})

test('test convert bytes markup', (t) => {
  const bts = fs.readFileSync('./data/markup1.html')
  const converter = new PdfItDownConverter()
  const result = converter.convertBytes(bts)

  t.true(isPdf(result))
})

test('test convert bytes image', (t) => {
  const bts = fs.readFileSync('./data/image.webp')
  const converter = new PdfItDownConverter()
  const result = converter.convertBytes(bts)

  t.true(isPdf(result))
})
