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
  importJson: document.querySelector("#importJson"),
  downloadJson: document.querySelector("#downloadJson"),
  reportFile: document.querySelector("#reportFile"),
  resultState: document.querySelector("#resultState"),
  summaryGrid: document.querySelector("#summaryGrid"),
  findingList: document.querySelector("#findingList"),
  textReport: document.querySelector("#textReport"),
  jsonPreview: document.querySelector("#jsonPreview"),
  connectionStatus: document.querySelector("#connectionStatus"),
  installButton: document.querySelector("#installButton"),
  appNotice: document.querySelector("#appNotice"),
  appNoticeTitle: document.querySelector("#appNoticeTitle"),
  appNoticeText: document.querySelector("#appNoticeText"),
  mobileGuideSummary: document.querySelector("#mobileGuideSummary"),
  mobileGuideBadge: document.querySelector("#mobileGuideBadge"),
  mobileGuideCommand: document.querySelector("#mobileGuideCommand"),
  mobileUrlList: document.querySelector("#mobileUrlList"),
  androidHint: document.querySelector("#androidHint"),
  iosHint: document.querySelector("#iosHint"),
  refreshPwaStatus: document.querySelector("#refreshPwaStatus"),
  copyPwaStatus: document.querySelector("#copyPwaStatus"),
  pwaModeValue: document.querySelector("#pwaModeValue"),
  pwaInstallValue: document.querySelector("#pwaInstallValue"),
  pwaWorkerValue: document.querySelector("#pwaWorkerValue"),
  pwaStorageValue: document.querySelector("#pwaStorageValue"),
  pwaViewportValue: document.querySelector("#pwaViewportValue"),
  pwaServerValue: document.querySelector("#pwaServerValue"),
  languageSelect: document.querySelector("#languageSelect"),
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
  ["definitions", "web_definitions"], ["imports", "web_imports"], ["unused_imports", "web_unused_imports"],
  ["unused_definitions", "web_unused_definitions"], ["missing_imports", "web_missing_imports"],
  ["missing_definitions", "web_missing_definitions"], ["duplicate_imports", "web_duplicate_imports"], ["todos", "web_todos"],
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

const STORAGE_KEYS = {
  draft: "methodenanalyser-webapp-draft-v1",
  report: "methodenanalyser-webapp-report-v1",
};

const EMPTY_TEXT_REPORT = "Noch keine Analyse gestartet.";
const EMPTY_JSON = "{}";

let sourceKind = "snippet";
let currentFileName = "<snippet>";
let currentZipBase64 = null;
let lastReport = null;
let lastReportMetadata = null;
let installPromptEvent = null;
let isRestoringDraft = false;
let runtimeInfo = null;
let latestPwaStatus = null;
let activeLanguage = localStorage.getItem("methodenanalyser-webapp-language") || "de";
let translations = {};

function t(key, fallback = key) {
  return translations[key] || fallback;
}

function applyTranslations() {
  if (document.documentElement) document.documentElement.lang = activeLanguage;
  document.title = t("web_title", "MethodenAnalyser Web Companion");
  const staticText = {
    ".brand p": "web_companion", "#inputTitle": "web_source", "#resultTitle": "web_result",
    "label[for='sourceCode']": "web_python_code", "#analyzeButton": "web_analyze",
    "#sampleButton": "web_load_example", "#clearButton": "web_clear", "#importJson": "web_load_json",
    "#downloadJson": "web_save_json", "#installButton": "web_install_app", "#snippetMode": "web_snippet",
    "#fileMode": "web_file", "#mobileGuideTitle": "web_mobile_test_path", "#pwaStatusTitle": "web_pwa_status",
    "#refreshPwaStatus": "web_refresh_status", "#copyPwaStatus": "web_copy_status",
  };
  Object.entries(staticText).forEach(([selector, key]) => {
    const element = document.querySelector(selector);
    if (element) element.textContent = t(key, element.textContent);
  });
}

async function loadTranslations(language = activeLanguage) {
  try {
    const response = await fetch(`/api/translations?lang=${encodeURIComponent(language)}`);
    const payload = await response.json();
    if (!response.ok || !payload.ok) throw new Error("translations");
    activeLanguage = payload.language;
    translations = payload.translations || {};
    localStorage.setItem("methodenanalyser-webapp-language", activeLanguage);
  } catch {
    activeLanguage = "de";
  }
  elements.languageSelect.value = activeLanguage;
  applyTranslations();
}

function isPlainObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

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

function setNotice(title, text, variant = "") {
  elements.appNotice.dataset.variant = variant;
  elements.appNoticeTitle.textContent = title;
  elements.appNoticeText.textContent = text;
}

async function copyText(value) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return true;
  }

  const helper = document.createElement("textarea");
  helper.value = value;
  helper.setAttribute("readonly", "readonly");
  helper.style.position = "absolute";
  helper.style.left = "-9999px";
  document.body.append(helper);
  helper.select();
  const copied = document.execCommand("copy");
  helper.remove();
  return copied;
}

function currentStandaloneMode() {
  return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

function formatBytes(value) {
  if (!Number.isFinite(value) || value < 0) {
    return "unbekannt";
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(0)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

async function collectPwaStatus() {
  const isStandalone = currentStandaloneMode();
  const draftSaved = Boolean(localStorage.getItem(STORAGE_KEYS.draft));
  const reportSaved = Boolean(localStorage.getItem(STORAGE_KEYS.report));

  let workerLabel = "Nicht unterstützt";
  if ("serviceWorker" in navigator) {
    try {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration) {
        workerLabel = navigator.serviceWorker.controller ? "Aktiv und steuert diese Seite" : "Registriert, wartet auf Übernahme";
      } else {
        workerLabel = "Noch nicht registriert";
      }
    } catch {
      workerLabel = "Status konnte nicht gelesen werden";
    }
  }

  let persistedLabel = `Entwurf: ${draftSaved ? "ja" : "nein"} · Report: ${reportSaved ? "ja" : "nein"}`;
  if (navigator.storage?.persisted) {
    try {
      const persisted = await navigator.storage.persisted();
      persistedLabel += persisted ? " · Persistenz erlaubt" : " · Persistenz offen";
    } catch {
      persistedLabel += " · Persistenz unbekannt";
    }
  }
  if (navigator.storage?.estimate) {
    try {
      const estimate = await navigator.storage.estimate();
      persistedLabel += ` · Nutzung ${formatBytes(estimate.usage ?? 0)} / ${formatBytes(estimate.quota ?? 0)}`;
    } catch {
      // Browser ohne verwertbare Speicherwerte ignorieren.
    }
  }

  const installLabel = installPromptEvent
    ? "Prompt verfügbar"
    : isStandalone
      ? "Bereits installiert"
      : "Noch kein Prompt";

  const serverValue = runtimeInfo?.local_only
    ? runtimeInfo.local_url || "Nur dieses Gerät"
    : Array.isArray(runtimeInfo?.candidate_urls) && runtimeInfo.candidate_urls.length > 0
      ? runtimeInfo.candidate_urls[0]
      : runtimeInfo?.local_url || "Wird lokal erkannt";

  return {
    mode: isStandalone ? "Standalone / Homescreen-App" : "Browser-Tab",
    install: installLabel,
    worker: workerLabel,
    storage: persistedLabel,
    viewport: `${window.innerWidth} × ${window.innerHeight} px @ ${window.devicePixelRatio || 1}x`,
    server: serverValue,
    online: navigator.onLine,
  };
}

function renderPwaStatus(status) {
  latestPwaStatus = status;
  elements.pwaModeValue.textContent = status.mode;
  elements.pwaInstallValue.textContent = status.install;
  elements.pwaWorkerValue.textContent = status.worker;
  elements.pwaStorageValue.textContent = status.storage;
  elements.pwaViewportValue.textContent = status.viewport;
  elements.pwaServerValue.textContent = status.server;
}

function buildPwaStatusSummary(status) {
  const onlineLabel = status.online ? "online" : "offline";
  return [
    "MethodenAnalyser Web Companion – PWA-Status",
    `App-Modus: ${status.mode}`,
    `Install-Flow: ${status.install}`,
    `Service Worker: ${status.worker}`,
    `Lokaler Speicher: ${status.storage}`,
    `Viewport: ${status.viewport}`,
    `Server: ${status.server}`,
    `Netzstatus: ${onlineLabel}`,
  ].join("\n");
}

async function refreshPwaStatus() {
  const status = await collectPwaStatus();
  renderPwaStatus(status);
}

async function copyPwaStatus() {
  if (!latestPwaStatus) {
    await refreshPwaStatus();
  }
  const copied = await copyText(buildPwaStatusSummary(latestPwaStatus));
  if (copied) {
    setNotice(
      "PWA-Status kopiert",
      "Die kompakte Testkarte liegt jetzt in der Zwischenablage und kann direkt in ein Testprotokoll eingefügt werden.",
      "ok",
    );
  }
}

function renderMobileGuide(info) {
  runtimeInfo = info;
  elements.mobileUrlList.replaceChildren();
  elements.mobileGuideCommand.innerHTML = `Für WLAN-Tests: <code>${info.mobile_command}</code>`;
  elements.androidHint.textContent = info.mobile_notes.android;
  elements.iosHint.textContent = info.mobile_notes.ios;

  if (info.local_only) {
    elements.mobileGuideBadge.textContent = "Nur lokal";
    elements.mobileGuideSummary.textContent = "Standardmäßig ist die PWA nur auf diesem Gerät erreichbar. Für Android/iOS im selben WLAN den Server mit 0.0.0.0 starten.";
    return;
  }

  elements.mobileGuideBadge.textContent = "WLAN bereit";
  elements.mobileGuideSummary.textContent = info.mobile_notes.network;

  if (!Array.isArray(info.candidate_urls) || info.candidate_urls.length === 0) {
    const note = document.createElement("p");
    note.className = "mobile-url-empty";
    note.textContent = "Keine LAN-Adressen erkannt. Du kannst stattdessen den manuellen Host oder Rechnernamen in derselben Port-Kombination verwenden.";
    elements.mobileUrlList.append(note);
    return;
  }

  for (const url of info.candidate_urls) {
    const item = document.createElement("div");
    item.className = "mobile-url-item";

    const link = document.createElement("a");
    link.href = url;
    link.textContent = url;
    link.target = "_blank";
    link.rel = "noreferrer";

    const copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className = "ghost-button mobile-copy-button";
    copyButton.textContent = "Kopieren";
    copyButton.addEventListener("click", async () => {
      const copied = await copyText(url);
      if (copied) {
        setNotice(
          "URL kopiert",
          "Die LAN-Adresse liegt jetzt in der Zwischenablage und kann an ein Mobilgerät geschickt werden.",
          "ok",
        );
      }
    });

    item.append(link, copyButton);
    elements.mobileUrlList.append(item);
  }
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
  elements.snippetMode.setAttribute("aria-pressed", nextMode === "snippet" ? "true" : "false");
  elements.fileMode.setAttribute("aria-pressed", nextMode === "file" ? "true" : "false");
  elements.zipMode.setAttribute("aria-pressed", nextMode === "zip" ? "true" : "false");

  if (nextMode === "snippet") {
    currentFileName = "<snippet>";
    currentZipBase64 = null;
    elements.fileName.textContent = "Keine Datei gewählt";
    elements.sourceFile.value = "";
  } else if (nextMode === "file") {
    if (!currentFileName.endsWith(".py")) {
      currentFileName = "upload.py";
    }
  } else if (!currentFileName.endsWith(".zip")) {
    currentFileName = "upload.zip";
  }

  syncInputUi();
  persistDraft();
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
    caption.textContent = t(label, label);
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

function reportHasFindings(report) {
  return collectFindings(report).length > 0;
}

function normalizeImportedReport(rawReport) {
  if (!isPlainObject(rawReport)) {
    throw new Error("Die JSON-Datei muss ein Objekt im Report-Format enthalten.");
  }
  if (rawReport.schema_version !== "methodenanalyser-report-v1") {
    throw new Error("Nur methodenanalyser-report-v1.json wird unterstützt.");
  }
  if (!["snippet", "file", "project", "zip"].includes(rawReport.source_kind)) {
    throw new Error("Der JSON-Report enthält keinen unterstützten source_kind.");
  }

  return {
    ...rawReport,
    files: Array.isArray(rawReport.files) ? rawReport.files : [],
    summary: isPlainObject(rawReport.summary) ? rawReport.summary : {},
    unused_imports: isPlainObject(rawReport.unused_imports) ? rawReport.unused_imports : {},
    unused_definitions: isPlainObject(rawReport.unused_definitions) ? rawReport.unused_definitions : {},
    missing_imports: isPlainObject(rawReport.missing_imports) ? rawReport.missing_imports : {},
    missing_definitions: isPlainObject(rawReport.missing_definitions) ? rawReport.missing_definitions : {},
    duplicate_imports: isPlainObject(rawReport.duplicate_imports) ? rawReport.duplicate_imports : {},
    errors: Array.isArray(rawReport.errors) ? rawReport.errors : [],
  };
}

function describeImportedReport(report, importedFileName) {
  const sourceLabelMap = {
    snippet: "Snippet",
    file: "Datei",
    project: "Projekt",
    zip: "ZIP-Projekt",
  };
  const sourceName = typeof report.source?.name === "string" && report.source.name
    ? report.source.name
    : importedFileName;
  const lines = [
    `Importierter JSON-Report: ${importedFileName}`,
    `Quelle: ${sourceLabelMap[report.source_kind] || report.source_kind} (${sourceName})`,
    `Schema: ${report.schema_version}`,
  ];

  if (typeof report.generated_at === "string" && report.generated_at) {
    lines.push(`Erzeugt am: ${report.generated_at}`);
  }
  if (report.source_kind === "project" || report.source_kind === "zip") {
    lines.push(`Dateien im Report: ${report.summary.files_analyzed ?? report.files.length ?? 0}`);
  }

  lines.push(
    "Der Textreport selbst wird nicht im JSON gespeichert. Für eine frische Textansicht den lokalen Python-Server erneut nutzen."
  );
  return lines.join("\n");
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
  lastReportMetadata = { origin: "analyzed" };
  renderSummary(payload.report.summary, payload.report);
  renderFindings(payload.report);
  elements.textReport.textContent = payload.text_report;
  elements.jsonPreview.textContent = JSON.stringify(payload.report, null, 2);
  elements.downloadJson.disabled = false;
  setState(payload.has_findings ? "Findings" : "Sauber", payload.has_findings ? "state-warning" : "state-ok");
  persistReport();
}

function renderImportedReport(report, importedFileName) {
  lastReport = report;
  lastReportMetadata = { origin: "imported", importedFileName };
  const hasFindings = reportHasFindings(report);
  renderSummary(report.summary, report);
  renderFindings(report);
  elements.textReport.textContent = describeImportedReport(report, importedFileName);
  elements.jsonPreview.textContent = JSON.stringify(report, null, 2);
  elements.downloadJson.disabled = false;
  setState(hasFindings ? "Report geladen" : "Report sauber", hasFindings ? "state-warning" : "state-ok");
  persistReport();
}

function renderError(message) {
  setState("Fehler", "state-error");
  elements.textReport.textContent = message;
  elements.jsonPreview.textContent = EMPTY_JSON;
  elements.downloadJson.disabled = !lastReport;
}

function persistDraft() {
  if (isRestoringDraft) {
    return;
  }

  const payload = {
    sourceKind,
    currentFileName,
    currentZipBase64,
    code: elements.sourceCode.value,
  };

  try {
    localStorage.setItem(STORAGE_KEYS.draft, JSON.stringify(payload));
    refreshPwaStatus();
  } catch {
    setNotice(
      "Browser-Speicher blockiert",
      "Entwürfe konnten nicht lokal gespeichert werden. Analysen funktionieren trotzdem.",
      "warning",
    );
  }
}

function persistReport() {
  if (!lastReport) {
    localStorage.removeItem(STORAGE_KEYS.report);
    refreshPwaStatus();
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEYS.report, JSON.stringify({
      report: lastReport,
      metadata: lastReportMetadata,
    }));
    refreshPwaStatus();
  } catch {
    setNotice(
      "Report nicht gespeichert",
      "Der letzte JSON-Report passt nicht mehr in den lokalen Browser-Speicher.",
      "warning",
    );
  }
}

function restoreDraft() {
  const raw = localStorage.getItem(STORAGE_KEYS.draft);
  if (!raw) {
    return;
  }

  try {
    const saved = JSON.parse(raw);
    isRestoringDraft = true;
    sourceKind = saved.sourceKind === "zip"
      ? "zip"
      : saved.sourceKind === "file"
        ? "file"
        : "snippet";
    currentFileName = typeof saved.currentFileName === "string" ? saved.currentFileName : "<snippet>";
    currentZipBase64 = typeof saved.currentZipBase64 === "string" ? saved.currentZipBase64 : null;
    elements.sourceCode.value = typeof saved.code === "string" ? saved.code : "";
    elements.fileName.textContent = currentZipBase64 ? currentFileName : "Zuletzt lokal geladen";
    setMode(sourceKind);
    setNotice(
      "Entwurf wiederhergestellt",
      "Die letzte Eingabe wurde lokal aus diesem Browser geladen.",
      "ok",
    );
  } catch {
    localStorage.removeItem(STORAGE_KEYS.draft);
  } finally {
    isRestoringDraft = false;
  }
}

function restoreLastReport() {
  const raw = localStorage.getItem(STORAGE_KEYS.report);
  if (!raw) {
    return;
  }

  try {
    const saved = JSON.parse(raw);
    const isPersistedEnvelope = isPlainObject(saved) && isPlainObject(saved.report);
    lastReport = isPersistedEnvelope ? saved.report : saved;
    lastReportMetadata = isPersistedEnvelope && isPlainObject(saved.metadata) ? saved.metadata : null;
    if (
      lastReportMetadata?.origin === "imported"
      && typeof lastReportMetadata.importedFileName === "string"
      && lastReportMetadata.importedFileName
    ) {
      renderImportedReport(lastReport, lastReportMetadata.importedFileName);
      return;
    }
    renderSummary(lastReport.summary, lastReport);
    renderFindings(lastReport);
    elements.jsonPreview.textContent = JSON.stringify(lastReport, null, 2);
    elements.downloadJson.disabled = false;
    if (elements.textReport.textContent === EMPTY_TEXT_REPORT) {
      elements.textReport.textContent = "Letzter JSON-Report lokal wiederhergestellt. Für einen frischen Textreport den Server erneut ansprechen.";
    }
  } catch {
    localStorage.removeItem(STORAGE_KEYS.report);
  }
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
      requestBody = {
        code: elements.sourceCode.value,
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
    setNotice(
      "Analyse lokal abgeschlossen",
      "Der aktuelle Entwurf und der letzte JSON-Report bleiben auf diesem Gerät gespeichert.",
      "ok",
    );
    await checkHealth();
  } catch (error) {
    renderError(error.message);
    elements.connectionStatus.textContent = "Server nicht erreichbar";
    setNotice(
      "Lokaler Server fehlt",
      "Die Oberfläche bleibt nutzbar, aber neue Analysen brauchen den laufenden Python-Server.",
      "warning",
    );
  } finally {
    elements.analyzeButton.disabled = false;
  }
}

async function loadReportFile(file) {
  if (!file) {
    return;
  }

  try {
    const rawText = await file.text();
    const parsed = JSON.parse(rawText);
    const report = normalizeImportedReport(parsed);
    renderImportedReport(report, file.name || "methodenanalyser-report-v1.json");
    setNotice(
      "JSON-Report geladen",
      "Der Report ist jetzt lokal im Browser verfügbar und kann mobil oder offline erneut betrachtet werden.",
      "ok",
    );
  } catch (error) {
    renderError(error instanceof Error ? error.message : "JSON-Report konnte nicht geladen werden.");
    setNotice(
      "JSON-Import fehlgeschlagen",
      "Bitte nur gültige methodenanalyser-report-v1.json-Dateien laden.",
      "warning",
    );
  } finally {
    elements.reportFile.value = "";
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
  persistDraft();
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error("offline");
    }
    elements.connectionStatus.textContent = navigator.onLine ? "Lokal bereit" : "Gerät offline";
  } catch {
    elements.connectionStatus.textContent = "Server offline";
  }
}

async function loadRuntimeInfo() {
  try {
    const response = await fetch("/api/runtime");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const payload = await response.json();
    if (!payload.ok || !payload.runtime) {
      throw new Error("runtime");
    }
    renderMobileGuide(payload.runtime);
    await refreshPwaStatus();
  } catch {
    renderMobileGuide({
      local_only: true,
      local_url: "http://127.0.0.1:8765/",
      mobile_command: "python webapp/server.py --host 0.0.0.0 --port 8765",
      candidate_urls: [],
      mobile_notes: {
        network: "Nur im vertrauenswürdigen WLAN testen: Der lokale HTTP-Server hat keine Authentifizierung und kein TLS. Browser-Analyse bleibt lokal ohne Cloud.",
        android: "Chrome oder Edge im selben WLAN öffnen und die URL bei Bedarf als App installieren.",
        ios: "Safari im selben WLAN öffnen und die Seite über Teilen zum Home-Bildschirm sichern.",
      },
    });
    runtimeInfo = {
      local_only: true,
      local_url: "http://127.0.0.1:8765/",
    };
    await refreshPwaStatus();
  }
}

function syncConnectivityLabel() {
  if (!navigator.onLine) {
    elements.connectionStatus.textContent = "Gerät offline";
    setNotice(
      "Offline-Modus",
      "Gespeicherte Entwürfe und der letzte JSON-Report bleiben verfügbar. Für neue Analysen muss das Gerät wieder online sein und der lokale Server laufen.",
      "warning",
    );
    return;
  }
  checkHealth();
}

function updateInstallUi() {
  const isStandalone = currentStandaloneMode();
  elements.installButton.hidden = !installPromptEvent || isStandalone;
  if (isStandalone) {
    setNotice(
      "App installiert",
      "Die PWA läuft als eigenständige App. Entwürfe und letzte Reports bleiben lokal im Browserprofil.",
      "ok",
    );
  }
  refreshPwaStatus();
}

async function installApp() {
  if (!installPromptEvent) {
    return;
  }

  installPromptEvent.prompt();
  try {
    await installPromptEvent.userChoice;
  } finally {
    installPromptEvent = null;
    updateInstallUi();
  }
}

function resetState() {
  currentFileName = "<snippet>";
  currentZipBase64 = null;
  lastReport = null;
  lastReportMetadata = null;
  elements.sourceCode.value = "";
  elements.sourceFile.value = "";
  elements.reportFile.value = "";
  elements.fileName.textContent = "Keine Datei gewählt";
  renderSummary();
  elements.findingList.replaceChildren();
  elements.textReport.textContent = EMPTY_TEXT_REPORT;
  elements.jsonPreview.textContent = EMPTY_JSON;
  elements.downloadJson.disabled = true;
  localStorage.removeItem(STORAGE_KEYS.draft);
  localStorage.removeItem(STORAGE_KEYS.report);
  refreshPwaStatus();
  setNotice(
    "Lokaler Entwurf aktiv",
    "Eingaben und der letzte JSON-Report bleiben nur in diesem Browser gespeichert.",
  );
  setState("Bereit");
  setMode("snippet");
}

elements.snippetMode.addEventListener("click", () => setMode("snippet"));
elements.fileMode.addEventListener("click", () => setMode("file"));
elements.zipMode.addEventListener("click", () => setMode("zip"));
elements.analyzeButton.addEventListener("click", analyzeCurrentSource);
elements.sampleButton.addEventListener("click", () => {
  elements.sourceCode.value = sampleCode;
  setMode("snippet");
  persistDraft();
});
elements.clearButton.addEventListener("click", resetState);
elements.importJson.addEventListener("click", () => {
  elements.reportFile.click();
});
elements.downloadJson.addEventListener("click", downloadCurrentJson);
elements.installButton.addEventListener("click", installApp);
elements.refreshPwaStatus.addEventListener("click", () => {
  refreshPwaStatus();
});
elements.copyPwaStatus.addEventListener("click", () => {
  copyPwaStatus();
});
elements.languageSelect.addEventListener("change", async (event) => {
  await loadTranslations(event.target.value);
  setMode(sourceKind);
  renderSummary(lastReport?.summary, lastReport);
});
elements.sourceFile.addEventListener("change", (event) => {
  loadSelectedFile(event.target.files?.[0]);
});
elements.reportFile.addEventListener("change", (event) => {
  loadReportFile(event.target.files?.[0]);
});
elements.sourceCode.addEventListener("input", persistDraft);

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  installPromptEvent = event;
  updateInstallUi();
});

window.addEventListener("appinstalled", () => {
  installPromptEvent = null;
  updateInstallUi();
});

window.addEventListener("online", syncConnectivityLabel);
window.addEventListener("offline", syncConnectivityLabel);
window.addEventListener("resize", () => {
  refreshPwaStatus();
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js").catch(() => {});
}

function initialize() {
  renderSummary();
  loadRuntimeInfo();
  restoreDraft();
  restoreLastReport();
  setMode(sourceKind);
  syncConnectivityLabel();
  updateInstallUi();
  refreshPwaStatus();
  loadTranslations().then(() => {
    setMode(sourceKind);
    renderSummary(lastReport?.summary, lastReport);
  });
}

initialize();
