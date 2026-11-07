Short Description:
Static Python code analyzer detecting unused imports, dead definitions, and code duplicates.

Description:
MethodenAnalyser is a specialized static code analyzer designed for Python codebases. It performs precise AST-based analysis without regex heuristics, identifies unused imports and dead functions, and detects code duplicates.

Key Features:
- AST-based static analysis running on standard Python without third-party dependencies
- Reliable unused import detection with safe auto-fix and atomic backup preservation
- Comprehensive catalog of methods, functions, and classes with usage indicators
- Code similarity and duplicate block detection with configurable similarity thresholds
- Framework awareness recognizing callbacks and implicit bindings (Tkinter, requests, asyncio, etc.)
- Recursive multi-file project analysis producing structured summary reports
- Headless CLI interface and machine-readable JSON export (methodenanalyser-report-v1.json)
- 100% local and private execution with zero data egress

Target Audience:
Python developers, code reviewers, and engineering teams cleaning up legacy code, preparing refactoring milestones, and enforcing clean code standards. License: MIT.

Keywords:
code analysis, AST parser, unused imports, duplicate detection, refactoring, clean code, developer tools
