import { chromium } from 'playwright';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { spawn } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DOC_ROOT = join(__dirname, 'docs');

// Start a short-lived local HTTP server on a random port.
// All img srcs use relative paths like /docs/harness-first-agentic-ai/figures/…
// which resolve correctly when the server root is the docs/ directory.
function startServer(port) {
  return new Promise((resolve, reject) => {
    const proc = spawn('python3', ['-m', 'http.server', String(port)], {
      cwd: DOC_ROOT, stdio: 'pipe', detached: false
    });
    proc.on('error', reject);
    // Wait until the server is ready (listens on the port)
    const timeout = setTimeout(() => reject(new Error('server start timeout')), 5000);
    proc.stdout.on('data', (d) => {
      if (d.toString().includes('Listening') || d.toString().includes('Serving')) {
        clearTimeout(timeout);
        resolve(proc);
      }
    });
    // Also succeed on first stdout if we missed the log line
    proc.stdout.once('data', () => { clearTimeout(timeout); resolve(proc); });
    proc.stderr.pipe(process.stderr);
  });
}

const PORT = 8889;  // non-conflicting local port
const proc = await startServer(PORT);
let browser, page;

try {
  browser = await chromium.launch();
  page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  
  // Load the index page via HTTP so relative asset paths resolve.
  await page.goto(`http://127.0.0.1:${PORT}/`, { waitUntil: 'networkidle', timeout: 30000 });
  
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
    headerTemplate: `<div style="font-size:7.5pt; font-family:Georgia; text-align:right; width:100%; padding-right:16px; color:#444;">Harness-First Agentic AI — AAIAAS.ai Whitepaper v1.3</div>`,
    footerTemplate: `<div style="font-size:7.5pt; font-family:Georgia; text-align:center; width:100%; color:#444;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>`
  });
  console.log(`PDF written to ${pdfPath}`);
} finally {
  if (browser) await browser.close();
  proc.kill();
}
