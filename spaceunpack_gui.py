#!/usr/bin/env python3
"""
SpaceUnpack - desktop app.  Extract an archive and delete it without needing
double the disk space.  Needs spaceunpack.py in the same folder.

Run:        python spaceunpack_gui.py [archive]
Windows exe: see build_windows.bat
"""
import os
import subprocess
import sys
import threading

import spaceunpack as su


# --------------------------------------------------------------------------
# Background job (no GUI code in here)
# --------------------------------------------------------------------------
class Cancelled(Exception):
    pass


class Job(threading.Thread):
    """Runs one extraction in a thread. Doubles as the `progress` object."""

    def __init__(self, path, dest, password, low_space, delete_after, shrink=False):
        super().__init__(daemon=True)
        self.path, self.dest = path, dest
        self.password, self.low_space, self.delete_after = password, low_space, delete_after
        self.shrink = shrink
        self.indeterminate = su.detect(path)[0] == "external"
        self.fraction = 0.0
        self.label = ""
        self.result = None            # ("ok", n_files) | ("cancelled", None) | ("error", message)
        self._cancel = threading.Event()

    # progress interface used by the extractors
    def update(self, frac, label=""):
        if self._cancel.is_set():
            raise Cancelled()
        self.fraction, self.label = frac, label

    def done(self):
        pass

    def cancel(self):
        if not self.indeterminate:     # an external 7z/unrar run can't be interrupted safely
            self._cancel.set()

    def run(self):
        try:
            if self.low_space:
                ok, why = su.check_low_space(self.path, su.detect(self.path)[0])
                if not ok:
                    raise RuntimeError(f"Low-space mode isn't possible here: {why}")
            n = su.extract_archive(self.path, self.dest, self.password or None,
                                   self.low_space, self, shrink=self.shrink)
            if self.delete_after:
                os.remove(self.path)
            self.result = ("ok", n)
        except Cancelled:
            self.result = ("cancelled", None)
        except Exception as e:  # noqa: BLE001
            self.result = ("error", str(e))


def human_size(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


KIND_NAMES = {"zip": "ZIP archive", "tar": "TAR archive", "single": "compressed file",
              "external": "other format (needs 7-Zip or unrar installed)"}


# --------------------------------------------------------------------------
# Window
# --------------------------------------------------------------------------
class App:
    def __init__(self, root, initial=None, auto=False, here=False, low=False, shrink=False):
        import tkinter as tk
        from tkinter import ttk
        self.tk, self.ttk = tk, ttk
        self.root = root
        self.job = None
        self.kind = None
        self.closing = False
        self.auto = auto

        root.title("SpaceUnpack")
        try:                                   # window / taskbar icon (Windows)
            base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
            root.iconbitmap(os.path.join(base, "SpaceUnpack.ico"))
        except Exception:  # noqa: BLE001
            pass
        root.minsize(560, 0)
        root.resizable(True, False)
        style = ttk.Style()
        for theme in ("vista", "clam"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break

        self.archive = tk.StringVar()
        self.dest = tk.StringVar()
        self.password = tk.StringVar()
        self.delete_after = tk.BooleanVar(value=True)
        self.low_space = tk.BooleanVar(value=False)
        self.shrink = tk.BooleanVar(value=False)
        self.info = tk.StringVar(value="Choose an archive to begin.")
        self.status = tk.StringVar(value="")

        frm = ttk.Frame(root, padding=14)
        frm.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="Archive:").grid(row=0, column=0, sticky="w", pady=4)
        self.archive_entry = ttk.Entry(frm, textvariable=self.archive)
        self.archive_entry.grid(row=0, column=1, sticky="ew", padx=6)
        self.archive_entry.bind("<Return>", lambda e: self.set_archive(self.archive.get()))
        self.archive_entry.bind("<FocusOut>", lambda e: self.set_archive(self.archive.get()))
        self.btn_archive = ttk.Button(frm, text="Browse…", command=self.pick_archive)
        self.btn_archive.grid(row=0, column=2)

        ttk.Label(frm, textvariable=self.info, foreground="#555").grid(
            row=1, column=1, columnspan=2, sticky="w", padx=6)

        ttk.Label(frm, text="Extract to:").grid(row=2, column=0, sticky="w", pady=4)
        self.dest_entry = ttk.Entry(frm, textvariable=self.dest)
        self.dest_entry.grid(row=2, column=1, sticky="ew", padx=6)
        self.btn_dest = ttk.Button(frm, text="Browse…", command=self.pick_dest)
        self.btn_dest.grid(row=2, column=2)

        ttk.Label(frm, text="Password:").grid(row=3, column=0, sticky="w", pady=4)
        self.pw_entry = ttk.Entry(frm, textvariable=self.password, show="•", width=24)
        self.pw_entry.grid(row=3, column=1, sticky="w", padx=6)

        opts = ttk.LabelFrame(frm, text="Options", padding=10)
        opts.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10, 6))
        self.chk_delete = ttk.Checkbutton(
            opts, text="Delete the archive after a successful extraction",
            variable=self.delete_after)
        self.chk_delete.grid(sticky="w")
        self.chk_shrink = ttk.Checkbutton(
            opts, text="Shrink mode (ZIP only): remove each file from the zip once extracted",
            variable=self.shrink, command=lambda: self.on_mode_toggled("shrink"))
        self.chk_shrink.grid(sticky="w", pady=(6, 0))
        ttk.Label(opts, foreground="#555", wraplength=500, justify="left",
                  text="Saves space on any drive. If it stops, the zip still holds the files "
                       "that weren't extracted yet: run it again to continue.").grid(sticky="w", padx=22)
        self.chk_low = ttk.Checkbutton(
            opts, text="Low-space mode: free disk space while extracting",
            variable=self.low_space, command=lambda: self.on_mode_toggled("low"))
        self.chk_low.grid(sticky="w", pady=(6, 0))
        ttk.Label(
            opts, foreground="#a33", wraplength=500, justify="left",
            text="Lets you extract an archive that is larger than half your free space. "
                 "The archive is destroyed as it is read: if extraction fails or is "
                 "cancelled, it cannot be recovered.").grid(sticky="w", padx=22)

        self.bar = ttk.Progressbar(frm, maximum=100)
        self.bar.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(8, 2))
        ttk.Label(frm, textvariable=self.status).grid(row=6, column=0, columnspan=3, sticky="w")

        buttons = ttk.Frame(frm)
        buttons.grid(row=7, column=0, columnspan=3, sticky="e", pady=(10, 0))
        self.btn_extract = ttk.Button(buttons, text="Extract", command=self.start)
        self.btn_extract.grid(row=0, column=0, padx=4)
        self.btn_cancel = ttk.Button(buttons, text="Cancel", command=self.cancel, state="disabled")
        self.btn_cancel.grid(row=0, column=1, padx=4)
        self.btn_open = ttk.Button(buttons, text="Open folder", command=self.open_folder,
                                   state="disabled")
        self.btn_open.grid(row=0, column=2, padx=4)

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        if initial:
            self.set_archive(initial)
            if here and getattr(self, "_current", None):
                self.dest.set(os.path.dirname(self._current))
            if low and self.kind not in (None, "external"):
                self.low_space.set(True)
                self.on_low_space_toggled()
            if shrink and self.kind == "zip":
                self.shrink.set(True)
                self.on_mode_toggled("shrink")
            if auto and getattr(self, "_current", None):
                root.after(300, self.start)

    # ---- archive / destination ------------------------------------------
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
        if not path:
            return
        if not os.path.isfile(path):
            self.kind = None
            self.info.set("File not found.")
            return
        path = os.path.abspath(path)
        if path == getattr(self, "_current", None):
            return
        self._current = path
        self.archive.set(path)
        try:
            self.kind, comp = su.detect(path)
        except Exception as e:  # noqa: BLE001
            self.kind = None
            self.info.set(f"Can't read this file: {e}")
            return
        self.info.set(f"{KIND_NAMES[self.kind]} · {human_size(os.path.getsize(path))}")
        self.dest.set(su.default_dest(path))
        if self.kind == "external":
            self.low_space.set(False)
            self.chk_low.state(["disabled"])
        else:
            self.chk_low.state(["!disabled"])
        if self.kind == "zip":
            self.chk_shrink.state(["!disabled"])
        else:
            self.shrink.set(False)
            self.chk_shrink.state(["disabled"])
        self.on_mode_toggled()

    def on_mode_toggled(self, which=None):
        if which == "shrink" and self.shrink.get():
            self.low_space.set(False)
        elif which == "low" and self.low_space.get():
            self.shrink.set(False)
        if self.low_space.get() or self.shrink.get():
            self.delete_after.set(True)          # the (emptied) archive is deleted either way
            self.chk_delete.state(["disabled"])
        else:
            self.chk_delete.state(["!disabled"])

    on_low_space_toggled = on_mode_toggled

    # ---- running ----------------------------------------------------------
    def start(self):
        from tkinter import messagebox
        self.set_archive(self.archive.get())
        path = getattr(self, "_current", None)
        if not path or self.kind is None:
            messagebox.showerror("SpaceUnpack", "Please choose an archive first.")
            return
        dest = self.dest.get().strip()
        if not dest:
            messagebox.showerror("SpaceUnpack", "Please choose where to extract to.")
            return
        if self.low_space.get() and not messagebox.askyesno(
                "Low-space mode",
                "The archive will be destroyed while it is being read.\n"
                "If extraction fails or is cancelled, it can't be recovered.\n\nContinue?",
                icon="warning", default="no"):
            return

        self.job = Job(path, os.path.abspath(dest), self.password.get(),
                       self.low_space.get(), self.delete_after.get(), self.shrink.get())
        self.set_running(True)
        self.job.start()
        self.poll()

    def set_running(self, running):
        state = "disabled" if running else "normal"
        for w in (self.archive_entry, self.dest_entry, self.pw_entry,
                  self.btn_archive, self.btn_dest):
            w.configure(state=state)
        self.btn_extract.configure(state=state)
        self.btn_cancel.configure(
            state="normal" if running and not self.job.indeterminate else "disabled")
        self.btn_open.configure(state="disabled")
        if running:
            self.chk_low.state(["disabled"])
            self.chk_shrink.state(["disabled"])
            self.chk_delete.state(["disabled"])
            if self.job.indeterminate:
                self.bar.configure(mode="indeterminate")
                self.bar.start(12)
            else:
                self.bar.configure(mode="determinate", value=0)
            self.status.set("Starting…")
        else:
            self.bar.stop()
            self.bar.configure(mode="determinate")
            if self.kind != "external":
                self.chk_low.state(["!disabled"])
            if self.kind == "zip":
                self.chk_shrink.state(["!disabled"])
            self.on_low_space_toggled()

    def poll(self):
        job = self.job
        if job.is_alive():
            if not job.indeterminate:
                self.bar.configure(value=job.fraction * 100)
                self.status.set(f"{job.fraction * 100:.0f}%   {job.label}")
            else:
                self.status.set("Extracting with external tool…")
            self.root.after(100, self.poll)
        else:
            self.finish()

    def finish(self):
        from tkinter import messagebox
        job = self.job
        kind, value = job.result or ("error", "The extraction stopped unexpectedly.")
        self.set_running(False)
        if kind == "ok":
            self.bar.configure(value=100)
            self.status.set(f"Done. {value} file(s) extracted.")
            self.btn_open.configure(state="normal")
            if job.delete_after:
                self._current = None           # the archive no longer exists
                self.archive.set("")
                self.info.set("Archive deleted. Choose another archive to continue.")
            if self.auto and not self.closing:
                self.root.after(1200, self.root.destroy)     # right-click use: close when done
            elif not self.closing:
                messagebox.showinfo(
                    "SpaceUnpack",
                    f"Extracted {value} file(s).\n" + ("The archive was deleted." if job.delete_after
                                                      else "The archive was kept."))
        elif kind == "cancelled":
            self.bar.configure(value=0)
            self.status.set("Cancelled.")
            if job.low_space and not self.closing:
                messagebox.showwarning(
                    "SpaceUnpack",
                    "Cancelled. The archive was partly consumed and can't be used again. "
                    "Files extracted so far are in the output folder.")
            elif job.shrink and not self.closing:
                messagebox.showinfo(
                    "SpaceUnpack",
                    "Cancelled. The zip still holds the files that weren't extracted yet. "
                    "Run it again to continue.")
        else:
            self.bar.configure(value=0)
            self.status.set("Failed.")
            note = ("\n\nThe archive was partly consumed and can't be used again." if job.low_space
                    else "\n\nThe zip still holds the files that weren't extracted yet. Run it again to continue."
                    if job.shrink else "\n\nThe archive was NOT deleted.")
            if not self.closing:
                messagebox.showerror("SpaceUnpack", f"{value}{note}")
        if self.closing:
            self.root.destroy()

    def cancel(self):
        from tkinter import messagebox
        if not (self.job and self.job.is_alive()):
            return
        if self.job.low_space and not messagebox.askyesno(
                "Cancel", "Cancelling in low-space mode leaves the archive unusable.\n"
                          "Stop anyway?", icon="warning", default="no"):
            return
        self.btn_cancel.configure(state="disabled")
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
        if self.job and self.job.is_alive():
            from tkinter import messagebox
            if not messagebox.askyesno("SpaceUnpack", "Extraction is running. Stop and exit?"):
                return
            self.closing = True
            self.job.cancel()
            if self.job.indeterminate:
                self.closing = False          # can't be interrupted; just wait for it
                messagebox.showinfo("SpaceUnpack", "This extraction can't be stopped. "
                                                   "Please wait for it to finish.")
            return
        self.root.destroy()


def main():
    import tkinter as tk
    if sys.platform.startswith("win"):
        try:                                   # crisp text on high-DPI screens
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # noqa: BLE001
            pass
    import argparse
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
