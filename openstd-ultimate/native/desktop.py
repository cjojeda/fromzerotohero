"""OpenSTD Ultimate Desktop — inventario y diagnóstico básico de solo lectura."""
import json
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from collector import collect
from diagnostics import run_basic_checks
from sensors import collect_sensors

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenSTD Ultimate — Desktop Alpha")
        self.geometry("980x650")
        self.minsize(720,500)
        self.configure(bg="#0c1424")
        self.events=queue.Queue()
        self.report=None
        self._build()
        self.after(120,self._poll)

    def _build(self):
        style=ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",background="#14233a",fieldbackground="#14233a",foreground="#eef4ff",rowheight=32)
        style.configure("Treeview.Heading",background="#223550",foreground="white",font=("Segoe UI",10,"bold"))
        sidebar=tk.Frame(self,bg="#111e33",width=205)
        sidebar.pack(side="left",fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar,text="◈ OpenSTD Ultimate",fg="#5fe1b5",bg="#111e33",font=("Segoe UI",15,"bold")).pack(pady=(28,24))
        for label,callback in [("Actualizar inventario",self.refresh),("Diagnóstico básico",self.check),("Leer sensores",self.read_sensors),("Exportar JSON",self.export)]:
            tk.Button(sidebar,text=label,command=callback,bg="#213653",fg="white",relief="flat",font=("Segoe UI",10),pady=12).pack(fill="x",padx=14,pady=6)
        tk.Label(sidebar,text="ALPHA · SIN PRUEBAS DE ESTRÉS",bg="#111e33",fg="#a6b8d0",wraplength=170,font=("Segoe UI",9)).pack(side="bottom",pady=20)
        body=tk.Frame(self,bg="#0c1424")
        body.pack(side="left",fill="both",expand=True,padx=25,pady=25)
        tk.Label(body,text="Centro de diagnóstico",bg="#0c1424",fg="white",font=("Segoe UI",22,"bold")).pack(anchor="w")
        self.status=tk.StringVar(value="Listo. Seleccioná una acción para comenzar.")
        tk.Label(body,textvariable=self.status,bg="#0c1424",fg="#91acc8",font=("Segoe UI",10),wraplength=650).pack(anchor="w",pady=(8,18))
        self.table=ttk.Treeview(body,columns=("value","status"),show="headings")
        self.table.heading("value",text="Componente / información")
        self.table.heading("status",text="Resultado")
        self.table.column("value",width=290,anchor="w")
        self.table.column("status",width=320,anchor="w")
        self.table.pack(fill="both",expand=True)
        tk.Label(body,text="No certifica la ausencia de fallas. No se ejecutan cargas intensivas ni cambios en el sistema.",bg="#0c1424",fg="#e9bf79",wraplength=670).pack(anchor="w",pady=14)

    def _run(self,fn):
        self.status.set("Procesando…")
        def work():
            try:self.events.put(("ok",fn()))
            except Exception as exc:self.events.put(("error",str(exc)))
        threading.Thread(target=work,daemon=True).start()

    def refresh(self):
        self._run(lambda:{"inventory":collect(),"checks":[]})
    def check(self):
        self._run(lambda:{"inventory":collect(),"checks":run_basic_checks()})

    def read_sensors(self):
        self._run(lambda:{'inventory':collect(),'checks':[],'sensor_snapshot':collect_sensors()})

    def _poll(self):
        try:
            while True:
                kind,value=self.events.get_nowait()
                if kind=="error":
                    self.status.set("Error: "+value)
                    messagebox.showerror("OpenSTD",value)
                else:self._show(value)
        except queue.Empty:pass
        self.after(120,self._poll)

    def _show(self,report):
        self.report=report
        self.table.delete(*self.table.get_children())
        data=report["inventory"]
        s=data["system"]
        rows=[("Sistema",str(s.get("os") or "N/D")+" "+str(s.get("release") or "")),("Arquitectura",s.get("architecture") or "N/D"),("Procesador",s.get("cpu") or "N/D"),("Núcleos lógicos",s.get("logical_cores") or "N/D")]
        mem=data["memory"]
        if isinstance(mem.get("total_bytes"),int):rows.append(("RAM instalada",f'{mem["total_bytes"]/1073741824:.2f} GiB'))
        for disk in data["filesystems"]:
            rows.append(("Espacio libre "+disk["mount"],f'{disk["free_bytes"]/1073741824:.2f} GiB'))
        for c in report["checks"]:rows.append((c["name"],c["status"]+" — "+c["detail"]))
        snapshot=report.get("sensor_snapshot")
        if snapshot:
            for b in snapshot["battery"].get("batteries",[]):
                rows.append(("Batería "+str(b.get("name") or ""),str(b.get("charge_percent") if b.get("charge_percent") is not None else "N/D")+" % carga"))
                if b.get("wear_percent") is not None:
                    rows.append(("Desgaste batería",str(b["wear_percent"])+" %"))
            for sensor in snapshot["thermal"].get("sensors",[]):
                rows.append(("Temperatura "+str(sensor["label"]),str(sensor["celsius"])+" °C"))
            for disk in snapshot["disks"].get("devices",[]):
                rows.append(("Estado unidad "+str(disk.get("name") or ""),str(disk.get("health_status") or "N/D")+" (no SMART completo)"))
            for key,label in [("thermal","Temperaturas"),("battery","Batería"),("disks","Estado de unidades")]:
                if not snapshot[key]["available"]:
                    rows.append((label,"No disponible"))
        for a,b in rows:self.table.insert("","end",values=(a,b))
        self.status.set("Lectura terminada. Las comprobaciones básicas no sustituyen pruebas de hardware.")

    def export(self):
        if self.report is None:
            messagebox.showinfo("OpenSTD","Primero ejecutá un inventario o diagnóstico.")
            return
        path=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")],initialfile="openstd-report.json")
        if not path:return
        target=Path(path)
        if target.exists() and not messagebox.askyesno("Confirmar","¿Sobrescribir archivo existente?"):return
        try:
            target.write_text(json.dumps(self.report,ensure_ascii=False,indent=2),encoding="utf-8")
            self.status.set("Reporte guardado: "+str(target))
        except OSError as exc:messagebox.showerror("Error al guardar",str(exc))

if __name__=="__main__":
    App().mainloop()
