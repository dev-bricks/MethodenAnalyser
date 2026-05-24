const elements = {
  sourceCode: document.querySelector("#sourceCode"),
  sourceFile: document.querySelector("#sourceFile"),
  fileName: document.querySelector("#fileName"),
  snippetMode: document.querySelector("#snippetMode"),
  fileMode: document.querySelector("#fileMode"),
  analyzeButton: document.querySelector("#analyzeButton"),
  sampleButton: document.querySelector("#sampleButton"),
  clearButton: document.querySelector("#clearButton"),
  downloadJson: document.querySelector("#downloadJson"),
  resultState: document.querySelector("#resultState"),
  summaryGrid: document.querySelector("#summaryGrid"),
  findingList: document.querySelector("#findingList"),
  textReport: document.querySelector("#textReport"),
  jsonPreview: document.querySelector("#jsonPreview"),
  connectionStatus: document.querySelector("#connectionStatus"),
};

const sampleCode = `import os
import math

def area(radius):
    return math.pi * radius * radius

def old_helper():
    return os.getcwd()

print(area(3))
`;

const metricLabels = [
  ["definitions", "Definitionen"],
  ["imports", "Imports"],
  ["unused_imports", "Ungenutzte Imports"],
  ["unused_definitions", "Tote Definitionen"],
  ["missing_imports", "Fehlende Imports"],
  ["missing_definitions", "Fehlende Definitionen"],
  ["duplicate_imports", "Doppelte Imports"],
  ["todos", "TODOs"],
];

const findingLabels = [
  ["unused_imports", "Ungenutzte Imports"],
  ["unused_definitions", "Tote Definitionen"],
  ["missing_imports", "Fehlende Imports"],
  ["missing_definitions", "Fehlende Definitionen"],
  ["duplicate_imports", "Doppelte Imports"],
];

let sourceKind = "snippet";
let currentFileName = "<snippet>";
let lastReport = null;

function setMode(nextMode) {
  sourceKind = nextMode;
  elements.snippetMode.classList.toggle("active", nextMode === "snippet");
  elements.fileMode.classList.toggle("active", nextMode === "file");
  if (nextMode === "snippet") {
    currentFileName = "<snippet>";
    elements.fileName.textContent = "Keine Datei gewählt";
  }
}

function setState(label, variant = "") {
  elements.resultState.textContent = label;
  elements.resultState.classList.remove("state-error", "state-warning", "state-ok");
  if (variant) {
    elements.resultState.classList.add(variant);
  }
}

function renderSummary(summary = {}) {
  elements.summaryGrid.replaceChildren();
  for (const [key, label] of metricLabels) {
    const metric = document.createElement("div");
    metric.className = "metric";
    const caption = document.createElement("span");
    caption.textContent = label;
    const value = document.createElement("strong");
    value.textContent = String(summary[key] ?? 0);
    metric.append(caption, value);
    elements.summaryGrid.append(metric);
  }
}

function collectFindings(report) {
  const groups = [];
  for (const [key, label] of findingLabels) {
    const byFile = report[key] || {};
    const items = [];
    for (const [file, values] of Object.entries(byFile)) {
      for (const value of values || []) {
        items.push(`${file}: ${value}`);
      }
    }
    if (items.length > 0) {
      groups.push({ label, items });
    }
  }
  return groups;
}

function renderFindings(report) {
  elements.findingList.replaceChildren();
  const groups = collectFindings(report);
  if (groups.length === 0) {
    const empty = document.createElement("div");
    empty.className = "finding-empty";
    empty.textContent = "Keine Findings im aktuellen Report.";
    elements.findingList.append(empty);
    return;
  }

  for (const group of groups) {
    const section = document.createElement("section");
    section.className = "finding-group";
    const title = document.createElement("h3");
    title.textContent = group.label;
    const list = document.createElement("ul");
    for (const item of group.items) {
      const li = document.createElement("li");
      li.textContent = item;
      list.append(li);
    }
    section.append(title, list);
    elements.findingList.append(section);
  }
}

function renderResult(payload) {
  lastReport = payload.report;
  renderSummary(payload.report.summary);
  renderFindings(payload.report);
  elements.textReport.textContent = payload.text_report;
  elements.jsonPreview.textContent = JSON.stringify(payload.report, null, 2);
  elements.downloadJson.disabled = false;
  setState(payload.has_findings ? "Findings" : "Sauber", payload.has_findings ? "state-warning" : "state-ok");
}

function renderError(message) {
  setState("Fehler", "state-error");
  elements.textReport.textContent = message;
  elements.jsonPreview.textContent = "{}";
  elements.downloadJson.disabled = true;
}

async function analyzeCurrentSource() {
  const code = elements.sourceCode.value;
  elements.analyzeButton.disabled = true;
  elements.downloadJson.disabled = true;
  setState("Analysiert");

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code,
        source_kind: sourceKind,
        filename: currentFileName,
      }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || `HTTP ${response.status}`);
    }
    renderResult(payload);
  } catch (error) {
    renderError(error.message);
  } finally {
    elements.analyzeButton.disabled = false;
  }
}

function downloadCurrentJson() {
  if (!lastReport) {
    return;
  }
  const blob = new Blob([`${JSON.stringify(lastReport, null, 2)}\n`], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "methodenanalyser-report-v1.json";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function loadSelectedFile(file) {
  if (!file) {
    return;
  }
  currentFileName = file.name || "upload.py";
  elements.fileName.textContent = currentFileName;
  elements.sourceCode.value = await file.text();
  setMode("file");
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error("offline");
    }
    elements.connectionStatus.textContent = "Lokal";
  } catch {
    elements.connectionStatus.textContent = "Offline";
  }
}

elements.snippetMode.addEventListener("click", () => setMode("snippet"));
elements.fileMode.addEventListener("click", () => setMode("file"));
elements.analyzeButton.addEventListener("click", analyzeCurrentSource);
elements.sampleButton.addEventListener("click", () => {
  elements.sourceCode.value = sampleCode;
  setMode("snippet");
});
elements.clearButton.addEventListener("click", () => {
  elements.sourceCode.value = "";
  lastReport = null;
  renderSummary();
  elements.findingList.replaceChildren();
  elements.textReport.textContent = "Noch keine Analyse gestartet.";
  elements.jsonPreview.textContent = "{}";
  elements.downloadJson.disabled = true;
  setState("Bereit");
});
elements.downloadJson.addEventListener("click", downloadCurrentJson);
elements.sourceFile.addEventListener("change", (event) => {
  loadSelectedFile(event.target.files?.[0]);
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js").catch(() => {});
}

renderSummary();
checkHealth();
