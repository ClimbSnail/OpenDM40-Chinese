#!/usr/bin/env python3
"""Upload a DM40 update file over USBTMC and install it, on Windows.

dm40dbg.py (upstream) finds the meter through /sys/bus/usb/devices, so it is
Linux only. This is the same protocol over PyVISA:

    DBG:UPLOAD:BEGIN <len>,<crc32>
    DBG:UPLOAD:DATA <offset>,<232 raw bytes>      (repeated)
    DBG:UPLOAD:END?                ->  "<len>,<crc32>"  (the meter re-reads
                                      the file and checks it itself)
    DBG:UPDATE                     ->  loader marker zeroed, reset; the
                                      vendor loader installs the one
                                      dm40*.bin in the SPI disk's root

    python upload_zh.py IMAGE [--update] [--wait 90]
"""

import sys
import time
import zlib

import pyvisa

CHUNK = 232  # 256-byte USBTMC command buffer - "DBG:UPLOAD:DATA <offset>,"


def open_meter(timeout=5000):
    rm = pyvisa.ResourceManager("@py")
    names = [r for r in rm.list_resources() if "::4617::53312::" in r or "0x1209::0xD040" in r.upper()]
    if not names:
        return None, None, rm
    d = rm.open_resource(names[0], read_termination="\n", write_termination="\n", timeout=timeout)
    return d, names[0], rm


def drain(d):
    """Clear SCPI errors an earlier client may have left queued."""
    seen = []
    for _ in range(8):
        try:
            e = d.query("SYST:ERR?").strip()
        except Exception as ex:
            return seen + ["<no answer: %s>" % ex]
        if e.startswith("0,"):
            break
        seen.append(e)
    return seen


def present(rm):
    return any("::4617::53312::" in r or "0x1209::0xD040" in r.upper() for r in rm.list_resources())


def main():
    argv = sys.argv[1:]
    if not argv:
        sys.exit(__doc__)
    path = argv[0]
    do_update = "--update" in argv
    wait = int(argv[argv.index("--wait") + 1]) if "--wait" in argv else 90

    data = open(path, "rb").read()
    crc = zlib.crc32(data) & 0xFFFFFFFF
    print("image   : %s" % path)
    print("size    : %d bytes, CRC-32 %08x" % (len(data), crc))

    d, name, rm = open_meter()
    if not d:
        sys.exit("meter not found (USBTMC). Is the cable in and opendm40 running?")
    print("resource: %s" % name)
    print("IDN     : %s" % d.query("*IDN?").strip())

    stale = drain(d)
    if stale:
        print("note    : cleared %d stale SCPI error(s): %s" % (len(stale), "; ".join(stale)))

    # --- upload ---------------------------------------------------------
    t0 = time.time()
    d.write("DBG:UPLOAD:BEGIN %d,%d" % (len(data), crc))
    e = d.query("SYST:ERR?").strip()
    if not e.startswith("0,"):
        sys.exit("DBG:UPLOAD:BEGIN failed: SCPI error %s" % e)

    sent = 0
    for i, off in enumerate(range(0, len(data), CHUNK)):
        d.write_raw(b"DBG:UPLOAD:DATA %d," % off + data[off:off + CHUNK])
        sent = min(off + CHUNK, len(data))
        if i % 256 == 255:
            e = d.query("SYST:ERR?").strip()
            if not e.startswith("0,"):
                sys.exit("DBG:UPLOAD:DATA failed at offset %d: %s" % (off, e))
            sys.stderr.write("\r  %d / %d bytes" % (sent, len(data)))
            sys.stderr.flush()

    got = d.query("DBG:UPLOAD:END?").strip()
    want = "%d,%d" % (len(data), crc)
    sys.stderr.write("\r  %d / %d bytes\n" % (len(data), len(data)))
    if got != want:
        sys.exit("DBG:UPLOAD:END? mismatch: got %r want %r (the meter re-read the "
                 "file and its CRC did not match)" % (got, want))
    print("upload  : OK, %d bytes, CRC-32 %08x, %.1f s (stored as DM40FW.BIN)"
          % (len(data), crc, time.time() - t0))

    if not do_update:
        print("\ndone (upload only). Add --update to install it.")
        return

    # --- update ---------------------------------------------------------
    drain(d)
    print("update  : sending DBG:UPDATE (loader marker zeroed, reset)")
    try:
        d.write("DBG:UPDATE")
    except Exception as ex:
        print("  write returned %s (the reset may already have happened)" % type(ex).__name__)

    gone_at = None
    t1 = time.time() + 20
    while time.time() < t1:
        if not present(rm):
            gone_at = time.time()
            break
        time.sleep(0.1)
    print("  device dropped off USB: %s" % ("yes, %.1f s" % (gone_at - t1 + 20) if gone_at else "NO"))

    # --- wait for opendm40 to come back --------------------------------
    deadline = time.time() + wait
    back = False
    while time.time() < deadline:
        if present(rm):
            try:
                d2, _, _ = open_meter()
                if d2:
                    idn = d2.query("*IDN?").strip()
                    print("  back    : %s" % idn)
                    back = True
                    d2.close()
                    break
            except Exception:
                pass
        time.sleep(1.0)

    if not back:
        sys.exit("the meter did not come back within %d s" % wait)
    print("\ninstall finished. Verify with: MENU > Settings (title should read the "
          "Chinese word for Settings).")


main()
