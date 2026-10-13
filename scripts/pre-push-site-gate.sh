#!/usr/bin/env bash
# CC3 87111 — block LOCAL PREVIEW index or missing /docs pages before push
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel)
fail=0
if git show :index.html 2>/dev/null | grep -q 'LOCAL PREVIEW'; then
  echo "PRE-PUSH GATE FAIL: index.html contains 'LOCAL PREVIEW'" >&2
  fail=1
fi
if [[ -f index.html ]] && grep -q 'LOCAL PREVIEW' index.html; then
  echo "PRE-PUSH GATE FAIL: working tree index.html contains 'LOCAL PREVIEW'" >&2
  fail=1
fi
# require docs pages for aaiaas.ai-docs shape
if [[ -f vercel.json ]] || [[ -d docs ]]; then
  if [[ ! -f docs/harness-first-agentic-ai/index.html && ! -f docs/harness-first-agentic-ai.pdf ]]; then
    # marketing may not have harness — only enforce if this looks like aaiaas docs
    if grep -q 'aaiaas\|harness-first' index.html 2>/dev/null; then
      echo "PRE-PUSH GATE FAIL: missing docs/harness-first-agentic-ai page/pdf" >&2
      fail=1
    fi
  fi
fi
if [[ $fail -ne 0 ]]; then exit 1; fi
echo "PRE-PUSH GATE OK"
