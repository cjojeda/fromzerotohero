"""Comprobaciones rápidas no destructivas; NO son tests de estrés."""
import os
import shutil
import socket
from pathlib import Path

def run_basic_checks():
    checks=[]
    root=Path(os.environ.get("SystemDrive","C:")+"\\") if os.name=="nt" else Path("/")
    try:
        disk=shutil.disk_usage(root)
        ratio=disk.free/disk.total if disk.total else 0
        status="ADVERTENCIA" if ratio<0.10 else "INFORMATIVO"
        checks.append({"name":"Espacio libre del sistema","status":status,"detail":f"{ratio:.1%} disponible; no evalúa SMART"})
    except OSError as exc:
        checks.append({"name":"Espacio libre del sistema","status":"NO DISPONIBLE","detail":str(exc)})
    try:
        name=socket.gethostname()
        checks.append({"name":"Identificación local","status":"INFORMATIVO","detail":"Nombre del equipo disponible" if name else "Sin nombre"})
    except OSError:
        checks.append({"name":"Identificación local","status":"NO DISPONIBLE","detail":"No se pudo consultar"})
    return checks
