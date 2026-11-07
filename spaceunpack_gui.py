#!/usr/bin/env python3
"""
SpaceUnpack - desktop app.  Extract an archive (all of it, or just the files you tick)
and delete it without needing double the disk space.
Needs spaceunpack.py in the same folder.  Looks best with the `sv-ttk` package installed
(the Windows build bundles it); follows the Windows light/dark setting.

Run:  python spaceunpack_gui.py [archive] [--auto] [--here] [--shrink] [--low-space]
"""
import os
import subprocess
import sys
import threading

import spaceunpack as su

MAX_LIST = 50000                                  # don't list absurdly large archives
CHECK = {"all": "\u2611", "none": "\u2610", "partial": "\u25a3"}
KIND_NAMES = {"zip": "ZIP archive", "tar": "TAR archive", "single": "compressed file",
              "external": "other format (needs 7-Zip or unrar installed)"}
LOGO_B64 = "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"


def human_size(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def system_is_dark():
    """True when Windows is set to dark app mode."""
    if not sys.platform.startswith("win"):
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        return winreg.QueryValueEx(key, "AppsUseLightTheme")[0] == 0
    except Exception:  # noqa: BLE001
        return False


def set_dark_titlebar(root, dark):
    if not sys.platform.startswith("win"):
        return
    try:
        import ctypes
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        for attr in (20, 19):                     # DWMWA_USE_IMMERSIVE_DARK_MODE (new / old id)
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)) == 0:
                break
    except Exception:  # noqa: BLE001
        pass


# --------------------------------------------------------------------------
# Background jobs (no GUI code in here)
# --------------------------------------------------------------------------
class Cancelled(Exception):
    pass


class _Worker(threading.Thread):
    """A thread that doubles as the `progress` object the extractors report to."""

    def __init__(self):
        super().__init__(daemon=True)
        self.fraction = 0.0
        self.label = ""
        self.result = None            # ("ok", value) | ("cancelled", None) | ("error", message)
        self.cancellable = True
        self._cancel = threading.Event()

    def update(self, frac, label=""):
        if self._cancel.is_set():
            raise Cancelled()
        self.fraction, self.label = frac, label

    def done(self):
        pass

    def cancel(self):
        if self.cancellable:
            self._cancel.set()


class Job(_Worker):
    """One extraction."""

    def __init__(self, path, dest, password, low_space, delete_after, shrink=False, only=None):
        super().__init__()
        self.path, self.dest = path, dest
        self.password, self.low_space, self.delete_after = password, low_space, delete_after
        self.shrink, self.only = shrink, only
        self.indeterminate = su.detect(path)[0] == "external"
        self.cancellable = not self.indeterminate     # an external 7z/unrar run can't be stopped

    def run(self):
        try:
            if self.low_space:
                ok, why = su.check_low_space(self.path, su.detect(self.path)[0])
                if not ok:
                    raise RuntimeError(f"Low-space mode isn't possible here: {why}")
            n = su.extract_archive(self.path, self.dest, self.password or None, self.low_space,
                                   self, shrink=self.shrink, only=self.only)
            if self.delete_after:
                os.remove(self.path)
            self.result = ("ok", n)
        except Cancelled:
            self.result = ("cancelled", None)
        except Exception as e:  # noqa: BLE001
            self.result = ("error", str(e))


class ListJob(_Worker):
    """Reads the file list of a tar-type archive (needs one pass over the whole file)."""

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            self.result = ("ok", su.list_entries(self.path, self))
        except Cancelled:
            self.result = ("cancelled", None)
        except Exception as e:  # noqa: BLE001
            self.result = ("error", str(e))


# --------------------------------------------------------------------------
# Checkable file tree (pure logic, no GUI)
# --------------------------------------------------------------------------
class FileModel:
    def __init__(self, entries):
        self.nodes, self.order, self.roots, self.file_ids = {}, [], [], []
        self.total_files = self.sel_total = 0
        folders = {}
        for name, size, is_dir in entries:
            parts = [p for p in name.split("/") if p not in ("", ".")]   # "./a.txt" -> a.txt
            if not parts:
                continue
            parent = None
            for depth in range(len(parts) if is_dir else len(parts) - 1):
                path = "/".join(parts[:depth + 1])
                if path not in folders:
                    folders[path] = self._new(parts[depth], parent, True, 0, None)
                parent = folders[path]
            if not is_dir:
                self._new(parts[-1], parent, False, size, name)

    def _new(self, label, parent, folder, size, full):
        iid = f"n{len(self.order)}"
        self.nodes[iid] = {"label": label, "parent": parent, "folder": folder, "size": size,
                           "full": full, "children": [], "files": 0, "sel": 0, "bytes": 0,
                           "checked": True}
        self.order.append(iid)
        (self.nodes[parent]["children"] if parent is not None else self.roots).append(iid)
        if not folder:
            self.file_ids.append(iid)
            self.total_files += 1
            self.sel_total += 1
            p = parent
            while p is not None:
                node = self.nodes[p]
                node["files"] += 1
                node["sel"] += 1
                node["bytes"] += size
                p = node["parent"]
        return iid

    def state(self, iid):
        n = self.nodes[iid]
        if not n["folder"]:
            return "all" if n["checked"] else "none"
        if n["sel"] == 0:
            return "none"
        return "all" if n["sel"] == n["files"] else "partial"

    def toggle(self, iid):
        """Flip a file, or a whole folder. Returns every node whose tick changed."""
        n = self.nodes[iid]
        target = (n["sel"] < n["files"]) if n["folder"] else (not n["checked"])
        return self._set(iid, target)

    def _set(self, iid, target):
        n = self.nodes[iid]
        before = n["sel"] if n["folder"] else int(n["checked"])
        after = (n["files"] if n["folder"] else 1) if target else 0
        changed, stack = [], [iid]
        while stack:
            i = stack.pop()
            cur = self.nodes[i]
            changed.append(i)
            if cur["folder"]:
                cur["sel"] = cur["files"] if target else 0
                stack.extend(cur["children"])
            else:
                cur["checked"] = target
        delta = after - before
        self.sel_total += delta
        p = n["parent"]
        while p is not None:
            self.nodes[p]["sel"] += delta
            changed.append(p)
            p = self.nodes[p]["parent"]
        return changed

    def set_all(self, target):
        for r in self.roots:
            self._set(r, target)
        return list(self.nodes)

    def all_selected(self):
        return self.sel_total == self.total_files

    def selected_count(self):
        return self.sel_total

    def selected_files(self):
        return {self.nodes[i]["full"] for i in self.file_ids if self.nodes[i]["checked"]}

    def summary(self):
        chosen = [self.nodes[i]["size"] for i in self.file_ids if self.nodes[i]["checked"]]
        return len(chosen), self.total_files, sum(chosen)


# --------------------------------------------------------------------------
# Window
# --------------------------------------------------------------------------
MODE_NOTES = {
    "safe": "Extracts, then deletes the archive. If anything fails, the archive is kept.",
    "shrink": "Each file is cut out of the zip as soon as it is extracted. If it stops, the zip "
              "still holds the rest: run it again to continue.",
    "low": "Frees the archive's disk space while it is read. The archive is destroyed: "
           "if extraction fails or is cancelled, it can't be recovered.",
}


class App:
    def __init__(self, root, initial=None, auto=False, here=False, low=False, shrink=False):
        import tkinter as tk
        from tkinter import ttk
        self.tk, self.ttk, self.root, self.auto = tk, ttk, root, auto
        self.job = self.scan = None
        self.busy = None                       # None | "scan" | "extract"
        self.kind = self.comp = self.model = None
        self._current = None
        self._delete_pref = True
        self._dark = None
        self.closing = False

        root.title("SpaceUnpack")
        try:                                   # window / taskbar icon (Windows)
            root.iconbitmap(resource_path("SpaceUnpack.ico"))
        except Exception:  # noqa: BLE001
            pass
        self.style = ttk.Style()
        try:                                   # modern theme that follows the system
            import sv_ttk
            self.sv = sv_ttk
        except Exception:  # noqa: BLE001
            self.sv = None
            for theme in ("vista", "clam"):
                if theme in self.style.theme_names():
                    self.style.theme_use(theme)
                    break
        self.check_theme()
        self._build()

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        if initial:
            self.set_archive(initial)
            if here and self._current:
                self.dest.set(os.path.dirname(self._current))
            if low and self.kind in ("zip", "tar", "single"):
                self.mode.set("low")
            if shrink and self.kind == "zip":
                self.mode.set("shrink")
            self.refresh_controls()
            if auto and self._current:
                root.after(300, self.start)

    # ---- theme ------------------------------------------------------------
    def check_theme(self):
        dark = system_is_dark()
        if dark != self._dark:
            self._dark = dark
            if self.sv:
                try:
                    self.sv.set_theme("dark" if dark else "light")
                except Exception:  # noqa: BLE001
                    self.sv = None
            set_dark_titlebar(self.root, dark)
        if not self.closing:
            self.root.after(2000, self.check_theme)    # follow live changes of the system theme

    # ---- layout -----------------------------------------------------------
    def _build(self):
        tk, ttk, root = self.tk, self.ttk, self.root
        try:
            scale = max(1.0, float(root.winfo_fpixels("1i")) / 96)
        except Exception:  # noqa: BLE001
            scale = 1.0
        root.geometry(f"{int(780 * scale)}x{int(740 * scale)}")
        root.minsize(int(660 * scale), int(600 * scale))
        accent = "Accent.TButton" if self.sv else "TButton"

        self.archive, self.dest, self.password = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.mode = tk.StringVar(value="safe")
        self.delete_after = tk.BooleanVar(value=True)
        self.info = tk.StringVar(value="Choose an archive to begin.")
        self.list_note = tk.StringVar()
        self.mode_note = tk.StringVar()
        self.status = tk.StringVar()

        outer = ttk.Frame(root, padding=(20, 16))
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        head = ttk.Frame(outer)
        head.grid(row=0, column=0, sticky="ew")
        head.columnconfigure(1, weight=1)
        try:
            self.logo = tk.PhotoImage(data=LOGO_B64)
            ttk.Label(head, image=self.logo).grid(row=0, column=0, rowspan=2, padx=(0, 12))
        except Exception:  # noqa: BLE001
            pass
        ttk.Label(head, text="SpaceUnpack", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=1, sticky="w")
        ttk.Label(head, textvariable=self.info).grid(row=1, column=1, sticky="w")

        paths = ttk.Frame(outer)
        paths.grid(row=1, column=0, sticky="ew", pady=(14, 6))
        paths.columnconfigure(1, weight=1)
        ttk.Label(paths, text="Archive").grid(row=0, column=0, sticky="w", pady=4)
        self.archive_entry = ttk.Entry(paths, textvariable=self.archive)
        self.archive_entry.grid(row=0, column=1, sticky="ew", padx=10)
        self.archive_entry.bind("<Return>", lambda e: self.set_archive(self.archive.get()))
        self.archive_entry.bind("<FocusOut>", lambda e: self.set_archive(self.archive.get()))
        self.btn_archive = ttk.Button(paths, text="Browse…", command=self.pick_archive)
        self.btn_archive.grid(row=0, column=2)
        ttk.Label(paths, text="Extract to").grid(row=1, column=0, sticky="w", pady=4)
        self.dest_entry = ttk.Entry(paths, textvariable=self.dest)
        self.dest_entry.grid(row=1, column=1, sticky="ew", padx=10)
        self.btn_dest = ttk.Button(paths, text="Browse…", command=self.pick_dest)
        self.btn_dest.grid(row=1, column=2)
        ttk.Label(paths, text="Password").grid(row=2, column=0, sticky="w", pady=4)
        self.pw_entry = ttk.Entry(paths, textvariable=self.password, show="•", width=28)
        self.pw_entry.grid(row=2, column=1, sticky="w", padx=10)

        bar = ttk.Frame(outer)
        bar.grid(row=2, column=0, sticky="ew", pady=(10, 4))
        bar.columnconfigure(0, weight=1)
        ttk.Label(bar, textvariable=self.list_note).grid(row=0, column=0, sticky="w")
        self.btn_scan = ttk.Button(bar, text="Scan to choose files", command=self.scan_archive)
        self.btn_scan.grid(row=0, column=1, padx=4)
        self.btn_all = ttk.Button(bar, text="Select all", command=lambda: self.select_all(True))
        self.btn_all.grid(row=0, column=2, padx=4)
        self.btn_none = ttk.Button(bar, text="Select none", command=lambda: self.select_all(False))
        self.btn_none.grid(row=0, column=3, padx=(4, 0))

        box = ttk.Frame(outer)
        box.grid(row=3, column=0, sticky="nsew")
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(box, columns=("check", "size"), selectmode="browse", height=8)
        ys = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ys.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        self.tree.heading("#0", text="Name", anchor="w")
        self.tree.heading("check", text="Extract")
        self.tree.heading("size", text="Size", anchor="e")
        self.tree.column("#0", stretch=True, minwidth=int(200 * scale), width=int(360 * scale))
        self.tree.column("check", width=int(70 * scale), anchor="center", stretch=False)
        self.tree.column("size", width=int(100 * scale), anchor="e", stretch=False)
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<space>", self.on_tree_space)

        opts = ttk.LabelFrame(outer, text="How to extract", padding=(14, 8))
        opts.grid(row=4, column=0, sticky="ew", pady=(12, 6))
        self.rb = {}
        for value, text in (
                ("safe", "Safe  ·  extract, then delete the archive (or keep it)"),
                ("shrink", "Shrink  ·  ZIP only: remove each file from the zip as it is extracted"),
                ("low", "Low-space  ·  free the archive's disk space while extracting")):
            rb = ttk.Radiobutton(opts, text=text, value=value, variable=self.mode,
                                 command=self.refresh_controls)
            rb.grid(sticky="w", pady=2)
            self.rb[value] = rb
        self.chk_delete = ttk.Checkbutton(
            opts, text="Delete the archive after a successful extraction",
            variable=self.delete_after, command=self._on_delete_toggle)
        self.chk_delete.grid(sticky="w", padx=24, pady=(2, 0))
        ttk.Label(opts, textvariable=self.mode_note, wraplength=int(640 * scale),
                  justify="left").grid(sticky="w", pady=(8, 0))

        self.bar = ttk.Progressbar(outer, maximum=100)
        self.bar.grid(row=5, column=0, sticky="ew", pady=(10, 2))
        ttk.Label(outer, textvariable=self.status).grid(row=6, column=0, sticky="w")
        buttons = ttk.Frame(outer)
        buttons.grid(row=7, column=0, sticky="e", pady=(10, 0))
        self.btn_open = ttk.Button(buttons, text="Open folder", command=self.open_folder)
        self.btn_open.grid(row=0, column=0, padx=4)
        self.btn_cancel = ttk.Button(buttons, text="Cancel", command=self.cancel)
        self.btn_cancel.grid(row=0, column=1, padx=4)
        self.btn_extract = ttk.Button(buttons, text="Extract", style=accent, command=self.start)
        self.btn_extract.grid(row=0, column=2, padx=(4, 0))
        self.refresh_controls()

    # ---- small helpers ------------------------------------------------------
    @staticmethod
    def _enable(widget, on):
        widget.state(["!disabled"] if on else ["disabled"])

    def _on_delete_toggle(self):
        self._delete_pref = self.delete_after.get()

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.model = None
        self.list_note.set("")

    # ---- choosing the archive / destination -----------------------------------
    def pick_archive(self):
        from tkinter import filedialog
        p = filedialog.askopenfilename(
            title="Select archive",
            filetypes=[("Archives", "*.zip *.tar *.gz *.tgz *.bz2 *.tbz2 *.xz *.txz *.7z *.rar"),
                       ("All files", "*.*")])
        if p:
            self.set_archive(p)

    def pick_dest(self):
        from tkinter import filedialog
        d = filedialog.askdirectory(title="Extract to", initialdir=self.dest.get() or None)
        if d:
            self.dest.set(d)

    def set_archive(self, path):
        path = path.strip().strip('"')
        if not path or self.busy:
            return
        if not os.path.isfile(path):
            self.kind = None
            self.info.set("File not found.")
            return
        path = os.path.abspath(path)
        if path == self._current:
            return
        self._current = path
        self.archive.set(path)
        self.clear_list()
        try:
            self.kind, self.comp = su.detect(path)
        except Exception as e:  # noqa: BLE001
            self.kind = None
            self.info.set(f"Can't read this file: {e}")
            return
        self.info.set(f"{KIND_NAMES[self.kind]} · {human_size(os.path.getsize(path))}")
        self.dest.set(su.default_dest(path))
        if self.kind == "zip":
            try:
                self.show_entries(su.list_zip(path))
            except Exception as e:  # noqa: BLE001
                self.list_note.set(f"Couldn't read the file list ({e}). Everything will be extracted.")
        elif self.kind == "tar":
            self.list_note.set("Everything will be extracted. To pick files, scan the archive first.")
        else:
            self.list_note.set("Everything in this archive will be extracted.")
        self.refresh_controls()

    # ---- file list ------------------------------------------------------------
    def show_entries(self, entries):
        if len(entries) > MAX_LIST:
            self.list_note.set(f"{len(entries):,} files: too many to list. Everything will be extracted.")
            return
        model = FileModel(entries)
        if model.total_files == 0:
            self.list_note.set("This archive has no files.")
            return
        self.model = model
        for iid in model.order:
            n = model.nodes[iid]
            size = n["bytes"] if n["folder"] else n["size"]
            self.tree.insert(n["parent"] or "", "end", iid=iid, text=n["label"],
                             values=(CHECK[model.state(iid)], human_size(size)))
        self.update_summary()

    def update_summary(self):
        if self.model:
            n, total, size = self.model.summary()
            self.list_note.set(f"{n} of {total} files selected · {human_size(size)}")

    def _refresh_glyphs(self, ids):
        for i in ids:
            self.tree.set(i, "check", CHECK[self.model.state(i)])
        self.update_summary()
        self.refresh_controls()

    def toggle(self, iid):
        if self.model and not self.busy:
            self._refresh_glyphs(self.model.toggle(iid))

    def select_all(self, target):
        if self.model and not self.busy:
            self._refresh_glyphs(self.model.set_all(target))

    def on_tree_click(self, event):
        if not self.model or self.busy:
            return
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        if self.tree.identify_column(event.x) != "#1":
            return
        iid = self.tree.identify_row(event.y)
        if iid:
            self.toggle(iid)

    def on_tree_space(self, event):
        iid = self.tree.focus()
        if iid:
            self.toggle(iid)
        return "break"

    def scan_archive(self):
        if self.busy or self.kind != "tar" or not self._current:
            return
        self.scan = ListJob(self._current)
        self.set_busy("scan")
        self.scan.start()
        self.poll_scan()

    def poll_scan(self):
        s = self.scan
        if s.is_alive():
            self.bar.configure(value=s.fraction * 100)
            self.status.set(f"Reading the file list… {s.fraction * 100:.0f}%")
            self.root.after(100, self.poll_scan)
            return
        self.scan = None
        kind, value = s.result or ("error", "The scan stopped unexpectedly.")
        self.set_busy(None)
        self.bar.configure(value=0)
        if kind == "ok":
            self.show_entries(value)
            self.status.set("File list loaded.")
        elif kind == "cancelled":
            self.status.set("Scan cancelled.")
        else:
            self.status.set(f"Couldn't read the file list: {value}")
        self.refresh_controls()
        if self.closing:
            self.root.destroy()

    # ---- which controls are allowed right now ---------------------------------------
    def refresh_controls(self):
        if self.busy:
            return
        m = self.model
        partial = m is not None and not m.all_selected()
        k = self.kind
        can = {"safe": True,
               "shrink": k == "zip" and not partial,
               "low": k in ("zip", "tar", "single") and not partial}
        if not can[self.mode.get()]:
            self.mode.set("safe")
        mode = self.mode.get()
        for value, rb in self.rb.items():
            self._enable(rb, can[value])
        if partial:                              # unselected files would be lost with the archive
            self.delete_after.set(False)
            self._enable(self.chk_delete, False)
            self.mode_note.set("Only some files are selected, so the archive is kept.")
        else:
            if mode == "safe":
                self.delete_after.set(self._delete_pref)
                self._enable(self.chk_delete, True)
            else:
                self.delete_after.set(True)
                self._enable(self.chk_delete, False)
            self.mode_note.set(MODE_NOTES[mode])
        for w in (self.archive_entry, self.dest_entry, self.pw_entry, self.btn_archive, self.btn_dest):
            self._enable(w, True)
        self._enable(self.btn_all, m is not None)
        self._enable(self.btn_none, m is not None)
        self._enable(self.btn_scan, k == "tar" and m is None and bool(self._current))
        self._enable(self.btn_cancel, False)
        self._enable(self.btn_extract,
                     bool(self._current and k and (m is None or m.selected_count() > 0)))
        self.btn_extract.configure(text="Extract selected" if partial else "Extract")

    def set_busy(self, what):
        self.busy = what
        if what is None:
            self.bar.stop()
            self.bar.configure(mode="determinate")
            self.refresh_controls()
            return
        for w in (self.archive_entry, self.dest_entry, self.pw_entry, self.btn_archive,
                  self.btn_dest, self.btn_all, self.btn_none, self.btn_scan, self.btn_extract,
                  self.btn_open, self.chk_delete, *self.rb.values()):
            self._enable(w, False)
        worker = self.scan if what == "scan" else self.job
        self._enable(self.btn_cancel, worker.cancellable)
        if getattr(worker, "indeterminate", False):
            self.bar.configure(mode="indeterminate")
            self.bar.start(12)
        else:
            self.bar.configure(mode="determinate", value=0)
        self.status.set("Starting…")

    # ---- extracting -----------------------------------------------------------
    def start(self):
        from tkinter import messagebox
        if self.busy:
            return
        self.set_archive(self.archive.get())
        if not self._current or self.kind is None:
            messagebox.showerror("SpaceUnpack", "Please choose an archive first.")
            return
        dest = self.dest.get().strip()
        if not dest:
            messagebox.showerror("SpaceUnpack", "Please choose where to extract to.")
            return
        only = None
        if self.model and not self.model.all_selected():
            if self.model.selected_count() == 0:
                messagebox.showerror("SpaceUnpack", "Tick at least one file to extract.")
                return
            only = self.model.selected_files()
        mode = self.mode.get()
        if mode == "low" and not messagebox.askyesno(
                "Low-space mode",
                "The archive will be destroyed while it is being read.\n"
                "If extraction fails or is cancelled, it can't be recovered.\n\nContinue?",
                icon="warning", default="no"):
            return
        self.job = Job(self._current, os.path.abspath(dest), self.password.get(), mode == "low",
                       self.delete_after.get(), mode == "shrink", only)
        self.set_busy("extract")
        self.job.start()
        self.poll()

    def poll(self):
        job = self.job
        if job.is_alive():
            if job.indeterminate:
                self.status.set("Extracting with an external tool…")
            else:
                self.bar.configure(value=job.fraction * 100)
                self.status.set(f"{job.fraction * 100:.0f}%   {job.label}")
            self.root.after(100, self.poll)
        else:
            self.finish()

    def finish(self):
        from tkinter import messagebox
        job = self.job
        kind, value = job.result or ("error", "The extraction stopped unexpectedly.")
        self.job = None
        deleted = kind == "ok" and job.delete_after
        if deleted:                                   # the archive no longer exists
            self._current = self.kind = None
            self.archive.set("")
            self.clear_list()
            self.info.set("Archive deleted. Choose another archive to continue.")
        self.set_busy(None)
        if kind == "ok":
            self.bar.configure(value=100)
            self.status.set(f"Done. {value} file(s) extracted.")
            self._enable(self.btn_open, True)
            if self.auto and not self.closing:
                self.root.after(1200, self.root.destroy)     # right-click use: close when done
            elif not self.closing:
                tail = "The archive was deleted." if deleted else "The archive was kept."
                messagebox.showinfo("SpaceUnpack", f"Extracted {value} file(s).\n{tail}")
        elif kind == "cancelled":
            self.bar.configure(value=0)
            self.status.set("Cancelled.")
            if not self.closing:
                if job.low_space:
                    messagebox.showwarning(
                        "SpaceUnpack",
                        "Cancelled. The archive was partly consumed and can't be used again. "
                        "Files extracted so far are in the output folder.")
                elif job.shrink:
                    messagebox.showinfo(
                        "SpaceUnpack",
                        "Cancelled. The zip still holds the files that weren't extracted yet. "
                        "Run it again to continue.")
        else:
            self.bar.configure(value=0)
            self.status.set("Failed.")
            note = ("\n\nThe archive was partly consumed and can't be used again." if job.low_space
                    else "\n\nThe zip still holds the files that weren't extracted yet. "
                         "Run it again to continue." if job.shrink
                    else "\n\nThe archive was NOT deleted.")
            if not self.closing:
                messagebox.showerror("SpaceUnpack", f"{value}{note}")
        if self.closing:
            self.root.destroy()

    def cancel(self):
        from tkinter import messagebox
        if self.scan and self.scan.is_alive():
            self.scan.cancel()
            self.status.set("Cancelling…")
            return
        if not (self.job and self.job.is_alive()):
            return
        if self.job.low_space and not messagebox.askyesno(
                "Cancel", "Cancelling in low-space mode leaves the archive unusable.\n"
                          "Stop anyway?", icon="warning", default="no"):
            return
        self._enable(self.btn_cancel, False)
        self.status.set("Cancelling…")
        self.job.cancel()

    def open_folder(self):
        d = self.dest.get()
        if not os.path.isdir(d):
            return
        if sys.platform.startswith("win"):
            os.startfile(d)                                   # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", d])
        else:
            subprocess.run(["xdg-open", d])

    def on_close(self):
        worker = self.scan if self.scan and self.scan.is_alive() else (
            self.job if self.job and self.job.is_alive() else None)
        if worker is None:
            self.closing = True
            self.root.destroy()
            return
        from tkinter import messagebox
        if not worker.cancellable:
            messagebox.showinfo("SpaceUnpack", "This extraction can't be stopped. "
                                               "Please wait for it to finish.")
            return
        if not messagebox.askyesno("SpaceUnpack", "Work is in progress. Stop and exit?"):
            return
        self.closing = True
        worker.cancel()                      # the window closes when the worker has stopped


def main():
    import argparse
    import tkinter as tk
    if sys.platform.startswith("win"):
        try:                                   # crisp text on high-DPI screens
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # noqa: BLE001
            pass
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("archive", nargs="?")
    ap.add_argument("--auto", action="store_true")       # start extracting immediately
    ap.add_argument("--here", action="store_true")       # extract into the archive's own folder
    ap.add_argument("--low-space", action="store_true")
    ap.add_argument("--shrink", action="store_true")     # ZIP: remove files from the zip as extracted
    args, _ = ap.parse_known_args()
    root = tk.Tk()
    App(root, args.archive, args.auto, args.here, args.low_space, args.shrink)
    root.mainloop()


if __name__ == "__main__":
    main()
