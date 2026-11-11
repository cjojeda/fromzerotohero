# Fase 2 — Inventario real, local y de solo lectura

Este módulo obtiene **datos reales de inventario** de Windows y Linux mediante Python estándar, sin dependencias de terceros.

## Ejecutar
1. Instalar Python 3.10 o superior.
2. Abrir una terminal en `openstd-ultimate/native`.
3. Ejecutar `python collector.py --output inventario.json`.
4. Abrir `openstd-ultimate/index.html`, seleccionar **Importar inventario JSON** y elegir el archivo generado.

## Validar
`python -m unittest discover -s . -p "test_*.py"`

## Alcance
Se leen versión del sistema, arquitectura, procesador, núcleos lógicos, RAM y capacidad libre del volumen principal. Los valores pueden estar ausentes si el sistema bloquea el acceso. No se realizan pruebas de estabilidad, SMART, batería o sensores, ni se calcula un veredicto PASA/FALLA.

## Privacidad
La exportación es local. El JSON puede incluir información técnica del equipo. Revisarlo antes de compartirlo. No ejecutar scripts desconocidos como administrador.

## Siguientes pasos
Adaptador nativo para sensores y SMART, pruebas de memoria/CPU con límites de seguridad, firma del instalador, pruebas en hardware real y consentimiento informado.
