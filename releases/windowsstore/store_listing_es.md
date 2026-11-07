Descripción corta:
Analizador estático de Python para detectar importaciones no usadas, código muerto y duplicados.

Descripción:
MethodenAnalyser es un analizador estático especializado para proyectos Python. Analiza el código fuente con precisión mediante el árbol de sintaxis abstracta (AST), detecta importaciones no utilizadas y funciones inactivas, y localiza duplicados de código.

Características principales:
- Análisis estático basado en AST sin dependencias externas
- Detección precisa de importaciones no utilizadas con corrección automática y copia de seguridad
- Catálogo de métodos, funciones y clases con estado de utilización detallado
- Detección de bloques de código similares y duplicados con umbral configurable
- Reconocimiento de frameworks para funciones callback (Tkinter, requests, asyncio, etc.)
- Análisis recursivo de proyectos con múltiples archivos e informes estructurados
- Modo CLI sin interfaz gráfica y exportación JSON (methodenanalyser-report-v1.json)
- Ejecución 100% local y respetuosa con la privacidad sin conexión a la nube

Público objetivo:
Desarrolladores de Python, revisores de código y equipos de ingeniería que limpian bases de código heredadas y preparan refactorizaciones. Licencia: MIT.

Palabras clave:
analisis de codigo, parser AST, importaciones, deteccion duplicados, refactorizacion, codigo limpio, herramientas desarrollo
