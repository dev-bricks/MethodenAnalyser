"""Regression coverage for the local webapp report persistence contract."""

from __future__ import annotations

import subprocess
import textwrap
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


NODE_SCENARIO = r"""
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

class Element {
  constructor() {
    this.textContent = "";
    this.value = "";
    this.disabled = false;
    this.hidden = false;
    this.style = {};
    this.dataset = {};
    this.children = [];
    this.listeners = new Map();
    this.classList = { add() {}, remove() {}, toggle() {} };
  }
  addEventListener(name, callback) { this.listeners.set(name, callback); }
  setAttribute() {}
  append(...items) { this.children.push(...items); }
  appendChild(item) { this.children.push(item); return item; }
  replaceChildren(...items) { this.children = items; }
  remove() {}
  click() {}
}

function boot(storage) {
  const nodes = new Map();
  const node = (selector) => {
    if (!nodes.has(selector)) nodes.set(selector, new Element());
    return nodes.get(selector);
  };
  const localStorage = {
    getItem(key) { return Object.hasOwn(storage, key) ? storage[key] : null; },
    setItem(key, value) { storage[key] = String(value); },
    removeItem(key) { delete storage[key]; },
  };
  const context = {
    Blob,
    URL,
    console,
    document: {
      body: new Element(),
      createElement() { return new Element(); },
      querySelector: node,
    },
    fetch: async () => { throw new Error("offline"); },
    localStorage,
    navigator: { onLine: true, standalone: false },
    Promise,
    setTimeout,
    window: { addEventListener() {}, matchMedia() { return { matches: false }; }, navigator: { standalone: false } },
  };
  vm.createContext(context);
  const app = fs.readFileSync("webapp/static/app.js", "utf8");
  vm.runInContext(`${app}\nglobalThis.__test = { loadReportFile };`, context);
  return { context, node };
}

(async () => {
  const storage = {};
  const report = {
    schema_version: "methodenanalyser-report-v1",
    source_kind: "project",
    source: { name: "example-project" },
    summary: { files_analyzed: 1 },
    files: [],
    unused_imports: {}, unused_definitions: {}, missing_imports: {},
    missing_definitions: {}, duplicate_imports: {}, errors: [],
  };
  const firstSession = boot(storage);
  await firstSession.context.__test.loadReportFile({
    name: "shared-report.json",
    text: async () => JSON.stringify(report),
  });

  const restoredSession = boot(storage);
  assert.match(
    restoredSession.node("#textReport").textContent,
    /Importierter JSON-Report: shared-report\.json/,
  );
})().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
"""


class WebappReportPersistenceTests(unittest.TestCase):
    def test_imported_report_keeps_its_origin_after_local_restore(self) -> None:
        result = subprocess.run(
            ["node", "-e", textwrap.dedent(NODE_SCENARIO)],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
