import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DOC_PATH = join(__dirname, 'docs', 'harness-first-agentic-ai', 'index.html');

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });

try {
  // Use file:// protocol to avoid WSL localhost TCP issues
  const fileUrl = join('file://', __dirname, 'docs', 'harness-first-agentic-ai', 'index.html').replace(/\\/g, '/');
  await page.goto(fileUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  
  // Inject print-density styles via page.evaluate (runs in-page).
  await page.evaluate(() => {
    const style = document.createElement('style');
    style.id = 'print-density';
    style.innerHTML = `
      body { font-size: 10pt !important; line-height: 1.35 !important; }
      h1 { font-size: 18pt !important; margin: 0.4em 0 0.3em !important; }
      h2 { font-size: 13pt !important; margin: 0.8em 0 0.35em !important; page-break-after: avoid; }
      h3 { font-size: 11pt !important; margin: 0.6em 0 0.25em !important; page-break-after: avoid; }
      p, li { margin: 0.35em 0 !important; }
      #content { max-width: 100% !important; }
      nav, .toc { font-size: 9.5pt !important; }
      table { font-size: 9pt !important; }
    `;
    document.head.appendChild(style);
  });

  const pdfPath = join(__dirname, 'harness-first-agentic-ai.pdf');
  await page.pdf({
    path: pdfPath,
    format: 'Letter',
    margin: { top: '0.7in', bottom: '0.7in', left: '0.85in', right: '0.85in' },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: `<div style="font-size:7.5pt; font-family:Georgia; text-align:right; width:100%; padding-right:16px; color:#444;">Harness-First Agentic AI — AAIAAS.ai Whitepaper v1.6.2</div>`,
    footerTemplate: `<div style="font-size:7pt; font-family:Georgia; text-align:center; width:100%; color:#666;"><span class="pageNumber"></span> of <span class="totalPages"></span> &nbsp; &bull; &nbsp; PEREGRINES™, AAIAAS™, and OGACS™ are trademarks of Peregrines AI, Inc. U.S. trademark applications pending. Serial nos. 50032311, 50032341, 50032358. All rights reserved.</div>`
  });
  console.log(`PDF written to ${pdfPath}`);
} finally {
  await browser.close();
}
