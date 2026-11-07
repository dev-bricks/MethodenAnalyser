# Store Listing — MethodenAnalyser

## Deutsch

### Kurzbeschreibung (max 100 Zeichen)
Statischer Python-Code-Analyser für ungenutzte Imports, Definitionen und Code-Duplikate.

### Beschreibung (max 10.000 Zeichen)
MethodenAnalyser ist ein spezialisierter statischer Code-Analyser für Python-Projekte. Er nutzt den Abstract Syntax Tree (AST) für präzise Analysen ohne Regex-Heuristiken und spürt ungenutzte Imports, tote Funktionen sowie Code-Duplikate zuverlässig auf.

**Was MethodenAnalyser bietet:**

- AST-basierte Analyse: Präzise statische Analyse über den Python Abstract Syntax Tree ohne externe Abhängigkeiten
- Import-Tracking: Erkennt genutzte und ungenutzte Imports zuverlässig mit sicherem Auto-Fix und atomarer Backup-Sicherung
- Methoden-Katalog: Listet alle Funktionen, Methoden und Klassen mit Verwendungsstatus auf
- Duplikat-Erkennung: Findet ähnliche Code-Blöcke mit konfigurierbarem Schwellwert (Standard: 80%)
- Framework-Erkennung: Erkennt implizite Nutzung durch GUI-Frameworks und Bibliotheken (Tkinter, requests, asyncio u. a.)
- Callback-Erkennung: Identifiziert Callback-Funktionen korrekt als genutzt
- Multi-File-Analyse: Rekursive Projektanalyse mit aggregiertem Strukturreport
- Headless-CLI & JSON-Export: Automatisierbar via Kommandozeile mit standardisiertem Exportformat (methodenanalyser-report-v1.json)
- Lokale Ausführung: 100% Offline-Betrieb ohne Cloud-Zwang und Datenabfluss

**Für wen ist MethodenAnalyser?**

Python-Entwickler, Code-Reviewer und Teams, die ihren Code aufräumen, toten Code entfernen und Refactorings vorbereiten möchten.

### Schlüsselwörter
Code-Analyse, AST-Parser, Ungenutzte Imports, Duplikat-Erkennung, Refactoring, Clean Code, Entwickler-Tools

### Kategorie
Developer Tools

---

## English

### Short Description (max 100 chars)
Static Python code analyzer detecting unused imports, dead definitions, and code duplicates.

### Description (max 10,000 chars)
MethodenAnalyser is a specialized static code analyzer designed for Python projects. It utilizes the Abstract Syntax Tree (AST) for precise static analysis without regex heuristics, reliably identifying unused imports, dead functions, and code duplicates.

**What MethodenAnalyser offers:**

- AST-based Analysis: Precise static analysis via standard Python AST with zero external dependencies
- Import Tracking: Accurately detects unused imports with safe auto-fix capabilities and atomic backup preservation
- Method Catalog: Comprehensive inventory of all functions, methods, and classes with usage indicators
- Duplicate Detection: Discovers similar code blocks with configurable similarity thresholds (default: 80%)
- Framework Awareness: Recognizes implicit bindings in GUI frameworks and standard libraries (Tkinter, requests, asyncio, etc.)
- Callback Detection: Properly flags callback routines as active code
- Multi-File Analysis: Recursively scans entire projects and produces consolidated summary reports
- Headless CLI & JSON Export: Full CLI integration and machine-readable exports (methodenanalyser-report-v1.json)
- Local-First Architecture: 100% private, offline execution without cloud dependency or telemetry

**Who is MethodenAnalyser for?**

Python developers, software architects, and engineering teams cleaning up legacy codebases, preparing refactoring milestones, and enforcing clean code standards.

### Keywords
code analysis, AST parser, unused imports, duplicate detection, refactoring, clean code, developer tools

### Category
Developer Tools

---

## Español

### Descripción corta (máx. 100 caracteres)
Analizador estático de Python para detectar importaciones no usadas, código muerto y duplicados.

### Descripción (máx. 10.000 caracteres)
MethodenAnalyser es un analizador estático especializado para proyectos Python. Analiza el código fuente con precisión mediante el árbol de sintaxis abstracta (AST), detecta importaciones no utilizadas y funciones inactivas, y localiza duplicados de código.

**Características principales:**

- Análisis estático basado en AST sin dependencias de terceros
- Detección precisa de importaciones no utilizadas con corrección automática y respaldo seguro
- Catálogo completo de métodos, funciones y clases con estado de utilización
- Detección de bloques de código similares con umbral de similitud configurable
- Reconocimiento de frameworks para funciones callback (Tkinter, requests, asyncio, etc.)
- Análisis recursivo de proyectos con múltiples archivos e informes agregados
- Modo CLI sin interfaz gráfica y exportación JSON estandarizada (methodenanalyser-report-v1.json)
- Ejecución 100% local y confidencial sin envío de datos a la nube

### Palabras clave
analisis de codigo, parser AST, importaciones, deteccion duplicados, refactorizacion, codigo limpio, herramientas desarrollo

### Categoría
Developer Tools

---

## 简体中文

### 简短描述（最多100字符）
用于检测未使用的导入、无用定义和代码重复的静态Python代码分析工具。

### 详细描述（最多10,000字符）
MethodenAnalyser 是一款专为 Python 代码库设计的本地静态代码分析工具。它通过抽象语法树（AST）实现精准语法分析，可迅速定位未使用的导入包、废弃函数以及代码重复段落。

**核心功能：**

- 基于 AST 的高精度静态代码分析，无外部第三方依赖
- 可靠检测未使用的 import，并支持带原子备份的安全自动修复
- 自动提取并整理所有函数、方法与类定义的使用状态目录
- 基于相似度算法的代码重复段落检测，支持自定义判定阈值
- 框架感知能力，自动识别回调函数（如 Tkinter、requests、asyncio 等）
- 支持对完整多文件 Python 工程进行递归扫描并输出聚合摘要报告
- 纯命令行 Headless 运行模式与机器可读的 JSON 报表导出（methodenanalyser-report-v1.json）
- 100% 本地运算，零网络请求与数据回传，严密保护代码隐私

### 关键词
代码分析, AST解析器, 未使用的导入, 重复代码检测, 代码重构, 整洁代码, 开发工具

### 类别
Developer Tools

---

## 日本語

### 短い説明（最大100文字）
未使用インポート、不要な定義、コード重複を検出するPython静的解析ツール。

### 説明（最大10,000文字）
MethodenAnalyser は、Python プロジェクト専用に設計されたローカル完結型の静的コード解析ツールです。抽象構文木（AST）を用いてソースコードを正確に解析し、未使用のインポート、到達不能な関数、コードの重複箇所を的確に特定します。

**主な機能：**

- 外部依存関係なしで動作する、高精度な AST ベースの静的コード解析
- 未使用インポートの正確な検出と、バックアップを保持する安全な自動修正機能
- クラス、関数、メソッドを網羅した詳細な利用状況カタログ
- しきい値調整可能な類似コードブロックおよび重複コード検出
- フレームワーク認識によるコールバック関数の自動判定（Tkinter、requests、asyncio など）
- 複数ファイルで構成されるプロジェクト全体の再帰的解析とサマリーレポート生成
- ヘッドレス CLI モードおよび機械可読な JSON レポート出力（methodenanalyser-report-v1.json）
- クラウド通信を一切行わない 100% ローカルのプライバシー保護設計

### キーワード
コード解析, ASTパーサー, 未使用インポート, 重複検出, リファクタリング, クリーンコード, 開発ツール

### カテゴリ
Developer Tools

---

## Русский

### Краткое описание (макс. 100 символов)
Статический анализатор Python для поиска неиспользуемых импортов, определений и дубликатов.

### Описание (макс. 10.000 символов)
MethodenAnalyser — специализированный инструмент статического анализа для проектов на Python. Он точно анализирует исходный код с помощью абстрактного синтаксического дерева (AST), выявляя неиспользуемые импорты, неактивные функции и дубликаты кода.

**Основные возможности:**

- Высокоточный статический анализ на базе AST без сторонних зависимостей
- Надежное обнаружение неиспользуемых импортов с безопасным авто-исправлением и созданием резервной копии
- Полный каталог методов, функций и классов с детальным статусом использования
- Распознавание похожих фрагментов и дубликатов кода с настраиваемым порогом сходства
- Распознавание неявного вызова функций обратного вызова в популярных фреймворках (Tkinter, requests, asyncio и др.)
- Рекурсивный анализ многофайловых проектов со сводным структурированным отчетом
- Консольный режим CLI и экспорт машиночитаемых отчетов в формате JSON (methodenanalyser-report-v1.json)
- Полностью локальная обработка без сетевых вызовов и передачи данных

### Ключевые слова
анализ кода, AST парсер, неиспользуемый импорт, поиск дубликатов, рефакторинг, чистый код, инструменты разработчика

### Категория
Developer Tools
