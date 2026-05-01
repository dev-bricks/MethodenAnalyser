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
from typing import Set, Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from functools import lru_cache

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
        # NEU: Track Modul.Attribut Zugriffe
        self.module_attribute_calls: Dict[str, Set[str]] = collections.defaultdict(set)
        self.imported_modules: Set[str] = set()  # Nur Modulnamen (für import X)

    def visit_Call(self, node: ast.Call) -> None:
        """Verarbeitet Funktionsaufrufe und erkennt Modul-Attribut-Zugriffe."""
        if isinstance(node.func, ast.Attribute):
            # Attribut-Aufruf: obj.method()
            attr_name = node.func.attr
            self.calls.add(attr_name)
            
            # Prüfe ob es ein Modul.Attribut Zugriff ist
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                self.module_attribute_calls[module_name].add(attr_name)
                
        elif isinstance(node.func, ast.Name):
            # Direkter Aufruf: function()
            self.calls.add(node.func.id)
            
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Verarbeitet Attribut-Zugriffe (auch ohne Call)."""
        # z.B. threading.Lock (ohne Klammern)
        if isinstance(node.value, ast.Name):
            module_name = node.value.id
            attr_name = node.attr
            self.module_attribute_calls[module_name].add(attr_name)
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
            # NEU: Track auch Modulnamen für Attribut-Zugriff
            if not alias.asname:
                self.imported_modules.add(module_base)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Verarbeitet From-Import-Statements und trackt importierte Namen."""
        if node.module:
            module_base = node.module.split(".")[0]
            self.imports.append(module_base)
        
        # Füge die importierten Namen hinzu
        for alias in node.names:
            # Überspringe Wildcard-Imports
            if alias.name == '*':
                continue
            
            import_name = alias.asname if alias.asname else alias.name
            self.import_names.add(import_name)
            self.imported_definitions.add(import_name)

    def visit_Name(self, node: ast.Name) -> None:
        """Verarbeitet Namensreferenzen."""
        self.used_names.add(node.id)
        self.generic_visit(node)


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

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
            # Nur String-Matches (Methodennamen) hinzufügen
            for match in matches:
                if isinstance(match, str) and match:
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
        Text wird nur gekuerzt wenn er laenger als 50 Zeichen ist.
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


def get_available_module_attributes(analyzer: 'CodeAnalyzer') -> Set[str]:
    """
    Ermittelt alle Attribute die durch importierte Module verfügbar sind.
    
    Wenn z.B. 'threading' importiert ist und Code 'threading.Lock()' verwendet,
    dann sollte 'Lock' nicht als fehlende Definition gemeldet werden.
    
    Args:
        analyzer: CodeAnalyzer-Instanz mit Import- und Verwendungs-Informationen
        
    Returns:
        Set aller durch Module verfügbar gemachten Attributnamen
    """
    available_attrs = set()
    
    # Durchlaufe alle Modul.Attribut Zugriffe
    for module_name, attributes in analyzer.module_attribute_calls.items():
        # Prüfe ob das Modul importiert wurde
        if module_name in analyzer.imported_modules or module_name in analyzer.import_names:
            # Prüfe ob wir die Exports dieses Moduls kennen
            if module_name in STDLIB_EXPORTS:
                # Nur valide Attribute hinzufügen
                for attr in attributes:
                    if attr in STDLIB_EXPORTS[module_name]:
                        available_attrs.add(attr)
            else:
                # Modul importiert aber unbekannt → akzeptiere alle Attribute
                # (um False Positives zu vermeiden)
                available_attrs.update(attributes)
    
    return available_attrs


# ============================================================================
# HAUPTANALYSE
# ============================================================================

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
                "latin-1 Fallback wurde verwendet -- Analyse-Ergebnisse koennen Artefakte enthalten.",
                UnicodeWarning,
                stacklevel=2,
            )
        except Exception as e:
            raise RuntimeError(f"Fehler beim Lesen der Datei: {e}")
    except Exception as e:
        raise RuntimeError(f"Fehler beim Lesen der Datei: {e}")

    # Code parsen (nur einmal!)
    try:
        tree = ast.parse(code)
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
    unused_imports = analyzer.import_names - analyzer.used_names

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
        calls - BUILTINS - framework_and_widgets
    )

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


def _extract_typehints(tree: ast.AST) -> Set[str]:
    """
    Extrahiert verwendete Type-Hints aus bereits geparsten AST.
    
    Args:
        tree: Bereits geparster AST
        
    Returns:
        Set der verwendeten Type-Hint-Namen
    """
    hints = set()
    try:
        for node in ast.walk(tree):
            # Variable Annotationen
            if isinstance(node, ast.AnnAssign) and isinstance(node.annotation, ast.Name):
                hints.add(node.annotation.id)
            # Funktionsparameter Annotationen
            elif isinstance(node, ast.arg) and node.annotation:
                if isinstance(node.annotation, ast.Name):
                    hints.add(node.annotation.id)
            # Funktions-Return-Annotationen
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns and isinstance(node.returns, ast.Name):
                    hints.add(node.returns.id)
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
        report.append("\n🔧 DYNAMISCHE AUFRUFE\n")
        report.append("-" * 70 + "\n")
        report.append(f"Erkannte Patterns: {', '.join(result.dynamic_usage)}\n")
        if result.dynamic_methods:
            report.append(f"Extrahierte Methoden: {', '.join(result.dynamic_methods)}\n")
        report.append("\n")

    # Namens-Matches
    if result.name_matches:
        report.append("\n💡 ÄHNLICHE NAMEN (mögliche Tippfehler)\n")
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
        report.append(f"\n📥 IMPORTIERTE DEFINITIONEN\n")
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
        report.append(f"\n🔗 MODUL-ATTRIBUT VERWENDUNG\n")
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
    output_widget.insert(tk.END, f"📄 Analysierte Datei: {os.path.basename(path)}\n\n")
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
        output_widget.insert(tk.END, f"\n[WARNUNG] Keine Schreibberechtigung fuer Export")
        messagebox.showwarning("Export-Fehler", "Keine Schreibberechtigung")
    except Exception as e:
        output_widget.insert(tk.END, f"\n[WARNUNG] Export-Fehler: {e}")
        messagebox.showwarning("Export-Fehler", str(e))




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
        # Datei lesen
        with open(_last_analysis_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # AST parsen um Import-Zeilen zu finden
        with open(_last_analysis_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        
        # Import-Zeilen markieren die entfernt werden sollen
        lines_to_remove = set()
        unused_set = set(_last_analysis_result.unused_imports)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # import x, y, z
                names = [alias.asname or alias.name for alias in node.names]
                if all(name in unused_set for name in names):
                    lines_to_remove.add(node.lineno)
            elif isinstance(node, ast.ImportFrom):
                # from x import y, z
                names = [alias.asname or alias.name for alias in node.names]
                if all(name in unused_set for name in names):
                    lines_to_remove.add(node.lineno)
        
        if not lines_to_remove:
            messagebox.showinfo("Info", "Keine vollständig ungenutzten Import-Zeilen gefunden.\n(Teilweise genutzte Imports müssen manuell bearbeitet werden)")
            return
        
        # Backup erstellen
        backup_path = _last_analysis_path + ".bak"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        # Neue Datei ohne ungenutzte Imports
        new_lines = [line for i, line in enumerate(lines, 1) if i not in lines_to_remove]
        
        with open(_last_analysis_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        
        # Ausgabe
        output_widget.insert(tk.END, f"\n\n[OK] AUTO-FIX ERFOLGREICH\n")
        output_widget.insert(tk.END, f"Entfernte Zeilen: {sorted(lines_to_remove)}\n")
        output_widget.insert(tk.END, f"Backup erstellt: {backup_path}\n")
        output_widget.insert(tk.END, f"\nBitte Datei erneut analysieren zur Überprüfung.")
        
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
            if pattern in str(py_file):
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
    all_duplicate_imports: Dict[str, List[str]]
    file_results: Dict[str, AnalysisResult]


def analyze_project(folder_path: str, progress_callback=None) -> ProjectAnalysisResult:
    """Analysiert alle Python-Dateien in einem Projektordner."""
    python_files = collect_python_files(folder_path)
    files_with_errors, file_results = [], {}
    all_unused_imports, all_unused_defs = {}, {}
    all_missing_defs, all_duplicate_imports = {}, {}
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
            except (IOError, OSError):
                pass
            rel_path = os.path.relpath(file_path, folder_path)
            if result.unused_imports:
                all_unused_imports[rel_path] = result.unused_imports
            if result.unused_defs:
                all_unused_defs[rel_path] = result.unused_defs
            if result.missing_defs:
                all_missing_defs[rel_path] = result.missing_defs
            if result.duplicate_imports:
                all_duplicate_imports[rel_path] = result.duplicate_imports
        except Exception as e:
            files_with_errors.append((file_path, str(e)))
    
    return ProjectAnalysisResult(
        folder_path=folder_path, files_analyzed=len(python_files) - len(files_with_errors),
        files_with_errors=files_with_errors, total_lines=total_lines,
        total_defs=total_defs, total_imports=total_imports,
        all_unused_imports=all_unused_imports, all_unused_defs=all_unused_defs,
        all_missing_defs=all_missing_defs, all_duplicate_imports=all_duplicate_imports,
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
    
    score = max(0, 100 - total_ui * 2 - total_ud * 2)
    report.append(f"\n{'=' * 70}\nSCORE: {score}/100\n{'=' * 70}\n")
    return "".join(report)


def run_project_analysis(output_widget: scrolledtext.ScrolledText) -> None:
    """Ordner-Dialog und Projekt-Analyse."""
    folder_path = filedialog.askdirectory(title="Projektordner auswaehlen")
    if not folder_path:
        return
    
    output_widget.delete("1.0", tk.END)
    output_widget.insert(tk.END, f"Analysiere: {folder_path}\n\n")
    output_widget.update()
    
    def progress_cb(cur, tot, fp):
        output_widget.insert(tk.END, f"[{cur}/{tot}] {os.path.basename(fp)}\n")
        output_widget.see(tk.END)
        output_widget.update()
    
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
    
    # Analyse-Button
    btn = tk.Button(
        button_frame,
        text="📂 Datei analysieren",
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
        text="ℹ️  Info",
        command=lambda: messagebox.showinfo(
            "Python Code Analyzer",
            "Python Code Analyzer v2.0\n\n"
            "Analysiert Python-Dateien auf:\n"
            "• Fehlende Definitionen\n"
            "• Ungenutzte Definitionen\n"
            "• Ungenutzte Imports\n"
            "• Dynamische Aufrufe\n"
            "• Import-Scope-Probleme\n\n"
            "© 2024 - Optimierte Version"
        ),
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
        text="🔧 Auto-Fix Imports",
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
        text="Projekt analysieren",
        command=lambda: run_project_analysis(output),
        bg="#9C27B0",
        fg="white",
        font=("Arial", 10),
        padx=15,
        pady=10,
        cursor="hand2"
    )
    project_btn.pack(side=tk.LEFT, padx=5)


    
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
    welcome_text = (
        "Willkommen beim Python Code Analyzer!\n\n"
        "Klicken Sie auf 'Datei analysieren', um eine Python-Datei zu untersuchen.\n\n"
        "Die Analyse umfasst:\n"
        "• Fehlende und ungenutzte Definitionen\n"
        "• Import-Analyse und -Optimierung\n"
        "• Dynamische Methodenaufrufe\n"
        "• Mögliche Tippfehler\n"
    )
    output.insert(tk.END, welcome_text)
    
    root.mainloop()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    create_gui()
