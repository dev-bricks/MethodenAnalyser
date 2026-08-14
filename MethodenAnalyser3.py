import argparse
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import ast
import re
import os
import sys
import pathlib
import pkgutil
import builtins
import collections
import difflib
import datetime
import sqlite3
import threading
import warnings
import importlib
from typing import Set, Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from functools import lru_cache

try:
    from translator import TranslationSystem
except Exception:  # pragma: no cover - Übersetzung ist optional
    TranslationSystem = None

# ============================================================================
# KONSTANTEN
# ============================================================================

# GUI Konfiguration
WINDOW_GEOMETRY = "1200x700"

# Globale Variablen für Auto-Fix
_last_analysis_path: str = ""
_last_analysis_result: 'AnalysisResult' = None
OUTPUT_WIDTH = 140
OUTPUT_HEIGHT = 40
OUTPUT_FONT = ("Courier", 9)
APP_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MethodenAnalyser.ico")
TOOL_VERSION = "3.0"
JSON_SCHEMA_VERSION = "methodenanalyser-report-v1"
DEFAULT_JSON_REPORT_NAME = f"{JSON_SCHEMA_VERSION}.json"

# CLI Exit-Codes
EXIT_OK = 0
EXIT_ANALYSIS_ERROR = 1
EXIT_FINDINGS = 2
EXIT_PARTIAL_ERROR = 3

# ============================================================================
# SPRACHE / KONFIGURATION (Welle-1 U1: sichtbarer DE/EN-Sprachschalter)
# ============================================================================

SUPPORTED_LANGUAGES = ("de", "en")
DEFAULT_LANGUAGE = "de"

# Erste Zeile der Willkommensnachricht je Sprache (fuer Live-Neurendern beim Sprachwechsel)
_WELCOME_HEADS = (
    "Willkommen beim Python Code Analyzer!",
    "Welcome to Python Code Analyzer!",
)


def _config_dir() -> pathlib.Path:
    """Per-User-Konfigverzeichnis (auch bei read-only Store-Installation schreibbar)."""
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
            os.path.expanduser("~"), ".config"
        )
    return pathlib.Path(base) / "MethodenAnalyser"


def _config_path() -> pathlib.Path:
    return _config_dir() / "config.json"


def load_app_config() -> Dict[str, Any]:
    """Liest die persistente App-Konfiguration (leer bei Fehlen/Korruption)."""
    try:
        with open(_config_path(), "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_app_config(config: Dict[str, Any]) -> bool:
    """Speichert die App-Konfiguration; True bei Erfolg."""
    try:
        _config_dir().mkdir(parents=True, exist_ok=True)
        with open(_config_path(), "w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


def get_saved_language() -> str:
    """Gespeicherte Sprache oder Default, validiert gegen SUPPORTED_LANGUAGES."""
    lang = load_app_config().get("language", DEFAULT_LANGUAGE)
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def set_saved_language(lang: str) -> bool:
    """Persistiert die gewaehlte Sprache in der App-Konfiguration."""
    if lang not in SUPPORTED_LANGUAGES:
        return False
    config = load_app_config()
    config["language"] = lang
    return save_app_config(config)


_TRANSLATOR = None


def get_translator():
    """Lazy-Singleton des TranslationSystem, mit gespeicherter Sprache initialisiert."""
    global _TRANSLATOR
    if _TRANSLATOR is None and TranslationSystem is not None:
        _TRANSLATOR = TranslationSystem(get_saved_language())
    return _TRANSLATOR


def _t(key: str) -> str:
    """Übersetzt key in die aktuelle Sprache (Fallback: key selbst)."""
    translator = get_translator()
    return translator.t(key) if translator is not None else key


# Analyse Konfiguration
SIMILARITY_THRESHOLD = 0.8

# Builtin Namen
BUILTINS = set(dir(builtins))

# Callback und Handler Suffixe
CALLBACK_SUFFIXES = (
    "_callback", "_fetch", "_stage", "_emit", "_process", "_task", "_async", "_handler"
)

# Framework-spezifische Methoden
COMMON_FRAMEWORK_METHODS = {
    "__enter__", "__exit__", "__eq__", "__hash__", "__init__",
    "__str__", "__repr__", "__len__", "__getitem__", "__setitem__",
    "on_start", "on_stop", "on_close", "on_refresh", "mainloop"
}

# Gängige GUI-Widgets
COMMON_WIDGETS = {
    "Button", "Label", "Frame", "Canvas", "Entry", "Text", "Scrollbar", "Treeview",
    "Menu", "MenuItem", "Checkbutton", "Radiobutton", "Scale", "Spinbox",
    "BooleanVar", "StringVar", "IntVar", "DoubleVar", "Listbox", "Combobox"
}

# Framework-Methoden Zuordnung
FRAMEWORK_MAP = {
    "LabelFrame": "tkinter", "Progressbar": "tkinter", "after": "tkinter",
    "after_idle": "tkinter", "grid": "tkinter", "pack": "tkinter",
    "rowconfigure": "tkinter", "columnconfigure": "tkinter",
    "update_idletasks": "tkinter", "update_menu": "tkinter", "winfo_children": "tkinter",
    "askopenfilename": "tkinter", "asksaveasfilename": "tkinter", "askyesno": "tkinter",
    "showerror": "tkinter", "showinfo": "tkinter", "showwarning": "tkinter",
    "tag_configure": "tkinter", "tag_add": "tkinter", "tag_remove": "tkinter",
    "ClientSession": "aiohttp", "ClientTimeout": "aiohttp",
    "Session": "requests", "HTTPAdapter": "requests", "raise_for_status": "requests",
    "Workbook": "openpyxl", "cell": "openpyxl", "load_workbook": "openpyxl",
    "Image": "PIL", "ImageDraw": "PIL", "Icon": "PIL", "Draw": "PIL",
    "drawString": "reportlab", "showPage": "reportlab", "setFont": "reportlab",
}

# Modul-zu-Attribut Mapping für Standard Library und häufige Third-Party
# Format: "modul": {"attribut1", "attribut2", ...}
STDLIB_EXPORTS = {
    # threading
    "threading": {
        "Thread", "Lock", "RLock", "Event", "Semaphore", "BoundedSemaphore",
        "Condition", "Timer", "Barrier", "current_thread", "active_count",
        "enumerate", "main_thread", "get_ident", "get_native_id"
    },
    # subprocess
    "subprocess": {
        "Popen", "PIPE", "STDOUT", "DEVNULL", "run", "call", "check_call",
        "check_output", "CompletedProcess", "CalledProcessError", "TimeoutExpired"
    },
    # io
    "io": {
        "BytesIO", "StringIO", "BufferedReader", "BufferedWriter", "TextIOWrapper",
        "BufferedRandom", "FileIO", "open", "SEEK_SET", "SEEK_CUR", "SEEK_END"
    },
    # gzip
    "gzip": {
        "GzipFile", "open", "compress", "decompress", "BadGzipFile"
    },
    # asyncio
    "asyncio": {
        "get_event_loop", "get_running_loop", "new_event_loop", "set_event_loop",
        "run", "create_task", "gather", "wait", "sleep", "timeout", "Queue",
        "Event", "Lock", "Semaphore", "run_coroutine_threadsafe", "run_until_complete"
    },
    # collections
    "collections": {
        "Counter", "OrderedDict", "defaultdict", "deque", "namedtuple",
        "ChainMap", "UserDict", "UserList", "UserString"
    },
    # concurrent.futures
    "concurrent": {
        "ThreadPoolExecutor", "ProcessPoolExecutor", "Future", "as_completed",
        "wait", "FIRST_COMPLETED", "ALL_COMPLETED", "Executor"
    },
    # traceback
    "traceback": {
        "format_exc", "format_exception", "print_exc", "print_exception",
        "extract_tb", "format_tb", "print_tb", "TracebackException"
    },
    # psutil
    "psutil": {
        "cpu_percent", "cpu_count", "virtual_memory", "swap_memory",
        "disk_usage", "disk_partitions", "net_io_counters", "Process",
        "pid_exists", "process_iter", "wait_procs", "NoSuchProcess"
    },
    # tkinter (Attribut-Zugriffe)
    "tkinter": {
        "Tk", "Frame", "Label", "Button", "Entry", "Text", "Canvas", "Scrollbar",
        "Menu", "Toplevel", "Listbox", "Checkbutton", "Radiobutton", "Scale",
        "Spinbox", "LabelFrame", "PanedWindow", "messagebox", "filedialog",
        "StringVar", "IntVar", "DoubleVar", "BooleanVar", "PhotoImage",
        # Methoden die oft via obj.method() aufgerufen werden
        "wait_window", "winfo_width", "winfo_height", "winfo_x", "winfo_y",
        "bind_all", "unbind_all", "grab_set", "grab_release", "destroy",
        "winfo_children", "create_window", "yview_scroll", "xview_scroll",
        "get_children", "identify_row", "identify_column", "trace_add",
        # Menu-Methoden
        "add_command", "add_cascade", "add_separator", "add_checkbutton",
        "add_radiobutton"
    },
    # openpyxl
    "openpyxl": {
        "Workbook", "load_workbook", "cell", "iter_rows", "get_column_letter",
        "styles", "chart", "worksheet", "utils"
    },
    # requests
    "requests": {
        "Session", "Request", "Response", "get", "post", "put", "delete",
        "head", "options", "patch", "HTTPAdapter", "iter_content", "raise_for_status"
    },
    # aiohttp
    "aiohttp": {
        "ClientSession", "ClientTimeout", "ClientError", "TCPConnector",
        "request", "get", "post", "put", "delete"
    },
    # Bio.Align (Biopython)
    "Bio": {
        "SeqIO", "AlignIO", "Align", "Seq", "SeqRecord", "PairwiseAligner"
    },
    # pyfaidx
    "pyfaidx": {
        "Faidx", "Fasta", "FastaRecord"
    },
    # intervaltree
    "intervaltree": {
        "Interval", "IntervalTree"
    },
    # PIL/Pillow
    "PIL": {
        "Image", "ImageDraw", "ImageFont", "ImageFilter", "ImageEnhance"
    },
    # myvariant
    "myvariant": {
        "MyVariantInfo", "get_client"
    },
}

# Kompilierte Regex-Patterns für dynamische Aufrufe
DYNAMIC_PATTERNS = {
    "getattr": re.compile(r"\bgetattr\s*\("),
    "setattr": re.compile(r"\bsetattr\s*\("),
    "globals": re.compile(r"\bglobals\s*\(\s*\)"),
    "locals": re.compile(r"\blocals\s*\(\s*\)"),
    "exec": re.compile(r"\bexec\s*\("),
    "eval": re.compile(r"\beval\s*\("),
    # Verbesserte Regex für bind - funktioniert auch mit Lambda
    "bind": re.compile(r"\.bind\s*\(\s*['\"]<[^>]+>['\"],?\s*(?:lambda[^:]*:\s*)?self\.(\w+)"),
    # Verbesserte Regex für command
    "command": re.compile(r"command\s*=\s*(?:lambda[^:]*:\s*)?self\.(\w+)"),
    # Thread-Target
    "ThreadTarget": re.compile(r"Thread\s*\([^)]*target\s*=\s*self\.(\w+)"),
}

# Case-Transition Pattern (für CamelCase Erkennung)
CASE_TRANSITION_PATTERN = re.compile(r'[a-z][A-Z]|[A-Z][a-z]')


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class AnalysisResult:
    """Struktur für Analyse-Ergebnisse mit konsistenten Typen."""
    # Listen statt Sets für UI-Darstellung
    calls: List[str]
    defs: List[str]
    imported_definitions: List[str]  # Explizit importierte Namen
    module_provided_attrs: List[str]  # NEU: Durch Module verfügbar gemachte Attribute
    missing_defs: List[str]
    unused_defs: List[str]
    imports: List[str]
    used_imports: List[str]
    unused_imports: List[str]
    duplicate_imports: List[str]
    missing_imports: List[str]
    dynamic_usage: List[str] = field(default_factory=list)
    dynamic_methods: List[str] = field(default_factory=list)
    check_builtins_and_stdlib: List[Tuple[str, str]] = field(default_factory=list)
    framework_hooks: List[Tuple[str, str]] = field(default_factory=list)
    import_scopes: Dict[str, List[str]] = field(default_factory=dict)
    name_matches: List[Tuple[str, str]] = field(default_factory=list)
    typehints: List[str] = field(default_factory=list)
    module_attribute_usage: Dict[str, List[str]] = field(default_factory=dict)  # NEU: Modul → Attribute Mapping
    todo_comments: List[Tuple[int, str, str]] = field(default_factory=list)  # (Zeile, Typ, Text)


# ============================================================================
# AST VISITOR KLASSEN
# ============================================================================

class ImportScopeAnalyzer(ast.NodeVisitor):
    """Analysiert Imports nach Scope (Top-Level, Klasse, Methode)."""

    def __init__(self):
        self.top_level: Set[str] = set()
        self.class_level: Dict[str, Set[str]] = collections.defaultdict(set)
        self.method_level: Dict[str, Set[str]] = collections.defaultdict(set)
        self.scope_stack: List[Tuple[str, str]] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Verarbeitet Import-Statements."""
        names = {alias.name.split(".")[0] for alias in node.names}
        self._assign_imports(names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Verarbeitet From-Import-Statements."""
        if node.module:
            names = {node.module.split(".")[0]}
            self._assign_imports(names)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Verarbeitet Klassendefinitionen."""
        self.scope_stack.append(("class", node.name))
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Verarbeitet Funktionsdefinitionen."""
        self.scope_stack.append(("func", node.name))
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Verarbeitet asynchrone Funktionsdefinitionen."""
        self.scope_stack.append(("func", node.name))
        self.generic_visit(node)
        self.scope_stack.pop()

    def _assign_imports(self, names: Set[str]) -> None:
        """Ordnet Imports dem aktuellen Scope zu."""
        if not self.scope_stack:
            self.top_level |= names
        else:
            scope_type, scope_name = self.scope_stack[-1]
            if scope_type == "class":
                self.class_level[scope_name] |= names
            elif scope_type == "func":
                self.method_level[scope_name] |= names


class CodeAnalyzer(ast.NodeVisitor):
    """Analysiert Aufrufe, Definitionen und Imports mit Attribut-Zugriff-Erkennung."""

    def __init__(self):
        self.calls: Set[str] = set()
        self.defs: Set[str] = set()
        self.imports: List[str] = []
        self.import_names: Set[str] = set()
        self.imported_definitions: Set[str] = set()
        self.used_names: Set[str] = set()
        self.local_names: Set[str] = set()
        # NEU: Track Modul.Attribut Zugriffe
        self.module_attribute_calls: Dict[str, Set[str]] = collections.defaultdict(set)
        self.imported_modules: Set[str] = set()  # Nur Modulnamen (für import X)

    def visit_Call(self, node: ast.Call) -> None:
        """Verarbeitet Funktionsaufrufe und erkennt Modul-Attribut-Zugriffe."""
        if isinstance(node.func, ast.Attribute):
            # Attribut-Aufruf: obj.method()
            attr_name = node.func.attr
            self.calls.add(attr_name)
            
            # Vollständige Attribut-Kette auflösen (z.B. concurrent.futures.ThreadPoolExecutor)
            root_id, chain = _extract_attribute_chain(node.func)
            if root_id and chain:
                self.module_attribute_calls[root_id].update(chain)
                for i in range(1, len(chain)):
                    subpath = f"{root_id}.{'.'.join(chain[:i])}"
                    self.module_attribute_calls[subpath].add(chain[i])
                    self.module_attribute_calls[subpath].update(chain[i:])
                
        elif isinstance(node.func, ast.Name):
            # Direkter Aufruf: function()
            self.calls.add(node.func.id)
            
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Verarbeitet Attribut-Zugriffe (auch ohne Call)."""
        root_id, chain = _extract_attribute_chain(node)
        if root_id and chain:
            self.module_attribute_calls[root_id].update(chain)
            for i in range(1, len(chain)):
                subpath = f"{root_id}.{'.'.join(chain[:i])}"
                self.module_attribute_calls[subpath].add(chain[i])
                self.module_attribute_calls[subpath].update(chain[i:])
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Verarbeitet Funktionsdefinitionen."""
        self.defs.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Verarbeitet asynchrone Funktionsdefinitionen."""
        self.defs.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Verarbeitet Klassendefinitionen."""
        self.defs.add(node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Verarbeitet Import-Statements und trackt importierte Namen."""
        for alias in node.names:
            module_base = alias.name.split(".")[0]
            self.imports.append(module_base)
            # Speichere den tatsächlich verwendbaren Namen (alias oder module)
            import_name = alias.asname if alias.asname else module_base
            self.import_names.add(import_name)
            self.imported_definitions.add(import_name)
            # Track auch Modulnamen für Attribut-Zugriff (inkl. Submodule & Aliase)
            if alias.asname:
                self.imported_modules.add(alias.asname)
            else:
                self.imported_modules.add(module_base)
                self.imported_modules.add(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Verarbeitet From-Import-Statements und trackt importierte Namen."""
        if node.module:
            module_base = node.module.split(".")[0]
            self.imports.append(module_base)
            self.imported_modules.add(module_base)
            self.imported_modules.add(node.module)
        
        # Füge die importierten Namen hinzu
        for alias in node.names:
            # Überspringe Wildcard-Imports
            if alias.name == '*':
                continue
            
            import_name = alias.asname if alias.asname else alias.name
            self.import_names.add(import_name)
            self.imported_definitions.add(import_name)
            self.imported_modules.add(import_name)

    def visit_Name(self, node: ast.Name) -> None:
        """Verarbeitet Namensreferenzen."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.local_names.add(node.id)
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        """Erfasst Funktionsparameter als lokale Namen."""
        self.local_names.add(node.arg)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Erfasst Exception-Binding-Namen als lokale Namen."""
        if node.name:
            self.local_names.add(node.name)
        self.generic_visit(node)


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def _extract_attribute_chain(node: ast.AST) -> Tuple[Optional[str], List[str]]:
    """
    Extrahiert den Wurzel-Namen und die geordnete Kette von Attributen.
    Z.B. os.path.exists -> ('os', ['path', 'exists'])
    """
    chain: List[str] = []
    curr = node
    while isinstance(curr, ast.Attribute):
        chain.append(curr.attr)
        curr = curr.value
    if isinstance(curr, ast.Name):
        chain.reverse()
        return curr.id, chain
    return None, []


def has_case_transition(name: str) -> bool:
    """
    Prüft, ob Name CamelCase oder gemischte Schreibweise hat.
    
    Args:
        name: Zu prüfender Name
        
    Returns:
        True wenn CamelCase erkannt wurde
    """
    return bool(CASE_TRANSITION_PATTERN.search(name))


def scan_dynamic_usage(code: str) -> Tuple[List[str], Set[str]]:
    """
    Erkennt dynamische Methodenaufrufe (getattr, bind, command, etc.).
    
    Args:
        code: Python-Quellcode als String
        
    Returns:
        Tuple aus (gefundene Pattern-Namen, extrahierte Methodennamen)
    """
    dynamic_hits = []
    dynamic_methods = set()

    for name, pattern in DYNAMIC_PATTERNS.items():
        matches = pattern.findall(code)
        if matches:
            dynamic_hits.append(name)
            # Nur echte Bezeichner (Methodennamen) hinzufügen — Patterns ohne
            # Capture-Gruppe liefern den vollen Match inkl. '(' (z.B. 'getattr('),
            # die kein gueltiger Methodenname sind.
            for match in matches:
                if isinstance(match, str) and match and "(" not in match:
                    dynamic_methods.add(match)

    return dynamic_hits, dynamic_methods


@lru_cache(maxsize=1)
def build_stdlib_whitelist() -> Set[str]:
    """
    Erstellt Whitelist für Standard-Library-Methoden.
    
    Returns:
        Set aller Builtin- und Standardbibliothek-Namen
    """
    wl = set(dir(builtins))

    # Standardbibliothek-Module
    if hasattr(sys, "stdlib_module_names"):
        wl |= sys.stdlib_module_names
    else:
        wl |= {m.name for m in pkgutil.iter_modules()}

    # Methoden von builtin Types
    builtin_types = [str, list, dict, set, tuple, int, float, bool, complex, bytes]
    for t in builtin_types:
        wl |= set(dir(t))

    # Wichtige Standardbibliothek-Objekte
    wl |= set(dir(datetime))
    wl |= set(dir(pathlib.Path))
    wl |= set(dir(sqlite3.Cursor))

    return wl


# Pre-warm Whitelist im Hintergrund (pkgutil.iter_modules ist langsam auf Python < 3.10)
_whitelist_prewarm = threading.Thread(
    target=build_stdlib_whitelist,
    daemon=True,
    name="stdlib-whitelist-prewarm"
)
_whitelist_prewarm.start()


def is_valid_missing_def(name: str) -> bool:
    """
    Prüft, ob ein Name als fehlende Definition gemeldet werden sollte.
    Unterstützt sowohl CamelCase als auch snake_case.
    
    Args:
        name: Zu prüfender Name
        
    Returns:
        True wenn der Name gemeldet werden sollte
    """
    # Private/Protected Namen überspringen
    if name.startswith("_"):
        return False

    # Technische Suffixe generell überspringen (eindeutig interne Patterns)
    if name.endswith(("_fetch", "_stage", "_emit", "_process", "_task", "_async")):
        return False

    # _callback/_handler nur in Framework-Kontext überspringen, nicht pauschal
    if name.endswith(("_callback", "_handler")) and name in FRAMEWORK_MAP:
        return False

    # Framework-Methoden überspringen
    if name in FRAMEWORK_MAP:
        return False
    
    # Namen mit mindestens 3 Zeichen und gültiger Struktur
    if len(name) >= 3:
        # CamelCase ODER snake_case erlauben
        has_camel = has_case_transition(name)
        has_snake = '_' in name and not name.startswith('_')
        return has_camel or has_snake
    
    return False


def filter_missing_defs(
    missing_defs: Set[str],
    false_positives: Set[str],
    typehints: Set[str],
    whitelist: Set[str],
) -> List[str]:
    """
    Filtert falsche Positive aus fehlenden Definitionen.
    
    Args:
        missing_defs: Set der potenziell fehlenden Definitionen
        false_positives: Set bekannter False Positives
        typehints: Set der Type-Hints
        whitelist: Set erlaubter Namen (Builtins, Stdlib)
        
    Returns:
        Sortierte Liste der tatsächlich fehlenden Definitionen
    """
    filtered = []
    for name in missing_defs:
        # Überspringe bekannte False Positives
        if name in false_positives or name in typehints or name in whitelist:
            continue
        
        # Prüfe mit verbesserter Logik
        if is_valid_missing_def(name):
            filtered.append(name)
    
    return sorted(filtered)


_TODO_PATTERN = re.compile(
    r"#\s*(TODO|FIXME|HACK|NOTE|XXX)[:\s]+(.*)", re.IGNORECASE
)


def scan_todo_comments(code: str) -> List[Tuple[int, str, str]]:
    """
    Scannt Quellcode nach TODO/FIXME/HACK/NOTE/XXX Kommentaren.

    Args:
        code: Python-Quellcode als String

    Returns:
        Liste von Tupeln (Zeilennummer, Typ, Text).
        Text wird nur gekürzt wenn er länger als 50 Zeichen ist.
    """
    results = []
    for lineno, line in enumerate(code.splitlines(), start=1):
        match = _TODO_PATTERN.search(line)
        if match:
            tag = match.group(1).upper()
            text = match.group(2).strip()
            if len(text) > 50:
                text = text[:50] + "..."
            results.append((lineno, tag, text))
    return results


@lru_cache(maxsize=128)
def _get_module_all_attributes(module_name: str) -> Optional[Set[str]]:
    """Ermittelt alle exportierten/verfügbaren Attribute eines Moduls per Reflection."""
    try:
        mod = sys.modules.get(module_name)
        if mod is None:
            mod = importlib.import_module(module_name)
        return set(dir(mod))
    except Exception:
        return None


def get_available_module_attributes(analyzer: 'CodeAnalyzer') -> Set[str]:
    """
    Ermittelt alle Attribute, die durch importierte Module verfügbar sind.
    
    Wenn z.B. 'threading' importiert ist und Code 'threading.Lock()' oder
    'concurrent.futures.ThreadPoolExecutor()' verwendet, werden diese Attribute
    als verfügbar erkannt und nicht fälschlich als fehlende Definitionen gemeldet.
    
    Args:
        analyzer: CodeAnalyzer-Instanz mit Import- und Verwendungs-Informationen
        
    Returns:
        Set aller durch Module verfügbar gemachten Attributnamen
    """
    available_attrs = set()
    
    # Durchlaufe alle Modul.Attribut Zugriffe
    for module_name, attributes in analyzer.module_attribute_calls.items():
        base_mod = module_name.split(".")[0]
        is_imported = (
            module_name in analyzer.imported_modules
            or module_name in analyzer.import_names
            or base_mod in analyzer.imported_modules
            or base_mod in analyzer.import_names
        )
        if not is_imported:
            continue

        # 1. Dynamische Introspektion für Standard-Library und importierbare Pakete
        mod_attrs = _get_module_all_attributes(module_name)
        if mod_attrs is None and base_mod != module_name:
            mod_attrs = _get_module_all_attributes(base_mod)

        if mod_attrs is not None:
            for attr in attributes:
                if attr in mod_attrs:
                    available_attrs.add(attr)
            continue

        # 2. Prüfe ob wir die Exports dieses Moduls aus statischer Tabelle kennen (Fallback)
        if module_name in STDLIB_EXPORTS or base_mod in STDLIB_EXPORTS:
            known_exports = STDLIB_EXPORTS.get(module_name, STDLIB_EXPORTS.get(base_mod, set()))
            matched = False
            for attr in attributes:
                if attr in known_exports:
                    available_attrs.add(attr)
                    matched = True
            if matched:
                continue

        # 3. Modul importiert aber offline / unbekannt → akzeptiere alle Attribute
        # (um False Positives bei externen Third-Party-Bibliotheken zu vermeiden)
        available_attrs.update(attributes)
    
    return available_attrs


# ============================================================================
# HAUPTANALYSE
# ============================================================================

def analyze_source(code: str, source_name: str = "<snippet>") -> AnalysisResult:
    """
    Führt komplette Analyse für Python-Quellcode aus.

    Args:
        code: Python-Quellcode als String
        source_name: Anzeigename für Fehlerkontext und JSON-Reports

    Returns:
        AnalysisResult mit allen Analyseergebnissen

    Raises:
        RuntimeError: Bei Parsing-Fehlern
    """
    # Code parsen (nur einmal!)
    try:
        tree = ast.parse(code, filename=source_name)
    except SyntaxError as e:
        raise RuntimeError(f"Syntax-Fehler in Zeile {e.lineno}: {e.msg}")
    except Exception as e:
        raise RuntimeError(f"Fehler beim Parsen: {e}")

    # AST-Analysen
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    scope_analyzer = ImportScopeAnalyzer()
    scope_analyzer.visit(tree)

    # Dynamische Aufrufe scannen
    dynamic_hits, dynamic_methods = scan_dynamic_usage(code)

    # TODO-Kommentare scannen
    todo_comments = scan_todo_comments(code)

    # TypeHints extrahieren (verwendet bereits geparsten Tree!)
    typehints = _extract_typehints(tree)

    # Zusammengesetzte Mengen
    calls = analyzer.calls | dynamic_methods
    # FIX: Kombiniere echte Definitionen mit importierten Namen
    defs = analyzer.defs | analyzer.imported_definitions
    imports_unique = set(analyzer.imports)

    # NEU: Ermittle durch Module verfügbar gemachte Attribute
    module_provided_attrs = get_available_module_attributes(analyzer)

    # VERBESSERT: Berücksichtige Framework-Namen und Widgets
    framework_and_widgets = COMMON_FRAMEWORK_METHODS | COMMON_WIDGETS | set(FRAMEWORK_MAP.keys())

    # ERWEITERT: Berücksichtige auch Modul-Attribute
    missing_defs = (calls - defs) - BUILTINS - framework_and_widgets - module_provided_attrs
    unused_defs = analyzer.defs - calls  # Nur echte Definitionen, nicht Imports

    # VERBESSERT: Nur tatsächliche Import-Namen vergleichen
    # FIX: Namen, die NUR als String-Literal vorkommen (z.B. __all__ = ["Foo"] oder
    # String-/Forward-Ref-Annotationen "Bar" / "List[Bar]"), erfasst die AST-Name-Analyse
    # NICHT als 'used' -> sie wuerden faelschlich als ungenutzt gemeldet und vom Auto-Fix
    # aus der echten Datei geloescht (NameError / fehlendes __all__-Public-API). Daher
    # alle in String-Literalen vorkommenden Bezeichner als genutzt behandeln (konservativ).
    _string_refs: Set[str] = set()
    for _n in ast.walk(tree):
        if isinstance(_n, ast.Constant) and isinstance(_n.value, str):
            _string_refs.update(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", _n.value))
    unused_imports = analyzer.import_names - analyzer.used_names - _string_refs

    # Whitelist und False-Positive-Checks
    whitelist = build_stdlib_whitelist()
    false_positives = {
        name for name in calls
        if (name.startswith("__") and name.endswith("__")) or
           name.isupper() or len(name) <= 2 or
           name in whitelist or name in framework_and_widgets or
           name.startswith("_") or name.endswith(CALLBACK_SUFFIXES)
    }

    # Endergebnisse
    check_builtins = [
        (name, "framework" if name in FRAMEWORK_MAP else "builtin")
        for name in sorted(false_positives)
    ]

    framework_hooks = [
        (name, "magic" if name.startswith("__") else "handler")
        for name in sorted(defs)
        if name.startswith("__") or name.startswith("on_")
    ]

    # Import-Scopes analysieren
    import_scopes = _analyze_import_scopes(scope_analyzer, analyzer)

    # Name-Matching mit verbesserter Lesbarkeit
    name_matches = _find_name_matches(calls, defs)

    # VERBESSERT: missing_imports berücksichtigt Framework-Namen
    missing_imports = (
        analyzer.used_names - defs - imports_unique -
        calls - analyzer.local_names - BUILTINS - framework_and_widgets - module_provided_attrs
    )
    # Module-level Dunders (__file__, __name__, __doc__ etc.) sind implizit
    # verfügbar, aber nicht in dir(builtins) — Falsch-Positive herausfiltern
    missing_imports = {
        name for name in missing_imports
        if not (name.startswith("__") and name.endswith("__"))
    }

    return AnalysisResult(
        calls=sorted(calls),
        defs=sorted(analyzer.defs),  # Nur echte Definitionen
        imported_definitions=sorted(analyzer.imported_definitions),  # Importierte Namen
        module_provided_attrs=sorted(module_provided_attrs),  # NEU: Modul-Attribute
        missing_defs=filter_missing_defs(missing_defs, false_positives, typehints, whitelist),
        unused_defs=sorted(unused_defs),
        imports=sorted(imports_unique),
        used_imports=sorted(analyzer.import_names & analyzer.used_names),
        unused_imports=sorted(unused_imports),
        duplicate_imports=[
            imp for imp, cnt in collections.Counter(analyzer.imports).items() if cnt > 1
        ],
        missing_imports=sorted(missing_imports),
        dynamic_usage=dynamic_hits,
        dynamic_methods=sorted(dynamic_methods),
        check_builtins_and_stdlib=check_builtins,
        framework_hooks=framework_hooks,
        import_scopes=import_scopes,
        name_matches=name_matches,
        typehints=sorted(typehints),
        module_attribute_usage={  # NEU: Modul-Attribut Usage
            mod: sorted(attrs) for mod, attrs in analyzer.module_attribute_calls.items()
            if mod in analyzer.imported_modules or mod in analyzer.import_names
        },
        todo_comments=todo_comments,
    )


def analyze_file(path: str) -> AnalysisResult:
    """
    Führt komplette Analyse einer Python-Datei durch.

    Args:
        path: Pfad zur zu analysierenden Python-Datei

    Returns:
        AnalysisResult mit allen Analyseergebnissen

    Raises:
        RuntimeError: Bei Lese- oder Parsing-Fehlern
        FileNotFoundError: Wenn Datei nicht existiert
    """
    # Validierung
    if not os.path.exists(path):
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")

    if not os.path.isfile(path):
        raise RuntimeError(f"Pfad ist keine Datei: {path}")

    # Datei lesen
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except UnicodeDecodeError:
        try:
            # Fallback zu latin-1
            with open(path, "r", encoding="latin-1") as f:
                code = f.read()
            warnings.warn(
                f"Datei '{path}' konnte nicht als UTF-8 gelesen werden. "
                "latin-1 Fallback wurde verwendet -- Analyse-Ergebnisse können Artefakte enthalten.",
                UnicodeWarning,
                stacklevel=2,
            )
        except Exception as e:
            raise RuntimeError(f"Fehler beim Lesen der Datei: {e}")
    except Exception as e:
        raise RuntimeError(f"Fehler beim Lesen der Datei: {e}")

    return analyze_source(code, source_name=path)


def _extract_typehints(tree: ast.AST) -> Set[str]:
    """
    Extrahiert verwendete Type-Hints aus bereits geparstem AST.
    
    Args:
        tree: Bereits geparster AST
        
    Returns:
        Set der verwendeten Type-Hint-Namen
    """
    hints: Set[str] = set()
    try:
        for node in ast.walk(tree):
            # Variable Annotationen
            if isinstance(node, ast.AnnAssign) and node.annotation:
                for sub in ast.walk(node.annotation):
                    if isinstance(sub, ast.Name):
                        hints.add(sub.id)
            # Funktionsparameter Annotationen
            elif isinstance(node, ast.arg) and node.annotation:
                for sub in ast.walk(node.annotation):
                    if isinstance(sub, ast.Name):
                        hints.add(sub.id)
            # Funktions-Return-Annotationen
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
                for sub in ast.walk(node.returns):
                    if isinstance(sub, ast.Name):
                        hints.add(sub.id)
    except Exception as e:
        # Logge Fehler, aber breche nicht ab
        print(f"Warnung beim Extrahieren von Type-Hints: {e}", file=sys.stderr)
    
    return hints


def _find_name_matches(calls: Set[str], defs: Set[str]) -> List[Tuple[str, str]]:
    """
    Findet ähnliche Namen zwischen Aufrufen und Definitionen.
    
    Args:
        calls: Set der aufgerufenen Namen
        defs: Set der definierten Namen
        
    Returns:
        Liste von Tupeln (aufruf, ähnliche_definition)
    """
    matches = []
    for call in calls:
        if call in defs:
            continue
        
        similar = difflib.get_close_matches(
            call, defs, n=1, cutoff=SIMILARITY_THRESHOLD
        )
        
        if similar:
            matches.append((call, similar[0]))
    
    return matches


def _analyze_import_scopes(
    scope_analyzer: ImportScopeAnalyzer, 
    analyzer: CodeAnalyzer
) -> Dict[str, List[str]]:
    """
    Analysiert Import-Scopes und gibt Empfehlungen.
    
    Args:
        scope_analyzer: ImportScopeAnalyzer-Instanz
        analyzer: CodeAnalyzer-Instanz
        
    Returns:
        Dictionary mit Scope-Analyse-Ergebnissen
    """
    top = scope_analyzer.top_level
    all_class = (
        set.union(*scope_analyzer.class_level.values()) 
        if scope_analyzer.class_level else set()
    )
    all_methods = (
        set.union(*scope_analyzer.method_level.values()) 
        if scope_analyzer.method_level else set()
    )

    results = {
        "multi_local": sorted(
            imp for imp in (all_class | all_methods)
            if imp not in top and
            sum(imp in v for v in scope_analyzer.class_level.values()) +
            sum(imp in v for v in scope_analyzer.method_level.values()) > 1
        ),
        "redundant_local": sorted(
            imp for imp in top 
            if imp in all_class or imp in all_methods
        ),
        "unused_global": sorted(
            imp for imp in top
            if imp not in analyzer.used_names and 
               imp not in all_class and 
               imp not in all_methods
        ),
    }
    return results


# ============================================================================
# ERGEBNISSE FORMATIEREN
# ============================================================================

def generate_report(result: AnalysisResult) -> str:
    """
    Generiert einen formatierten Report.
    
    Args:
        result: AnalysisResult-Objekt
        
    Returns:
        Formatierter Report als String
    """
    report = []

    report.append("=" * 70 + "\n")
    report.append("PYTHON CODE ANALYSE - ERGEBNISSE\n")
    report.append("=" * 70 + "\n\n")

    # Hauptergebnisse
    report.append("[ANALYSE] HAUPTERGEBNISSE\n")
    report.append("-" * 70 + "\n")
    report.append(f"Fehlende Definitionen ({len(result.missing_defs)}):\n")
    report.append(f"  {', '.join(result.missing_defs) if result.missing_defs else '(keine)'}\n\n")
    
    report.append(f"Ungenutzte Definitionen ({len(result.unused_defs)}):\n")
    report.append(f"  {', '.join(result.unused_defs) if result.unused_defs else '(keine)'}\n\n")
    
    report.append(f"Ungenutzte Imports ({len(result.unused_imports)}):\n")
    report.append(f"  {', '.join(result.unused_imports) if result.unused_imports else '(keine)'}\n\n")
    report.append(f"Fehlende Imports ({len(result.missing_imports)}):\n")
    report.append(f"  {', '.join(result.missing_imports) if result.missing_imports else '(keine)'}\n\n")

    # Import-Analyse
    if result.import_scopes:
        report.append("\n[IMPORTS] IMPORT-SCOPE-ANALYSE\n")
        report.append("-" * 70 + "\n")
        
        scopes = result.import_scopes
        multi = scopes.get('multi_local', [])
        redundant = scopes.get('redundant_local', [])
        unused_global = scopes.get('unused_global', [])
        
        if multi:
            report.append(f"Mehrfach lokal importiert:\n  {', '.join(multi)}\n\n")
        if redundant:
            report.append(f"Redundant lokal importiert:\n  {', '.join(redundant)}\n\n")
        if unused_global:
            report.append(f"Ungenutzte globale Imports:\n  {', '.join(unused_global)}\n\n")

    # Duplikate
    if result.duplicate_imports:
        report.append("\n[WARNUNG] DOPPELTE IMPORTS\n")
        report.append("-" * 70 + "\n")
        report.append(f"  {', '.join(result.duplicate_imports)}\n\n")

    # Dynamische Aufrufe
    if result.dynamic_usage:
        report.append("\n[DYNAMISCH] DYNAMISCHE AUFRUFE\n")
        report.append("-" * 70 + "\n")
        report.append(f"Erkannte Patterns: {', '.join(result.dynamic_usage)}\n")
        if result.dynamic_methods:
            report.append(f"Extrahierte Methoden: {', '.join(result.dynamic_methods)}\n")
        report.append("\n")

    # Namens-Matches
    if result.name_matches:
        report.append("\n[TIPP] ÄHNLICHE NAMEN (mögliche Tippfehler)\n")
        report.append("-" * 70 + "\n")
        for call, match in result.name_matches:
            report.append(f"  '{call}' → vielleicht '{match}'?\n")
        report.append("\n")

    # Statistik
    report.append("\n[STATS] STATISTIK\n")
    report.append("-" * 70 + "\n")
    report.append(f"  Aufrufe gesamt: {len(result.calls)}\n")
    report.append(f"  Definitionen gesamt: {len(result.defs)}\n")
    report.append(f"  Importierte Definitionen: {len(result.imported_definitions)}\n")
    report.append(f"  Modul-bereitgestellte Attribute: {len(result.module_provided_attrs)}\n")
    report.append(f"  Imports gesamt: {len(result.imports)}\n")
    report.append(f"  Framework-Hooks: {len(result.framework_hooks)}\n")
    report.append(f"  Type-Hints: {len(result.typehints)}\n")

    # Optional: Zeige importierte Definitionen wenn gewünscht
    if result.imported_definitions:
        report.append("\n[IMPORTS] IMPORTIERTE DEFINITIONEN\n")
        report.append("-" * 70 + "\n")
        # Gruppiere nach Typ für bessere Lesbarkeit
        classes = [name for name in result.imported_definitions if name[0].isupper()]
        functions = [name for name in result.imported_definitions if name[0].islower()]
        
        if classes:
            report.append(f"  Klassen/Typen ({len(classes)}): {', '.join(sorted(classes)[:20])}")
            if len(classes) > 20:
                report.append(f" ... +{len(classes) - 20} weitere")
            report.append("\n")
        
        if functions:
            report.append(f"  Funktionen ({len(functions)}): {', '.join(sorted(functions)[:20])}")
            if len(functions) > 20:
                report.append(f" ... +{len(functions) - 20} weitere")
            report.append("\n")

    # NEU: Zeige Modul-Attribut Usage
    if result.module_attribute_usage:
        report.append("\n[MODULE] MODUL-ATTRIBUT VERWENDUNG\n")
        report.append("-" * 70 + "\n")
        report.append("  Zeigt welche Attribute von importierten Modulen verwendet werden:\n\n")
        
        for module, attrs in sorted(result.module_attribute_usage.items())[:10]:
            attrs_str = ', '.join(sorted(attrs)[:10])
            if len(attrs) > 10:
                attrs_str += f' ... +{len(attrs) - 10} weitere'
            report.append(f"  {module}: {attrs_str}\n")
        
        if len(result.module_attribute_usage) > 10:
            report.append(f"  ... und {len(result.module_attribute_usage) - 10} weitere Module\n")

    # TODO-Kommentare
    if result.todo_comments:
        report.append(f"\n[TODO] TODO-KOMMENTARE ({len(result.todo_comments)})\n")
        report.append("-" * 70 + "\n")
        for lineno, tag, text in result.todo_comments:
            report.append(f"  Zeile {lineno:4d}: [{tag}] {text}\n")

    report.append("\n" + "=" * 70 + "\n")

    return "".join(report)


# ============================================================================
# GUI
# ============================================================================

def create_safe_filename(original_path: str, suffix: str) -> str:
    """
    Erstellt sicheren Export-Dateinamen ohne bestehende Dateien zu überschreiben.
    
    Args:
        original_path: Ursprünglicher Dateipfad
        suffix: Suffix für neue Datei (z.B. "_analysis.txt")
        
    Returns:
        Sicherer Dateipfad
    """
    # VERBESSERT: Verwende rsplit statt replace
    base_path = original_path.rsplit(".py", 1)[0]
    export_path = f"{base_path}{suffix}"
    
    # Wenn Datei existiert, nummeriere
    counter = 1
    while os.path.exists(export_path):
        export_path = f"{base_path}_{counter}{suffix}"
        counter += 1
    
    return export_path


def run_analysis(output_widget: scrolledtext.ScrolledText) -> None:
    """
    Lädt Datei und führt Analyse durch.
    
    Args:
        output_widget: ScrolledText-Widget für Ausgabe
    """
    path = filedialog.askopenfilename(
        title="Python-Datei auswählen",
        filetypes=[("Python Dateien", "*.py"), ("Alle Dateien", "*.*")]
    )
    
    if not path:
        return
    try:
        result = analyze_file(path)
        # Für Auto-Fix speichern
        global _last_analysis_path, _last_analysis_result
        _last_analysis_path = path
        _last_analysis_result = result
    except FileNotFoundError as e:
        output_widget.delete("1.0", tk.END)
        output_widget.insert(tk.END, f"[FEHLER] {e}")
        messagebox.showerror("Dateifehler", str(e))
        return
    except RuntimeError as e:
        output_widget.delete("1.0", tk.END)
        output_widget.insert(tk.END, f"[FEHLER] {e}")
        messagebox.showerror("Analysefehler", str(e))
        return
    except Exception as e:
        output_widget.delete("1.0", tk.END)
        output_widget.insert(tk.END, f"[FEHLER] Unerwarteter Fehler: {e}")
        messagebox.showerror("Fehler", f"Unerwarteter Fehler: {e}")
        return

    # Ergebnisse anzeigen
    output_widget.delete("1.0", tk.END)
    output_widget.insert(tk.END, f"[DATEI] Analysierte Datei: {os.path.basename(path)}\n\n")
    output_widget.insert(tk.END, generate_report(result))

    # Export mit Bestätigung
    try:
        export_path = create_safe_filename(path, "_analysis.txt")
        
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(f"Analysierte Datei: {path}\n")
            f.write(f"Datum: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(generate_report(result))
        
        output_widget.insert(tk.END, f"\n[OK] Report gespeichert: {export_path}")

    except PermissionError:
        output_widget.insert(tk.END, "\n[WARNUNG] Keine Schreibberechtigung für Export")
        messagebox.showwarning("Export-Fehler", "Keine Schreibberechtigung")
    except Exception as e:
        output_widget.insert(tk.END, f"\n[WARNUNG] Export-Fehler: {e}")
        messagebox.showwarning("Export-Fehler", str(e))




def _collect_unused_import_lines(tree: ast.AST, unused_set: Set[str]) -> Set[int]:
    """Gibt die Zeilennummern zurück, die zu vollständig ungenutzten Imports gehören."""
    lines_to_remove: Set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # __future__-Imports niemals entfernen — sie aendern Python-Semantik
            # (z.B. 'from __future__ import annotations' aktiviert PEP 563)
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                continue
            names = [alias.asname or alias.name.split(".")[0] for alias in node.names
                     if alias.name != "*"]
            if names and all(name in unused_set for name in names):
                lines_to_remove.update(range(node.lineno, node.end_lineno + 1))
    return lines_to_remove


def auto_fix_unused_imports(output_widget: scrolledtext.ScrolledText) -> None:
    """
    Entfernt ungenutzte Imports aus der zuletzt analysierten Datei.
    
    Args:
        output_widget: ScrolledText-Widget für Ausgabe
    """
    global _last_analysis_path, _last_analysis_result
    
    if not _last_analysis_path or not _last_analysis_result:
        messagebox.showwarning("Hinweis", "Bitte erst eine Datei analysieren!")
        return
    
    if not _last_analysis_result.unused_imports:
        messagebox.showinfo("Info", "Keine ungenutzten Imports gefunden!")
        return
    
    # Bestätigung
    unused_list = ", ".join(_last_analysis_result.unused_imports)
    if not messagebox.askyesno(
        "Auto-Fix bestätigen",
        f"Folgende Imports werden entfernt:\n\n{unused_list}\n\nFortfahren?"
    ):
        return
    
    try:
        # Datei lesen mit Encoding-Fallback — erkanntes Encoding für Schreibzugriff merken
        detected_encoding = "utf-8"
        try:
            with open(_last_analysis_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            detected_encoding = "latin-1"
            with open(_last_analysis_path, "r", encoding="latin-1") as f:
                lines = f.readlines()

        # AST parsen (readlines() beibehalten — splitlines() würde bei \x0c
        # Zeilennummern gegenüber AST-lineno verschieben und falsche Zeilen löschen)
        tree = ast.parse("".join(lines))

        # Import-Zeilen markieren die entfernt werden sollen
        unused_set = set(_last_analysis_result.unused_imports)
        lines_to_remove = _collect_unused_import_lines(tree, unused_set)

        if not lines_to_remove:
            messagebox.showinfo("Info", "Keine vollständig ungenutzten Import-Zeilen gefunden.\n(Teilweise genutzte Imports müssen manuell bearbeitet werden)")
            return

        # Backup und Ausgabe im erkannten Encoding — verhindert Korrumpierung von
        # latin-1-Dateien mit nicht-ASCII-Zeichen und # coding: latin-1 Deklaration
        backup_path = _last_analysis_path + ".bak"
        with open(backup_path, "w", encoding=detected_encoding) as f:
            f.writelines(lines)

        # Neue Datei ohne ungenutzte Imports
        new_lines = [line for i, line in enumerate(lines, 1) if i not in lines_to_remove]

        with open(_last_analysis_path, "w", encoding=detected_encoding) as f:
            f.writelines(new_lines)
        
        # Ausgabe
        output_widget.insert(tk.END, "\n\n[OK] AUTO-FIX ERFOLGREICH\n")
        output_widget.insert(tk.END, f"Entfernte Zeilen: {sorted(lines_to_remove)}\n")
        output_widget.insert(tk.END, f"Backup erstellt: {backup_path}\n")
        output_widget.insert(tk.END, "\nBitte Datei erneut analysieren zur Überprüfung.")
        
        messagebox.showinfo("Erfolg", f"Ungenutzte Imports entfernt!\nBackup: {backup_path}")
        
    except Exception as e:
        messagebox.showerror("Fehler", f"Auto-Fix fehlgeschlagen: {e}")




# ============================================================================
# MULTI-FILE / PROJEKT-ANALYSE
# ============================================================================

def collect_python_files(folder_path: str, exclude_patterns: List[str] = None) -> List[str]:
    """Sammelt alle Python-Dateien in einem Ordner rekursiv."""
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', '.git', '.venv', 'venv', 'env', 
                           'node_modules', '.eggs', 'build', 'dist']
    
    python_files = []
    folder = pathlib.Path(folder_path)
    
    for py_file in folder.rglob("*.py"):
        skip = False
        for pattern in exclude_patterns:
            if pattern in py_file.parts:
                skip = True
                break
        if not skip:
            python_files.append(str(py_file))
    
    return sorted(python_files)


@dataclass
class ProjectAnalysisResult:
    """Aggregierte Ergebnisse einer Projekt-Analyse."""
    folder_path: str
    files_analyzed: int
    files_with_errors: List[Tuple[str, str]]
    total_lines: int
    total_defs: int
    total_imports: int
    all_unused_imports: Dict[str, List[str]]
    all_unused_defs: Dict[str, List[str]]
    all_missing_defs: Dict[str, List[str]]
    all_missing_imports: Dict[str, List[str]]
    all_duplicate_imports: Dict[str, List[str]]
    file_results: Dict[str, AnalysisResult]


def analyze_project(folder_path: str, progress_callback=None) -> ProjectAnalysisResult:
    """Analysiert alle Python-Dateien in einem Projektordner."""
    python_files = collect_python_files(folder_path)
    files_with_errors, file_results = [], {}
    all_unused_imports, all_unused_defs = {}, {}
    all_missing_defs, all_missing_imports, all_duplicate_imports = {}, {}, {}
    total_lines, total_defs, total_imports = 0, 0, 0
    
    for i, file_path in enumerate(python_files):
        if progress_callback:
            progress_callback(i + 1, len(python_files), file_path)
        try:
            result = analyze_file(file_path)
            file_results[file_path] = result
            total_defs += len(result.defs)
            total_imports += len(result.imports)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        total_lines += len(f.readlines())
                except (IOError, OSError):
                    pass
            except (IOError, OSError):
                pass
            rel_path = os.path.relpath(file_path, folder_path)
            if result.unused_imports:
                all_unused_imports[rel_path] = result.unused_imports
            if result.unused_defs:
                all_unused_defs[rel_path] = result.unused_defs
            if result.missing_defs:
                all_missing_defs[rel_path] = result.missing_defs
            if result.missing_imports:
                all_missing_imports[rel_path] = result.missing_imports
            if result.duplicate_imports:
                all_duplicate_imports[rel_path] = result.duplicate_imports
        except Exception as e:
            files_with_errors.append((file_path, str(e)))
    
    return ProjectAnalysisResult(
        folder_path=folder_path, files_analyzed=len(python_files) - len(files_with_errors),
        files_with_errors=files_with_errors, total_lines=total_lines,
        total_defs=total_defs, total_imports=total_imports,
        all_unused_imports=all_unused_imports, all_unused_defs=all_unused_defs,
        all_missing_defs=all_missing_defs, all_missing_imports=all_missing_imports,
        all_duplicate_imports=all_duplicate_imports,
        file_results=file_results
    )


def generate_project_report(result: ProjectAnalysisResult) -> str:
    """Generiert einen formatierten Projekt-Report."""
    report = ["=" * 70 + "\n", "PROJEKT CODE ANALYSE\n", "=" * 70 + "\n\n"]
    report.append(f"Projekt: {os.path.basename(result.folder_path)}\n\n")
    report.append(f"Dateien: {result.files_analyzed} | Zeilen: {result.total_lines:,}\n")
    report.append(f"Definitionen: {result.total_defs:,} | Imports: {result.total_imports:,}\n\n")
    
    total_ui = sum(len(v) for v in result.all_unused_imports.values())
    total_ud = sum(len(v) for v in result.all_unused_defs.values())
    report.append(f"Ungenutzte Imports: {total_ui} | Ungenutzte Defs: {total_ud}\n\n")
    
    if result.all_unused_imports:
        report.append("UNGENUTZTE IMPORTS:\n" + "-" * 50 + "\n")
        for fp, imps in sorted(result.all_unused_imports.items()):
            report.append(f"  {fp}: {', '.join(imps)}\n")
    
    if result.all_unused_defs:
        report.append("\nUNGENUTZTE DEFINITIONEN:\n" + "-" * 50 + "\n")
        for fp, defs in sorted(result.all_unused_defs.items()):
            report.append(f"  {fp}: {', '.join(defs)}\n")

    if result.all_missing_defs:
        report.append("\nFEHLENDE DEFINITIONEN:\n" + "-" * 50 + "\n")
        for fp, defs in sorted(result.all_missing_defs.items()):
            report.append(f"  {fp}: {', '.join(defs)}\n")

    if result.all_missing_imports:
        report.append("\nFEHLENDE IMPORTS:\n" + "-" * 50 + "\n")
        for fp, imports in sorted(result.all_missing_imports.items()):
            report.append(f"  {fp}: {', '.join(imports)}\n")

    if result.all_duplicate_imports:
        report.append("\nDOPPELTE IMPORTS:\n" + "-" * 50 + "\n")
        for fp, imports in sorted(result.all_duplicate_imports.items()):
            report.append(f"  {fp}: {', '.join(imports)}\n")

    if result.files_with_errors:
        report.append("\nDATEIEN MIT FEHLERN:\n" + "-" * 50 + "\n")
        for fp, error in sorted(result.files_with_errors):
            report.append(f"  {fp}: {error}\n")

    score = max(0, 100 - total_ui * 2 - total_ud * 2)
    report.append(f"\n{'=' * 70}\nSCORE: {score}/100\n{'=' * 70}\n")
    return "".join(report)


def _generated_at_iso() -> str:
    """Erzeugt einen stabilen UTC-Zeitstempel für JSON-Reports."""
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _todo_comments_as_dicts(result: AnalysisResult) -> List[Dict[str, Any]]:
    """Wandelt TODO-Kommentare in JSON-kompatible Objekte um."""
    return [
        {"line": lineno, "tag": tag, "text": text}
        for lineno, tag, text in result.todo_comments
    ]


def _analysis_summary(result: AnalysisResult) -> Dict[str, int]:
    """Verdichtete Metriken für eine einzelne Analyse."""
    return {
        "calls": len(result.calls),
        "definitions": len(result.defs),
        "imports": len(result.imports),
        "unused_imports": len(result.unused_imports),
        "unused_definitions": len(result.unused_defs),
        "missing_definitions": len(result.missing_defs),
        "missing_imports": len(result.missing_imports),
        "duplicate_imports": len(result.duplicate_imports),
        "todos": len(result.todo_comments),
    }


def _analysis_result_to_json(result: AnalysisResult) -> Dict[str, Any]:
    """Serialisiert ein Dateiergebnis in das Austauschformat."""
    return {
        "summary": _analysis_summary(result),
        "calls": result.calls,
        "definitions": result.defs,
        "imported_definitions": result.imported_definitions,
        "imports": result.imports,
        "used_imports": result.used_imports,
        "unused_imports": result.unused_imports,
        "unused_definitions": result.unused_defs,
        "missing_definitions": result.missing_defs,
        "missing_imports": result.missing_imports,
        "duplicate_imports": result.duplicate_imports,
        "dynamic_usage": result.dynamic_usage,
        "dynamic_methods": result.dynamic_methods,
        "framework_hooks": [
            {"name": name, "kind": kind}
            for name, kind in result.framework_hooks
        ],
        "import_scopes": result.import_scopes,
        "name_matches": [
            {"name": name, "candidate": candidate}
            for name, candidate in result.name_matches
        ],
        "typehints": result.typehints,
        "module_attribute_usage": result.module_attribute_usage,
        "todos": _todo_comments_as_dicts(result),
    }


def _json_file_entry(path: str, result: AnalysisResult) -> Dict[str, Any]:
    """Erstellt einen files[]-Eintrag für den JSON-Report."""
    return {
        "path": path,
        "analysis": _analysis_result_to_json(result),
    }


def _project_summary(result: ProjectAnalysisResult) -> Dict[str, int]:
    """Verdichtete Metriken für eine Projektanalyse."""
    return {
        "files_analyzed": result.files_analyzed,
        "files_with_errors": len(result.files_with_errors),
        "total_lines": result.total_lines,
        "total_definitions": result.total_defs,
        "total_imports": result.total_imports,
        "unused_imports": sum(len(v) for v in result.all_unused_imports.values()),
        "unused_definitions": sum(len(v) for v in result.all_unused_defs.values()),
        "missing_definitions": sum(len(v) for v in result.all_missing_defs.values()),
        "missing_imports": sum(len(v) for v in result.all_missing_imports.values()),
        "duplicate_imports": sum(len(v) for v in result.all_duplicate_imports.values()),
    }


def build_json_report(
    source_kind: str,
    result: AnalysisResult | ProjectAnalysisResult,
    source_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Baut `methodenanalyser-report-v1.json` für Datei, Projekt oder Snippet.

    Das Format ist bewusst stabil und PWA-freundlich: keine absoluten Pfade in
    files[], Textreports bleiben unabhängig davon unverändert.
    """
    if source_kind not in {"file", "project", "snippet", "zip"}:
        raise ValueError(f"Unbekannte source_kind: {source_kind}")

    report: Dict[str, Any] = {
        "schema_version": JSON_SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "source_kind": source_kind,
        "generated_at": _generated_at_iso(),
        "source": {"name": source_name or source_kind},
        "files": [],
        "unused_imports": {},
        "unused_definitions": {},
        "missing_definitions": {},
        "missing_imports": {},
        "duplicate_imports": {},
        "summary": {},
    }

    if isinstance(result, ProjectAnalysisResult):
        source_root = result.folder_path
        source_label = os.path.basename(source_name) if source_name else os.path.basename(source_root)

        def normalize(value: str) -> str:
            return value.replace("\\", "/")

        report["source"] = {"name": source_label, "kind": source_kind}
        report["files"] = [
            _json_file_entry(normalize(os.path.relpath(path, source_root)), file_result)
            for path, file_result in sorted(result.file_results.items())
        ]
        report["unused_imports"] = {
            normalize(path): values for path, values in sorted(result.all_unused_imports.items())
        }
        report["unused_definitions"] = {
            normalize(path): values for path, values in sorted(result.all_unused_defs.items())
        }
        report["missing_definitions"] = {
            normalize(path): values for path, values in sorted(result.all_missing_defs.items())
        }
        report["missing_imports"] = {
            normalize(path): values for path, values in sorted(result.all_missing_imports.items())
        }
        report["duplicate_imports"] = {
            normalize(path): values for path, values in sorted(result.all_duplicate_imports.items())
        }
        report["errors"] = [
            {
                "path": normalize(os.path.relpath(path, source_root))
                if os.path.isabs(path) else normalize(path),
                "message": message,
            }
            for path, message in result.files_with_errors
        ]
        report["summary"] = _project_summary(result)
        return report

    file_key = source_name or ("<snippet>" if source_kind == "snippet" else "file.py")
    if source_kind == "file":
        file_key = os.path.basename(file_key)

    report["files"] = [_json_file_entry(file_key, result)]
    report["unused_imports"] = {file_key: result.unused_imports}
    report["unused_definitions"] = {file_key: result.unused_defs}
    report["missing_definitions"] = {file_key: result.missing_defs}
    report["missing_imports"] = {file_key: result.missing_imports}
    report["duplicate_imports"] = {file_key: result.duplicate_imports}
    report["summary"] = _analysis_summary(result)
    return report


def write_json_report(report: Dict[str, Any], output_path: str) -> str:
    """Schreibt einen JSON-Report und gibt den absoluten Pfad zurück."""
    target = os.path.abspath(output_path)
    target_dir = os.path.dirname(target)
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return target


def run_project_analysis(output_widget: scrolledtext.ScrolledText) -> None:
    """Ordner-Dialog und Projekt-Analyse."""
    folder_path = filedialog.askdirectory(title="Projektordner auswählen")
    if not folder_path:
        return
    
    output_widget.delete("1.0", tk.END)
    output_widget.insert(tk.END, f"Analysiere: {folder_path}\n\n")
    output_widget.update_idletasks()  # nur Render-Jobs, keine User-Events (Re-entranz-Schutz)

    def progress_cb(cur, tot, fp):
        output_widget.insert(tk.END, f"[{cur}/{tot}] {os.path.basename(fp)}\n")
        output_widget.see(tk.END)
        output_widget.update_idletasks()  # nur Render-Jobs, keine User-Events (Re-entranz-Schutz)
    
    try:
        result = analyze_project(folder_path, progress_cb)
        output_widget.delete("1.0", tk.END)
        output_widget.insert(tk.END, generate_project_report(result))
        
        export_path = os.path.join(folder_path, "project_analysis.txt")
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(generate_project_report(result))
        output_widget.insert(tk.END, f"\nGespeichert: {export_path}")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))


def _build_welcome_text() -> str:
    """Baut die übersetzte Willkommensnachricht inkl. eingesetztem Shortcut-Hinweis."""
    return _t("welcome_body").replace("{shortcut}", _get_keyboard_shortcut_hint())


def create_gui() -> None:
    """Erstellt und startet die GUI-Anwendung."""
    root = tk.Tk()
    root.title("Python Code Analyzer v3.0 - Multi-File")
    root.geometry(WINDOW_GEOMETRY)
    if os.path.exists(APP_ICON_PATH):
        try:
            root.iconbitmap(default=APP_ICON_PATH)
        except tk.TclError:
            pass
    
    # Button-Frame für besseres Layout
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    
    def show_info_dialog() -> None:
        messagebox.showinfo(
            "Python Code Analyzer",
            _t("info_body").replace("{version}", TOOL_VERSION),
        )

    # Analyse-Button
    btn = tk.Button(
        button_frame,
        text=_t("btn_analyze_file"),
        command=lambda: run_analysis(output),
        bg="#4CAF50",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=20,
        pady=10,
        cursor="hand2"
    )
    btn.pack(side=tk.LEFT, padx=5)
    
    # Info-Button
    info_btn = tk.Button(
        button_frame,
        text=_t("btn_info"),
        command=show_info_dialog,
        bg="#2196F3",
        fg="white",
        font=("Arial", 10),
        padx=15,
        pady=10,
        cursor="hand2"
    )
    info_btn.pack(side=tk.LEFT, padx=5)
    
    # Auto-Fix Button
    fix_btn = tk.Button(
        button_frame,
        text=_t("btn_autofix"),
        command=lambda: auto_fix_unused_imports(output),
        bg="#FF9800",
        fg="white",
        font=("Arial", 10),
        padx=15,
        pady=10,
        cursor="hand2"
    )
    fix_btn.pack(side=tk.LEFT, padx=5)

    # NEU: Projekt-Analyse Button
    project_btn = tk.Button(
        button_frame,
        text=_t("btn_analyze_project"),
        command=lambda: run_project_analysis(output),
        bg="#9C27B0",
        fg="white",
        font=("Arial", 10),
        padx=15,
        pady=10,
        cursor="hand2"
    )
    project_btn.pack(side=tk.LEFT, padx=5)

    shortcut_hint = tk.Label(
        root,
        text=_get_keyboard_shortcut_hint(),
        anchor="w",
        fg="#555555",
        font=("Arial", 9),
    )
    shortcut_hint.pack(fill=tk.X, padx=12, pady=(0, 8))

    # Output-Widget als globale Referenz
    output = scrolledtext.ScrolledText(
        root,
        width=OUTPUT_WIDTH,
        height=OUTPUT_HEIGHT,
        font=OUTPUT_FONT,
        wrap=tk.WORD,
        bg="#f5f5f5",
        fg="#333333"
    )
    output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    # Willkommensnachricht
    output.insert(tk.END, _build_welcome_text())

    # --- Menue "Sprache / Language" (Welle-1 U1: sichtbarer DE/EN-Schalter) ---
    translator = get_translator()
    current_lang = translator.get_language() if translator is not None else get_saved_language()
    lang_var = tk.StringVar(value=current_lang)

    def apply_language(lang: str) -> None:
        """Wechselt Sprache, persistiert sie und stellt die Oberflaeche live um."""
        if translator is not None:
            translator.set_language(lang)
        set_saved_language(lang)
        lang_var.set(lang)
        btn.config(text=_t("btn_analyze_file"))
        info_btn.config(text=_t("btn_info"))
        fix_btn.config(text=_t("btn_autofix"))
        project_btn.config(text=_t("btn_analyze_project"))
        shortcut_hint.config(text=_get_keyboard_shortcut_hint())
        # Willkommenstext nur neu rendern, solange keine Analyse-Ausgabe angezeigt wird.
        if output.get("1.0", "1.end").strip() in _WELCOME_HEADS:
            output.delete("1.0", tk.END)
            output.insert(tk.END, _build_welcome_text())
        messagebox.showinfo("Sprache / Language", _t("lang_switched_msg"))

    menubar = tk.Menu(root)
    lang_menu = tk.Menu(menubar, tearoff=0)
    lang_menu.add_radiobutton(
        label="Deutsch", value="de", variable=lang_var,
        command=lambda: apply_language("de"),
    )
    lang_menu.add_radiobutton(
        label="English", value="en", variable=lang_var,
        command=lambda: apply_language("en"),
    )
    menubar.add_cascade(label=_t("menu_language"), menu=lang_menu)
    root.config(menu=menubar)

    _register_gui_shortcuts(
        root,
        analyze_file_cb=lambda: run_analysis(output),
        info_cb=show_info_dialog,
        auto_fix_cb=lambda: auto_fix_unused_imports(output),
        analyze_project_cb=lambda: run_project_analysis(output),
    )
    output.focus_set()

    root.mainloop()


def _get_keyboard_shortcut_hint() -> str:
    """Liefert den sichtbaren Kurzhinweis für die Hauptaktionen der GUI."""
    return _t("shortcut_hint")


def _register_gui_shortcuts(
    root: Any,
    analyze_file_cb: Callable[[], None],
    info_cb: Callable[[], None],
    auto_fix_cb: Callable[[], None],
    analyze_project_cb: Callable[[], None],
) -> None:
    """Bindet globale Tastaturkürzel für die primären GUI-Aktionen."""
    shortcuts = {
        "<Alt-d>": analyze_file_cb,
        "<Alt-D>": analyze_file_cb,
        "<Alt-p>": analyze_project_cb,
        "<Alt-P>": analyze_project_cb,
        "<Alt-f>": auto_fix_cb,
        "<Alt-F>": auto_fix_cb,
        "<F1>": info_cb,
    }

    for sequence, callback in shortcuts.items():
        def _handler(_event: Any, cb: Callable[[], None] = callback) -> str:
            cb()
            return "break"

        root.bind_all(sequence, _handler)


def _file_has_findings(result: AnalysisResult) -> bool:
    """Prüft, ob eine Dateianalyse relevante Funde enthält."""
    return any((
        result.missing_defs,
        result.unused_defs,
        result.unused_imports,
        result.duplicate_imports,
        result.missing_imports,
        result.todo_comments,
    ))


def _project_has_findings(result: ProjectAnalysisResult) -> bool:
    """Prüft, ob eine Projektanalyse relevante Funde enthält."""
    return any((
        result.all_unused_imports,
        result.all_unused_defs,
        result.all_missing_defs,
        result.all_missing_imports,
        result.all_duplicate_imports,
        result.files_with_errors,
    ))


def _emit_cli_report(report: str) -> None:
    """Schreibt Reports konsistent nach stdout."""
    sys.stdout.write(report)
    if not report.endswith("\n"):
        sys.stdout.write("\n")


def _write_cli_json_if_requested(report: Dict[str, Any], output_path: Optional[str]) -> bool:
    """Schreibt optional den JSON-Report; Fehler gehen nach stderr."""
    if not output_path:
        return True
    try:
        written_path = write_json_report(report, output_path)
    except Exception as exc:
        print(f"[FEHLER] JSON-Export fehlgeschlagen: {exc}", file=sys.stderr)
        return False
    print(f"[OK] JSON gespeichert: {written_path}", file=sys.stderr)
    return True


def _run_cli_file(path: str, json_output: Optional[str] = None) -> int:
    """Führt eine Datei-Analyse ohne GUI aus."""
    try:
        result = analyze_file(path)
    except Exception as exc:
        print(f"[FEHLER] {exc}", file=sys.stderr)
        return EXIT_ANALYSIS_ERROR

    _emit_cli_report(generate_report(result))
    json_report = build_json_report("file", result, source_name=path)
    if not _write_cli_json_if_requested(json_report, json_output):
        return EXIT_ANALYSIS_ERROR
    return EXIT_FINDINGS if _file_has_findings(result) else EXIT_OK


def _run_cli_project(path: str, json_output: Optional[str] = None) -> int:
    """Führt eine Projektanalyse ohne GUI aus."""
    if not os.path.isdir(path):
        print(f"[FEHLER] Projektordner nicht gefunden: {path}", file=sys.stderr)
        return EXIT_ANALYSIS_ERROR

    try:
        result = analyze_project(path)
    except Exception as exc:
        print(f"[FEHLER] Projektanalyse fehlgeschlagen: {exc}", file=sys.stderr)
        return EXIT_ANALYSIS_ERROR

    _emit_cli_report(generate_project_report(result))
    json_report = build_json_report("project", result, source_name=path)
    if not _write_cli_json_if_requested(json_report, json_output):
        return EXIT_ANALYSIS_ERROR

    if result.files_with_errors:
        return EXIT_PARTIAL_ERROR
    return EXIT_FINDINGS if _project_has_findings(result) else EXIT_OK


def _run_cli_snippet(code: str, json_output: Optional[str] = None) -> int:
    """Analysiert ein Snippet ohne temporäre Projektdateien."""
    try:
        result = analyze_source(code, source_name="<snippet>")
    except Exception as exc:
        print(f"[FEHLER] {exc}", file=sys.stderr)
        return EXIT_ANALYSIS_ERROR

    _emit_cli_report(generate_report(result))
    json_report = build_json_report("snippet", result, source_name="<snippet>")
    if not _write_cli_json_if_requested(json_report, json_output):
        return EXIT_ANALYSIS_ERROR
    return EXIT_FINDINGS if _file_has_findings(result) else EXIT_OK


def build_cli_parser() -> argparse.ArgumentParser:
    """Erstellt den Argument-Parser für den CLI-Modus."""
    parser = argparse.ArgumentParser(
        description="Analysiert Python-Dateien oder ganze Projektordner ohne GUI.",
    )
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--file",
        metavar="DATEI.py",
        help="analysiert eine einzelne Python-Datei und schreibt den Textreport nach stdout",
    )
    target_group.add_argument(
        "--project",
        metavar="ORDNER",
        help="analysiert rekursiv einen Projektordner und schreibt den Projektreport nach stdout",
    )
    target_group.add_argument(
        "--stdin",
        action="store_true",
        help="liest Python-Code aus stdin und behandelt ihn als Snippet",
    )
    parser.add_argument(
        "--json-output",
        nargs="?",
        const=DEFAULT_JSON_REPORT_NAME,
        metavar="DATEI.json",
        help=(
            "schreibt zusätzlich einen JSON-Report im Schema "
            f"{JSON_SCHEMA_VERSION}; ohne Wert wird {DEFAULT_JSON_REPORT_NAME} genutzt"
        ),
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Startet GUI oder CLI je nach Argumenten."""
    parser = build_cli_parser()
    args = parser.parse_args(argv)

    if args.file:
        return _run_cli_file(args.file, args.json_output)
    if args.project:
        return _run_cli_project(args.project, args.json_output)
    if args.stdin:
        return _run_cli_snippet(sys.stdin.read(), args.json_output)

    create_gui()
    return EXIT_OK


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    sys.exit(main())
