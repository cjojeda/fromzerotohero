#!/usr/bin/env python3
"""OpenSTD Ultimate: collector de inventario local, solo lectura (Python 3.10+)."""
import argparse, datetime, json, os, platform, shutil, subprocess, sys
from pathlib import Path

def command(args, timeout=8):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=timeout,check=False,encoding="utf-8",errors="replace")
        return p.stdout.strip() if p.returncode==0 else None
    except (OSError,subprocess.TimeoutExpired):
        return None

def memory():
    if sys.platform.startswith("linux"):
        try:
            info={}
            for line in Path("/proc/meminfo").read_text().splitlines():
                k,v=line.split(":",1)
                info[k]=int(v.strip().split()[0])*1024
            return {"total_bytes":info.get("MemTotal"),"available_bytes":info.get("MemAvailable")}
        except (OSError,ValueError,IndexError): pass
    if sys.platform=="win32":
        out=command(["powershell","-NoProfile","-NonInteractive","-Command","(Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json -Compress)"])
        try:
            x=json.loads(out or "{}")
            return {"total_bytes":int(x["TotalVisibleMemorySize"])*1024,"available_bytes":int(x["FreePhysicalMemory"])*1024}
        except (KeyError,ValueError,TypeError): pass
    return {"total_bytes":None,"available_bytes":None}

def disks():
    result=[]
    for root in ([Path(os.environ.get("SystemDrive","C:")+"\\")] if sys.platform=="win32" else [Path("/")]):
        try:
            d=shutil.disk_usage(root)
            result.append({"mount":str(root),"total_bytes":d.total,"free_bytes":d.free})
        except OSError: pass
    return result

def collect():
    return {"schema_version":"1.0","collected_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "source":"openstd-ultimate-local-collector","kind":"inventory_only",
      "system":{"os":platform.system(),"release":platform.release(),"version":platform.version(),"architecture":platform.machine(),"cpu":platform.processor() or None,"logical_cores":os.cpu_count()},
      "memory":memory(),"filesystems":disks(),
      "tests":[],"sensors":{},"health_verdict":None,
      "limitations":["No se realizaron pruebas de estrés ni SMART","No se consultaron sensores térmicos","La capacidad libre no equivale a salud del disco"]}

def main():
    parser=argparse.ArgumentParser(description="Exportar inventario local de hardware sin cambios al sistema")
    parser.add_argument("--output",default="openstd-inventory.json")
    args=parser.parse_args()
    path=Path(args.output).expanduser()
    if path.exists():
        parser.error("El archivo ya existe; elija otro nombre con --output")
    path.write_text(json.dumps(collect(),ensure_ascii=False,indent=2),encoding="utf-8")
    print("Inventario guardado en:",path.resolve())
if __name__=="__main__":main()
