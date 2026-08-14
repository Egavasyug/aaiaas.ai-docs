from pypdf import PdfReader

pdf_path = "/home/aaiaas/aaiaas.ai-docs/harness-first-agentic-ai.pdf"
reader = PdfReader(pdf_path)
print(f"PDF pages: {len(reader.pages)}")
print(f"PDF format: {reader.pdf_format}")

# Extract first few pages to verify content
for i, page in enumerate(reader.pages[:3]):
    text = page.extract_text()
    print(f"\nPage {i+1} preview (first 200 chars):")
    if text:
        print(text[:200])
    else:
        print("(no text extracted)")
