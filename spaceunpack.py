#!/usr/bin/env python3
"""
spaceunpack - extract an archive and delete it, without needing double the disk space.

Modes
-----
default      Extract everything, verify it, then delete the archive.
             (Peak usage = archive + extracted data. Safe: archive is only
             deleted after a fully successful extraction.)

--low-space  Extract and hand the archive's disk space back to the filesystem
             *while extracting* (hole punching / sparse files), then delete the
             archive. Peak usage is roughly the size of the extracted data
             plus a few MiB.
             WARNING: the archive is destroyed as it is read. If extraction
             fails halfway (bad CRC, power cut, Ctrl+C) the archive CANNOT be
             recovered.

Supported: .zip, .tar, .tar.gz/.tgz, .tar.bz2, .tar.xz, and single-file
.gz/.bz2/.xz. Other formats (7z, rar, ...) are extracted through an installed
7-Zip/unrar command in default mode only.

--low-space needs a filesystem with sparse-file support:
Linux (ext4, xfs, btrfs, tmpfs...) and Windows (NTFS, ReFS). Not FAT/exFAT/macOS.

Usage
-----
    python spaceunpack.py archive.zip
    python spaceunpack.py archive.tar.gz -o /some/folder --low-space
    python spaceunpack.py archive.zip -p secret --low-space --yes
"""
import argparse
import bz2
import ctypes
import gzip
import io
import lzma
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile

IS_WIN = os.name == "nt"
IS_LINUX = sys.platform.startswith("linux")
CHUNK = 1 << 20          # 1 MiB read/write size
FREE_EVERY = 4 << 20     # give space back in batches of at least 4 MiB


# --------------------------------------------------------------------------
# Hole punching (give disk blocks of an already-read region back to the OS)
# --------------------------------------------------------------------------
_FALLOC_FL_KEEP_SIZE = 0x01
_FALLOC_FL_PUNCH_HOLE = 0x02
FSCTL_SET_SPARSE = 0x000900C4
FSCTL_SET_ZERO_DATA = 0x000980C8


def _win_ioctl(fd, code, payload=None):
    import msvcrt
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.DeviceIoControl.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
        wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID]
    k32.DeviceIoControl.restype = wintypes.BOOL
    returned = wintypes.DWORD(0)
    ptr = ctypes.byref(payload) if payload is not None else None
    size = ctypes.sizeof(payload) if payload is not None else 0
    if not k32.DeviceIoControl(msvcrt.get_osfhandle(fd), code, ptr, size,
                               None, 0, ctypes.byref(returned), None):
        raise ctypes.WinError(ctypes.get_last_error())


class _ZeroData(ctypes.Structure):
    _fields_ = [("FileOffset", ctypes.c_longlong), ("BeyondFinalZero", ctypes.c_longlong)]


class HolePuncher:
    """Opens a file for writing and can deallocate byte ranges of it."""

    def __init__(self, path):
        if not (IS_WIN or IS_LINUX):
            raise OSError("--low-space is only supported on Linux and Windows")
        self._f = open(path, "r+b", buffering=0)
        self._fd = self._f.fileno()
        if IS_WIN:
            _win_ioctl(self._fd, FSCTL_SET_SPARSE)
        else:
            libc = ctypes.CDLL(None, use_errno=True)
            libc.fallocate.argtypes = [ctypes.c_int, ctypes.c_int,
                                       ctypes.c_longlong, ctypes.c_longlong]
            libc.fallocate.restype = ctypes.c_int
            self._libc = libc

    def punch(self, offset, length):
        if length <= 0:
            return
        if IS_WIN:
            _win_ioctl(self._fd, FSCTL_SET_ZERO_DATA, _ZeroData(offset, offset + length))
        else:
            r = self._libc.fallocate(self._fd, _FALLOC_FL_PUNCH_HOLE | _FALLOC_FL_KEEP_SIZE,
                                     offset, length)
            if r != 0:
                e = ctypes.get_errno()
                raise OSError(e, os.strerror(e))

    def close(self):
        self._f.close()


def allocated_bytes(path):
    """Bytes of disk actually used by a (possibly sparse) file."""
    if IS_WIN:
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.GetCompressedFileSizeW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
        k32.GetCompressedFileSizeW.restype = wintypes.DWORD
        high = wintypes.DWORD(0)
        low = k32.GetCompressedFileSizeW(path, ctypes.byref(high))
        return (high.value << 32) | low
    return os.stat(path).st_blocks * 512


def punch_supported(directory):
    """Check on a scratch file in the same folder that hole punching really frees space."""
    fd, tmp = tempfile.mkstemp(prefix=".spaceunpack-test-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(os.urandom(1 << 20))
            f.flush()
            os.fsync(f.fileno())
        before = allocated_bytes(tmp)
        hp = HolePuncher(tmp)
        try:
            hp.punch(0, 1 << 20)
        finally:
            hp.close()
        after = allocated_bytes(tmp)
        if after < before:
            return True, ""
        return False, "the filesystem accepted the call but did not free any space"
    except Exception as e:  # noqa: BLE001
        return False, str(e)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
class Progress:
    def __init__(self):
        self._last = 0.0

    def update(self, frac, label=""):
        now = time.time()
        if now - self._last < 0.2 and frac < 1:
            return
        self._last = now
        label = label[-45:]
        sys.stderr.write(f"\r  {min(frac, 1) * 100:5.1f}%  {label:<45}")
        sys.stderr.flush()

    def done(self):
        sys.stderr.write("\r" + " " * 60 + "\r")
        sys.stderr.flush()


class UnsafePath(Exception):
    pass


def safe_target(dest, name):
    """Join an archive member name onto dest, refusing anything that escapes it."""
    parts = [p for p in name.replace("\\", "/").split("/") if p not in ("", ".")]
    root = os.path.abspath(dest)
    try:
        target = os.path.abspath(os.path.join(root, *parts))
        inside = os.path.commonpath([root, target]) == root
    except ValueError:
        inside = False
    if not inside:
        raise UnsafePath(f"refusing unsafe path in archive: {name!r}")
    return target


class FreeingReader(io.RawIOBase):
    """Sequential file reader that returns consumed bytes to the filesystem."""

    def __init__(self, path, puncher, progress):
        self._f = open(path, "rb", buffering=0)
        self._puncher = puncher
        self._progress = progress
        self._size = os.path.getsize(path) or 1
        self._pos = 0
        self._freed = 0

    def readable(self):
        return True

    def readinto(self, b):
        n = self._f.readinto(b)
        if n:
            self._pos += n
            if self._puncher and self._pos - self._freed >= FREE_EVERY:
                self._puncher.punch(self._freed, self._pos - self._freed)
                self._freed = self._pos
            self._progress.update(self._pos / self._size, "reading archive")
        return n

    def close(self):
        if not self.closed:
            self._f.close()
        super().close()


# --------------------------------------------------------------------------
# Format detection
# --------------------------------------------------------------------------
def detect(path):
    with open(path, "rb") as f:
        head = f.read(8)
    if zipfile.is_zipfile(path):
        return "zip", None
    comp = None
    if head[:2] == b"\x1f\x8b":
        comp = "gz"
    elif head[:3] == b"BZh":
        comp = "bz2"
    elif head[:6] == b"\xfd7zXZ\x00":
        comp = "xz"
    if tarfile.is_tarfile(path):
        return "tar", comp
    if comp:
        return "single", comp
    return "external", None


# --------------------------------------------------------------------------
# Extractors
# --------------------------------------------------------------------------
def extract_zip(path, dest, password, puncher, progress):
    freed = 0

    def release(upto, force=False):
        nonlocal freed
        if puncher and upto - freed >= (1 if force else FREE_EVERY):
            puncher.punch(freed, upto - freed)
            freed = upto

    count = 0
    with zipfile.ZipFile(path) as zf:
        if password:
            zf.setpassword(password.encode())
        # Process in on-disk order so everything before the current entry is dead weight.
        infos = sorted(zf.infolist(), key=lambda i: i.header_offset)
        total = sum(i.file_size for i in infos) or 1
        done = 0
        end_of_data = getattr(zf, "start_dir", None)  # where the central directory begins
        for idx, info in enumerate(infos):
            target = safe_target(dest, info.filename)
            if info.is_dir():
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            try:
                with zf.open(info) as src, open(target, "wb") as out:
                    while True:
                        chunk = src.read(CHUNK)
                        if not chunk:
                            break
                        out.write(chunk)
                        done += len(chunk)
                        release(zf.fp.tell())      # compressed bytes read so far
                        progress.update(done / total, info.filename)
            except BaseException:
                try:
                    os.remove(target)              # don't leave a truncated file behind
                except OSError:
                    pass
                raise
            try:
                ts = time.mktime(tuple(info.date_time) + (0, 0, -1))
                os.utime(target, (ts, ts))
            except (OverflowError, ValueError, OSError):
                pass
            count += 1
            nxt = infos[idx + 1].header_offset if idx + 1 < len(infos) else end_of_data
            if nxt is not None:
                release(nxt, force=True)
    return count


def extract_zip_shrink(path, dest, password, progress):
    """ZIP only. Extract the LAST file first, then cut it off the end of the zip.

    After every batch the zip is rewritten as a normal, valid (smaller) zip that holds only
    the files not extracted yet. Works on any filesystem. If it stops, run it again.
    """
    if not hasattr(zipfile.ZipFile, "_write_end_record"):
        raise RuntimeError("Shrink mode isn't supported by this Python version")
    count = done = 0
    removed = []                       # extracted files that are still physically in the zip
    with zipfile.ZipFile(path, "a") as zf:
        if password:
            zf.setpassword(password.encode())
        infos = sorted(zf.infolist(), key=lambda i: i.header_offset, reverse=True)
        total = sum(i.file_size for i in infos) or 1

        def commit():
            if not removed:
                return
            gone = {id(i) for i in removed}
            zf.filelist[:] = [i for i in zf.filelist if id(i) not in gone]
            for i in removed:
                if zf.NameToInfo.get(i.filename) is i:
                    del zf.NameToInfo[i.filename]
            zf.start_dir = min(i.header_offset for i in removed)
            zf._didModify = True
            zf.fp.seek(zf.start_dir)
            zf._write_end_record()     # writes the shorter directory and truncates the file
            zf.fp.flush()
            removed.clear()

        try:
            for info in infos:
                target = safe_target(dest, info.filename)
                if info.is_dir():
                    os.makedirs(target, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    try:
                        with zf.open(info) as src, open(target, "wb") as out:
                            while True:
                                chunk = src.read(CHUNK)
                                if not chunk:
                                    break
                                out.write(chunk)
                                done += len(chunk)
                                progress.update(done / total, info.filename)
                    except BaseException:
                        try:
                            os.remove(target)
                        except OSError:
                            pass
                        raise
                    try:
                        ts = time.mktime(tuple(info.date_time) + (0, 0, -1))
                        os.utime(target, (ts, ts))
                    except (OverflowError, ValueError, OSError):
                        pass
                    count += 1
                removed.append(info)
                if zf.start_dir - info.header_offset >= max(FREE_EVERY, 128 * len(zf.filelist)):
                    commit()
        finally:
            try:
                commit()               # always record what was extracted, even after an error
            except Exception:  # noqa: BLE001
                pass
    return count


def _open_decoder(comp, reader):
    if comp == "gz":
        return gzip.GzipFile(fileobj=reader, mode="rb")
    if comp == "bz2":
        return bz2.BZ2File(reader, "rb")
    if comp == "xz":
        return lzma.LZMAFile(reader, "rb")
    return reader


def extract_tar(path, dest, comp, puncher, progress):
    count = 0
    raw = FreeingReader(path, puncher, progress)
    reader = io.BufferedReader(raw, CHUNK)
    decoder = _open_decoder(comp, reader)
    try:
        kw = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
        with tarfile.open(fileobj=decoder, mode="r|") as tar:
            for m in tar:
                if not kw:
                    safe_target(dest, m.name)
                    if not (m.isreg() or m.isdir()):
                        continue
                tar.extract(m, dest, **kw)
                if m.isreg():
                    count += 1
        # Read to the true end of the stream so the gzip/bz2/xz integrity check runs.
        while decoder.read(CHUNK):
            pass
    finally:
        if decoder is not reader:
            decoder.close()
        reader.close()
    return count


def extract_single(path, dest, comp, puncher, progress):
    name = os.path.basename(path)
    for suf in (".gz", ".bz2", ".xz"):
        if name.lower().endswith(suf):
            name = name[: -len(suf)]
            break
    else:
        name += ".out"
    target = safe_target(dest, name)
    raw = FreeingReader(path, puncher, progress)
    reader = io.BufferedReader(raw, CHUNK)
    decoder = _open_decoder(comp, reader)
    try:
        with open(target, "wb") as out:
            while True:
                chunk = decoder.read(CHUNK)
                if not chunk:
                    break
                out.write(chunk)
    except BaseException:
        try:
            os.remove(target)
        except OSError:
            pass
        raise
    finally:
        decoder.close()
        reader.close()
    return 1


def extract_external(path, dest, password):
    for exe in ("7z", "7zz", "7za", "7zr"):
        found = shutil.which(exe)
        if found:
            cmd = [found, "x", "-y", f"-o{dest}", path]
            if password:
                cmd.insert(2, f"-p{password}")
            break
    else:
        found = shutil.which("unrar")
        if not found:
            raise RuntimeError("this format needs 7-Zip (7z) or unrar installed")
        cmd = [found, "x", "-y"] + ([f"-p{password}"] if password else []) + [path, dest + os.sep]
    flags = 0x08000000 if IS_WIN else 0   # CREATE_NO_WINDOW
    quiet = {} if sys.stdout else {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if subprocess.run(cmd, creationflags=flags, stdin=subprocess.DEVNULL, **quiet).returncode != 0:
        raise RuntimeError("external extractor reported an error")
    return 0


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
_SUFFIXES = (".tar.gz", ".tar.bz2", ".tar.xz", ".tgz", ".tbz2", ".txz", ".tar",
             ".zip", ".gz", ".bz2", ".xz", ".7z", ".rar")


def default_dest(path):
    name = os.path.basename(path)
    for suf in _SUFFIXES:
        if name.lower().endswith(suf) and len(name) > len(suf):
            return os.path.join(os.path.dirname(path), name[: -len(suf)])
    return os.path.join(os.path.dirname(path), name + "_extracted")


def check_low_space(path, kind):
    """Return (ok, reason) for whether --low-space can be used on this archive."""
    if kind == "external":
        return False, "this format needs 7z/unrar and can only be extracted in normal mode"
    return punch_supported(os.path.dirname(path))


def extract_archive(path, dest, password=None, low_space=False, progress=None, shrink=False):
    """Extract `path` into `dest`. Returns the number of files. Never deletes the archive.

    `progress` needs .update(fraction, label) and .done(); it may raise to abort.
    """
    progress = progress or Progress()
    kind, comp = detect(path)
    puncher = None
    try:
        os.makedirs(dest, exist_ok=True)
        if shrink:
            if kind != "zip":
                raise RuntimeError("Shrink mode only works with ZIP archives")
            return extract_zip_shrink(path, dest, password, progress)
        if low_space:
            puncher = HolePuncher(path)
        if kind == "zip":
            return extract_zip(path, dest, password, puncher, progress)
        if kind == "tar":
            return extract_tar(path, dest, comp, puncher, progress)
        if kind == "single":
            return extract_single(path, dest, comp, puncher, progress)
        return extract_external(path, dest, password)
    finally:
        if puncher:
            puncher.close()
        progress.done()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Extract an archive, then delete it.")
    ap.add_argument("archive")
    ap.add_argument("-o", "--output", help="destination folder (default: next to the archive)")
    ap.add_argument("-p", "--password", help="password for encrypted archives")
    ap.add_argument("--low-space", action="store_true",
                    help="free the archive's disk space while extracting (DESTRUCTIVE, see top of file)")
    ap.add_argument("--shrink", action="store_true",
                    help="ZIP only: remove each file from the zip as it is extracted (safe, works everywhere)")
    ap.add_argument("--keep", action="store_true", help="do not delete the archive afterwards")
    ap.add_argument("-y", "--yes", action="store_true", help="skip the --low-space confirmation")
    args = ap.parse_args(argv)

    path = os.path.abspath(args.archive)
    if not os.path.isfile(path):
        print(f"error: {path} is not a file", file=sys.stderr)
        return 2
    if args.low_space and args.keep:
        print("error: --low-space destroys the archive, it cannot be combined with --keep",
              file=sys.stderr)
        return 2
    dest = os.path.abspath(args.output) if args.output else default_dest(path)
    if args.shrink and (args.keep or args.low_space):
        print("error: --shrink can't be combined with --keep or --low-space", file=sys.stderr)
        return 2
    if args.shrink and detect(path)[0] != "zip":
        print("error: --shrink only works with ZIP archives", file=sys.stderr)
        return 2

    if args.low_space:
        ok, why = check_low_space(path, detect(path)[0])
        if not ok:
            print(f"error: --low-space is not possible here ({why}).\n"
                  "Run without --low-space instead.", file=sys.stderr)
            return 2
        if not args.yes:
            print("--low-space destroys the archive while it is being read.\n"
                  "If extraction fails or is interrupted, the archive cannot be recovered.")
            if input("Continue? [y/N] ").strip().lower() != "y":
                print("Cancelled.")
                return 1

    try:
        n = extract_archive(path, dest, args.password, args.low_space, shrink=args.shrink)
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        _failure_note(path, args.low_space, args.shrink)
        return 130
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        _failure_note(path, args.low_space, args.shrink)
        return 1

    print(f"Extracted {n} file(s) to {dest}")
    if not args.keep:
        os.remove(path)
        print(f"Deleted {path}")
    return 0


def _failure_note(path, low_space, shrink=False):
    if shrink:
        print("The zip still holds the files that were not extracted yet. Run the same command "
              "again to continue.", file=sys.stderr)
    elif low_space:
        print("The archive was partly consumed and can no longer be used to restart. "
              "Files extracted so far remain in the output folder.", file=sys.stderr)
    else:
        print("The archive was NOT deleted.", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
