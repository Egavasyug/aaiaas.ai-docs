import { chromium } from 'playwright';
import { readFileSync } from 'fs';

const html = readFileSync('/home/aaiaas/aaiaas.ai-docs/index.html', 'utf-8');
const pdfPath = '/home/aaiaas/aaiaas.ai-docs/harness-first-agentic-ai.pdf';

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
const denser = html.replace(
  '</head>',
  `<style id="print-density">
    @media print, screen {
      body { font-size: 10pt !important; line-height: 1.35 !important; }
      h1 { font-size: 18pt !important; margin: 0.4em 0 0.3em !important; }
      h2 { font-size: 13pt !important; margin: 0.8em 0 0.35em !important; page-break-after: avoid; }
      h3 { font-size: 11pt !important; margin: 0.6em 0 0.25em !important; page-break-after: avoid; }
      p, li { margin: 0.35em 0 !important; }
      #content { max-width: 100% !important; }
      nav, .toc { font-size: 9.5pt !important; }
      table { font-size: 9pt !important; }
    }
  </style></head>`
);
await page.setContent(denser, { waitUntil: 'networkidle' });
const contentHeight = await page.evaluate(() => {
  const el = document.getElementById('content') || document.body;
  return el.scrollHeight;
});
console.log(`Content height: ${contentHeight}px`);
await page.pdf({
  path: pdfPath,
  format: 'Letter',
  margin: { top: '0.7in', bottom: '0.7in', left: '0.85in', right: '0.85in' },
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: `<div style="font-size:7.5pt; font-family:Georgia; text-align:right; width:100%; padding-right:16px; color:#444;">Harness-First Agentic AI — AAIAAS.ai Whitepaper v1.2</div>`,
  footerTemplate: `<div style="font-size:7.5pt; font-family:Georgia; text-align:center; width:100%; color:#444;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>`
});
await browser.close();
console.log(`PDF written to ${pdfPath}`);
