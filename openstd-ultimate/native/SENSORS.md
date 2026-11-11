# Sensores — primera integración real

El módulo `sensors.py` consulta fuentes locales de solo lectura:

- **Windows**: porcentaje de carga y estado de batería mediante Win32_Battery; estado informado por Windows de unidades físicas mediante Get-PhysicalDisk.
- **Linux**: batería y desgaste cuando existen los campos en /sys/class/power_supply; zonas térmicas disponibles en /sys/class/thermal.
- **Temperatura Windows**: aún **no disponible**. No se inventan datos ni se usa una temperatura genérica como si fuera la del CPU.
- **SMART detallado**: aún **no disponible**. HealthStatus de Windows no equivale a SMART ni certifica la salud del SSD.
- **Pruebas de estrés**: no implementadas.

Ejecutar: `python -c "import json,sensors; print(json.dumps(sensors.collect_sensors(),indent=2))"`

Pruebas: `python -m unittest discover -s . -p "test_*.py" -v`

En futuras iteraciones se puede integrar LibreHardwareMonitor con permiso explícito y comprobar su licencia, y smartctl con consentimiento para consultas SMART. No es recomendable interpretar una lectura ausente como valor cero.
