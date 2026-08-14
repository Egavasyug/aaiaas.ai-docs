from weasyprint import HTML
from pathlib import Path

html_path = Path('/home/aaiaas/aaiaas.ai-docs/index.html')
pdf_path = Path('/home/aaiaas/aaiaas.ai-docs/harness-first-agentic-ai.pdf')

# Use the HTML as-is; CSS @page header/footer are defined in the HTML
print(f"Reading HTML: {html_path}")
print(f"Output PDF: {pdf_path}")

try:
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    print(f"PDF written successfully: {pdf_path}")
    print(f"PDF size: {pdf_path.stat().st_size} bytes")
except Exception as e:
    print(f"Error: {e}")
    raise
