"""Sensores de solo lectura. Los valores ausentes se representan como null."""
import json
import os
from pathlib import Path
import platform
import subprocess

def _run(argv, timeout=7):
    try:
        p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout,check=False,encoding="utf-8",errors="replace")
        return p.stdout.strip() if p.returncode==0 else None
    except (OSError,subprocess.TimeoutExpired):
        return None

def _ps(script):
    out=_run(["powershell","-NoProfile","-NonInteractive","-Command",script])
    if not out:return None
    try:return json.loads(out)
    except (ValueError,TypeError):return None

def battery():
    if platform.system()=="Windows":
        raw=_ps("Get-CimInstance Win32_Battery | Select-Object Name,EstimatedChargeRemaining,BatteryStatus | ConvertTo-Json -Compress")
        if not raw:return {"available":False,"source":"Win32_Battery"}
        items=raw if isinstance(raw,list) else [raw]
        return {"available":True,"source":"Win32_Battery","batteries":[{"name":x.get("Name"),"charge_percent":x.get("EstimatedChargeRemaining"),"status_code":x.get("BatteryStatus")} for x in items if isinstance(x,dict)],"wear_percent":None}
    if platform.system()=="Linux":
        items=[]
        for base in Path("/sys/class/power_supply").glob("*"):
            try:
                if (base/"type").read_text().strip().lower()!="battery":continue
                def number(key):
                    try:return int((base/key).read_text().strip())
                    except (OSError,ValueError):return None
                full=number("energy_full") or number("charge_full")
                design=number("energy_full_design") or number("charge_full_design")
                wear=round(100*(1-full/design),1) if full is not None and design and design>0 else None
                items.append({"name":base.name,"charge_percent":number("capacity"),"wear_percent":wear})
            except OSError:continue
        return {"available":bool(items),"source":"Linux sysfs","batteries":items}
    return {"available":False,"source":"unsupported"}

def thermal():
    if platform.system()=="Linux":
        sensors=[]
        for base in Path("/sys/class/thermal").glob("thermal_zone*"):
            try:
                raw=int((base/"temp").read_text().strip())
                temp=raw/1000
                if not -30<=temp<=150:continue
                label=(base/"type").read_text().strip() if (base/"type").exists() else base.name
                sensors.append({"label":label,"celsius":round(temp,1)})
            except (OSError,ValueError):continue
        return {"available":bool(sensors),"source":"Linux sysfs","sensors":sensors}
    return {"available":False,"source":"not configured","sensors":[]}

def disks():
    if platform.system()=="Windows":
        raw=_ps("Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus,MediaType,Size | ConvertTo-Json -Compress")
        if raw is None:return {"available":False,"source":"Get-PhysicalDisk","devices":[]}
        items=raw if isinstance(raw,list) else [raw]
        return {"available":True,"source":"Get-PhysicalDisk","devices":[{"name":x.get("FriendlyName"),"health_status":x.get("HealthStatus"),"operational_status":x.get("OperationalStatus"),"media_type":x.get("MediaType"),"size_bytes":x.get("Size")} for x in items if isinstance(x,dict)],"smart_attributes_available":False}
    return {"available":False,"source":"not configured","devices":[],"smart_attributes_available":False}

def collect_sensors():
    return {"schema_version":"1.0","kind":"read_only_sensor_snapshot","battery":battery(),"thermal":thermal(),"disks":disks(),
            "limitations":["El estado de Get-PhysicalDisk no es un análisis SMART completo","No se inventan temperaturas cuando el sistema no expone sensores","La batería puede no exponer desgaste ni ciclos","No se realizan pruebas de estrés"]}
