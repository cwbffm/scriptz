import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import crashnative as cn


def make_nsd(v1=False):
    count = 1
    n = 0x520+8+0x210+4+4 if v1 else 0x408+8
    d = bytearray(n)
    struct.pack_into("<II", d, 0x400, 1, count)
    if v1:
        struct.pack_into("<III", d, 0x40C, 2, 2, 2)
        struct.pack_into("<II", d, 0x520, 0, 1)
        pal = 0x520+8+0x210
        struct.pack_into("<HH", d, pal, 0x7FFF, 0x001F)
        d[pal+4:pal+8] = bytes([0, 1, 1, 0])
    else:
        struct.pack_into("<II", d, 0x408, 0, 1)
    return bytes(d)


def make_page():
    p = bytearray(cn.PAGE)
    struct.pack_into("<HHIII", p, 0, 0x1234, 0, 1, 1, 0)
    struct.pack_into("<II", p, 0x10, 0x18, 0x28)
    struct.pack_into("<IIII", p, 0x18, 0x0100FFFF, 1, 11, 0)
    return bytes(p)


class FormatTests(unittest.TestCase):
    def test_eid(self):
        self.assertEqual(cn.eid_name(0), "0000.0")
        self.assertEqual(len(cn.eid_name(0x6396347F)), 6)

    def test_nsd_v0(self):
        result = cn.nsd_index(make_nsd())
        self.assertEqual(result["version"], "v0")
        self.assertEqual(result["declared_chunks"], 1)
        self.assertEqual(result["lookup"][0]["chunk"], 0)

    def test_nsd_v1_loading_screen(self):
        nsd = make_nsd(True)
        meta = cn.nsd_index(nsd)
        self.assertEqual(meta["version"], "v1")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.bmp"
            self.assertTrue(cn.write_bmp(nsd, meta, path))
            self.assertEqual(path.read_bytes()[:2], b"BM")

    def test_decompress_literal_prefix(self):
        # Synthetic compressed chunk; real chunks must additionally
        # respect their on-disc sector alignment and size constraints.
        prefix = b"\x34\x12\x00\x00"
        raw = (struct.pack("<HHII", 0x1235, 0, len(prefix), 0)
               + bytes([len(prefix)]) + prefix
               + bytes(cn.PAGE-len(prefix)))
        decoded = cn.inflate_page(raw)
        self.assertEqual(len(decoded), cn.PAGE)
        self.assertEqual(decoded[:4], prefix)

    def test_decode_child_gool(self):
        result = cn.decode_page(make_page())
        self.assertEqual(result["family"], 0)
        self.assertEqual(result["entries"][0]["kind"], "GOOL")

    def test_zip_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "Crash.zip"
            exe = bytearray(2048)
            exe[:8] = b"PS-X EXE"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("SCUS_949.00", exe)
                z.writestr("S0/S0000003.NSD", make_nsd())
                z.writestr("S0/S0000003.NSF", make_page())
            output = Path(tmp)/"out"
            old_argv = sys.argv
            try:
                sys.argv = ["crashnative", str(archive), "--out", str(output)]
                cn.main()
            finally:
                sys.argv = old_argv
            result = json.loads((output/"analysis.json").read_text())
            self.assertEqual(len(result["levels"]), 1)
            self.assertEqual(result["levels"][0]["asset_types"]["GOOL"], 1)
            self.assertTrue(result["executable"]["valid"])


if __name__ == "__main__":
    unittest.main()
