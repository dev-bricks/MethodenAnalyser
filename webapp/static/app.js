const elements = {
  sourceCode: document.querySelector("#sourceCode"),
  sourceFile: document.querySelector("#sourceFile"),
  fileName: document.querySelector("#fileName"),
  sourceHint: document.querySelector("#sourceHint"),
  snippetMode: document.querySelector("#snippetMode"),
  fileMode: document.querySelector("#fileMode"),
  zipMode: document.querySelector("#zipMode"),
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

const singleFileMetricLabels = [
  ["definitions", "Definitionen"],
  ["imports", "Imports"],
  ["unused_imports", "Ungenutzte Imports"],
  ["unused_definitions", "Tote Definitionen"],
  ["missing_imports", "Fehlende Imports"],
  ["missing_definitions", "Fehlende Definitionen"],
  ["duplicate_imports", "Doppelte Imports"],
  ["todos", "TODOs"],
];

const projectMetricLabels = [
  ["files_analyzed", "Dateien"],
  ["files_with_errors", "Fehlerdateien"],
  ["total_lines", "Zeilen"],
  ["total_definitions", "Definitionen"],
  ["total_imports", "Imports"],
  ["unused_imports", "Ungenutzte Imports"],
  ["unused_definitions", "Tote Definitionen"],
  ["missing_imports", "Fehlende Imports"],
  ["missing_definitions", "Fehlende Definitionen"],
  ["duplicate_imports", "Doppelte Imports"],
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
let currentZipBase64 = null;
let lastReport = null;

function getMetricLabels(report = null) {
  if (report && ["project", "zip"].includes(report.source_kind)) {
    return projectMetricLabels;
  }
  return singleFileMetricLabels;
}

function zipPlaceholderText() {
  const archiveLabel = currentZipBase64
    ? `Archiv bereit: ${currentFileName}`
    : "Bitte ein kleines ZIP-Archiv mit Python-Dateien auswählen.";
  return [
    "# ZIP-Analyse aktiv",
    archiveLabel,
    "# Das Archiv wird lokal an den Python-Prozess geschickt, dort temporär entpackt und mit der bestehenden Projektanalyse geprüft.",
  ].join("\n");
}

function syncInputUi() {
  const isZip = sourceKind === "zip";
  elements.sourceCode.readOnly = isZip;
  elements.sourceCode.classList.toggle("is-readonly", isZip);
  elements.sourceFile.accept = isZip
    ? ".zip,application/zip,application/x-zip-compressed"
    : ".py,text/x-python,text/plain";

  if (sourceKind === "snippet") {
    elements.sourceHint.textContent = "Snippets direkt einfügen oder eine einzelne `.py`-Datei laden.";
  } else if (sourceKind === "file") {
    elements.sourceHint.textContent = "Eine einzelne Python-Datei wird direkt im Browser gelesen und lokal analysiert.";
  } else {
    elements.sourceHint.textContent = "Kleine ZIP-Archive mit `.py`-Dateien werden lokal an den Python-Prozess gesendet, dort temporär entpackt und als Mini-Projekt analysiert.";
    elements.sourceCode.value = zipPlaceholderText();
  }
}

function setMode(nextMode) {
  sourceKind = nextMode;
  elements.snippetMode.classList.toggle("active", nextMode === "snippet");
  elements.fileMode.classList.toggle("active", nextMode === "file");
  elements.zipMode.classList.toggle("active", nextMode === "zip");

  if (nextMode === "snippet") {
    currentFileName = "<snippet>";
    currentZipBase64 = null;
    elements.fileName.textContent = "Keine Datei gewählt";
    elements.sourceFile.value = "";
  } else if (nextMode === "file" && !currentFileName.endsWith(".py")) {
    currentFileName = "upload.py";
  } else if (nextMode === "zip" && !currentFileName.endsWith(".zip")) {
    currentFileName = "upload.zip";
  }

  syncInputUi();
}

function setState(label, variant = "") {
  elements.resultState.textContent = label;
  elements.resultState.classList.remove("state-error", "state-warning", "state-ok");
  if (variant) {
    elements.resultState.classList.add(variant);
  }
}

function renderSummary(summary = {}, report = null) {
  elements.summaryGrid.replaceChildren();
  for (const [key, label] of getMetricLabels(report)) {
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

  if (Array.isArray(report.errors) && report.errors.length > 0) {
    groups.push({
      label: "Dateifehler",
      items: report.errors.map((entry) => `${entry.path}: ${entry.message}`),
    });
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
  renderSummary(payload.report.summary, payload.report);
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
  elements.analyzeButton.disabled = true;
  elements.downloadJson.disabled = true;
  setState("Analysiert");

  try {
    let requestBody;
    if (sourceKind === "zip") {
      if (!currentZipBase64) {
        throw new Error("Bitte zuerst ein kleines ZIP-Archiv auswählen.");
      }
      requestBody = {
        source_kind: "zip",
        filename: currentFileName,
        zip_base64: currentZipBase64,
      };
    } else {
      const code = elements.sourceCode.value;
      requestBody = {
        code,
        source_kind: sourceKind,
        filename: currentFileName,
      };
    }

    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
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

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(new Error("Datei konnte nicht gelesen werden."));
    reader.readAsDataURL(file);
  });
}

async function loadSelectedFile(file) {
  if (!file) {
    return;
  }

  const lowerName = (file.name || "").toLowerCase();
  if (lowerName.endsWith(".zip")) {
    currentFileName = file.name || "upload.zip";
    currentZipBase64 = await readFileAsDataUrl(file);
    elements.fileName.textContent = currentFileName;
    setMode("zip");
    return;
  }

  currentZipBase64 = null;
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
elements.zipMode.addEventListener("click", () => setMode("zip"));
elements.analyzeButton.addEventListener("click", analyzeCurrentSource);
elements.sampleButton.addEventListener("click", () => {
  elements.sourceCode.value = sampleCode;
  setMode("snippet");
});
elements.clearButton.addEventListener("click", () => {
  currentFileName = "<snippet>";
  currentZipBase64 = null;
  lastReport = null;
  elements.sourceCode.value = "";
  elements.sourceFile.value = "";
  elements.fileName.textContent = "Keine Datei gewählt";
  renderSummary();
  elements.findingList.replaceChildren();
  elements.textReport.textContent = "Noch keine Analyse gestartet.";
  elements.jsonPreview.textContent = "{}";
  elements.downloadJson.disabled = true;
  setState("Bereit");
  setMode("snippet");
});
elements.downloadJson.addEventListener("click", downloadCurrentJson);
elements.sourceFile.addEventListener("change", (event) => {
  loadSelectedFile(event.target.files?.[0]);
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js").catch(() => {});
}

setMode("snippet");
renderSummary();
checkHealth();
