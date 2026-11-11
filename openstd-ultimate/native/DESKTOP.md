# OpenSTD Ultimate Desktop Alpha

## Funciones
- Interfaz nativa de Windows/Linux con Tkinter.
- Inventario real mediante `collector.py`.
- Comprobación no destructiva del espacio libre del sistema (advertencia por debajo de 10 %).
- Exportación JSON local.
- Procesamiento en segundo hilo para evitar bloquear la interfaz.

**No realiza pruebas de estrés, no lee SMART, no mide temperaturas ni declara un equipo libre de fallas.**

## Ejecutar localmente
Desde esta carpeta: `python desktop.py`. Requiere Python 3.10+ con Tkinter.

## Ejecutar pruebas
`python -m unittest discover -s . -p "test_*.py" -v`

## Crear EXE
El workflow `.github/workflows/openstd-windows.yml` ejecuta pruebas y empaqueta la aplicación en un artefacto de GitHub Actions. También se puede ejecutar manualmente desde Actions.

El EXE aún no está firmado digitalmente. Windows SmartScreen podría advertir sobre ejecutables desconocidos. Verificar el origen y no ejecutar como administrador.

## Pendiente
Pruebas reales de sensores/SMART, estabilidad y RAM, validación en hardware real, permisos, firma de código y auditoría de dependencias.
