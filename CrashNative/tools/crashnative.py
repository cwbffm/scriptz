#!/usr/bin/env python3
"""CrashNative: analyze Crash Bandicoot 1 NSD/NSF assets (Python 3.10+).
Read-only on input. Does not redistribute game resources.
Format: https://psx-spx.consoledev.net/dev/ps1/cdr/cdromfileformats/archives/
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import tempfile
import zipfile

PAGE = 65536
SECTOR = 2048
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_!"
TYPES = {1:"SVTX",2:"TGEO",3:"WGEO",4:"SLST",5:"TPAG",6:"LDAT",
         7:"ZDAT",11:"GOOL",12:"ADIO",13:"MIDI",14:"INST",
         15:"IMAG",17:"MDAT",18:"IPAL",19:"PBAK",20:"CVTX"}

def u16(b, p):
    if p < 0 or p+2 > len(b): raise ValueError("u16 out of range")
    return struct.unpack_from("<H", b, p)[0]

def u32(b, p):
    if p < 0 or p+4 > len(b): raise ValueError("u32 out of range")
    return struct.unpack_from("<I", b, p)[0]

def eid_name(eid):
    n = [(eid >> s)&63 for s in (25,19,13,7,1)]
    return "".join(ALPHABET[x] for x in n[:4])+"."+ALPHABET[n[4]]

def nsd_index(data):
    if len(data) < 0x408: raise ValueError("NSD too small")
    chunk_count, count = u32(data,0x400), u32(data,0x404)
    if chunk_count > 20000 or count > 100000:
        raise ValueError("Unreasonable NSD counts")
    if len(data) == 0x408+8*count:
        version, table = "v0", 0x408
        colors = width = height = raw_sector = 0
        descriptors = []
        palette = pixels = None
    else:
        version, table = "v1", 0x520
        if len(data) < table+count*8+0x210:
            raise ValueError("NSD v1 truncated")
        colors, width, height = (u32(data,x) for x in (0x40c,0x410,0x414))
        if colors > 256 or width > 2048 or height > 2048:
            raise ValueError("Invalid NSD bitmap dimensions")
        raw_sector = u32(data,0x418)
        compressed = u32(data,0x41c)
        if compressed > 64: raise ValueError("Invalid compressed page count")
        descriptors = [u32(data,0x420+4*i) for i in range(compressed)]
        palette = table+count*8+0x210
        pixels = palette+2*colors
        if pixels+width*height > len(data):
            raise ValueError("NSD bitmap truncated")
    lookup = []
    for i in range(count):
        p = table+i*8
        eid = u32(data,p+4)
        lookup.append({"chunk":u32(data,p),"eid":f"{eid:08X}",
                       "name":eid_name(eid)})
    return {"version":version,"declared_chunks":chunk_count,
            "lookup":lookup,"first_raw_sector":raw_sector,
            "compressed_descriptors":descriptors,
            "bitmap":{"colors":colors,"width":width,"height":height,
                      "palette":palette,"pixels":pixels}}

def inflate_page(data):
    if len(data)<12 or u16(data,0)!=0x1235:
        raise ValueError("Not a compressed NSF chunk")
    prefix,skip = u32(data,4),u32(data,8)
    if prefix>PAGE or skip>PAGE: raise ValueError("Invalid sizes")
    out=bytearray()
    p=12
    while len(out)<prefix:
        if p>=len(data): raise ValueError("Truncated stream")
        flag=data[p];p+=1
        if flag<0x80:
            if p+flag>len(data) or len(out)+flag>prefix:
                raise ValueError("Truncated literal")
            out.extend(data[p:p+flag]);p+=flag
        else:
            if p>=len(data): raise ValueError("Truncated backref")
            val=((flag&127)<<8)|data[p];p+=1
            distance=val>>3
            length=(val&7)+3
            if length==10:length=64
            if distance==0 or distance>len(out) or len(out)+length>prefix:
                raise ValueError("Bad LZ distance")
            for _ in range(length):out.append(out[-distance])
    p+=skip
    tail=PAGE-prefix
    if p+tail>len(data): raise ValueError("Truncated tail")
    out.extend(data[p:p+tail])
    if len(out)!=PAGE or u16(out,0)!=0x1234:
        raise ValueError("Invalid inflated chunk")
    return bytes(out)

def decode_page(page, export_gool=None):
    if len(page)!=PAGE or u16(page,0)!=0x1234:
        raise ValueError("Bad NSF chunk signature/size")
    family=u16(page,2)
    if family==1:
        return {"family":1,"kind":"TPAG","texture":eid_name(u32(page,4)),
                "entries":[]}
    n=u32(page,8)
    if n>15000 or 0x10+4*(n+1)>PAGE:
        raise ValueError("Bad NSF entry count")
    offsets=[u32(page,0x10+4*i) for i in range(n+1)]
    minimum=0x10+4*(n+1)
    entries=[]
    for i in range(n):
        a,b=offsets[i:i+2]
        if a<minimum or b<a or b>PAGE:
            raise ValueError("Bad NSF entry offsets")
        raw=page[a:b]
        if len(raw)<16 or u32(raw,0)!=0x0100ffff:continue
        eid,typ=u32(raw,4),u32(raw,8)
        name=eid_name(eid)
        entries.append({"name":name,"type":typ,
                        "kind":TYPES.get(typ,"UNKNOWN"),"size":len(raw),
                        "item_count":u32(raw,12)})
        if export_gool is not None and typ==11:
            export_gool.mkdir(parents=True,exist_ok=True)
            safe=re.sub(r"[^A-Za-z0-9_.-]","_",name)
            (export_gool/f"{i:04d}_{safe}.bin").write_bytes(raw)
    return {"family":family,"kind":"normal",
            "page_id":u32(page,4),"entries":entries}

def write_bmp(nsd, meta, path):
    b=meta["bitmap"]
    w,h,count=b["width"],b["height"],b["colors"]
    if not (w and h and count):return False
    palette,pixels=b["palette"],b["pixels"]
    colors=[]
    for i in range(count):
        value=u16(nsd,palette+i*2)
        colors.append(bytes([
            ((value>>10)&31)*255//31,
            ((value>>5)&31)*255//31,
            (value&31)*255//31]))
    stride=((3*w+3)//4)*4
    output=bytearray()
    for y in range(h-1,-1,-1):
        for idx in nsd[pixels+y*w:pixels+(y+1)*w]:
            output.extend(colors[idx] if idx<count else b"\0\0\0")
        output.extend(b"\0"*(stride-3*w))
    header=struct.pack("<2sIHHI",b"BM",54+len(output),0,0,54)
    dib=struct.pack("<IiiHHIIiiII",40,w,h,1,24,0,len(output),2835,2835,0,0)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(header+dib+output)
    return True

def inspect_pair(z, nsd_name, nsf_name, out, dump_gool, preview):
    data=z.read(nsd_name)
    nsd=nsd_index(data)
    result={"name":nsd_name,"nsf":nsf_name,"index":nsd,
            "pages":[],"warnings":[]}
    stem=Path(nsd_name).stem
    if preview and write_bmp(data,nsd,out/"previews"/f"{stem}.bmp"):
        result["preview"]=f"previews/{stem}.bmp"
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"level.nsf"
        with z.open(nsf_name) as src,path.open("wb") as dst:
            shutil.copyfileobj(src,dst,1024*1024)
        size=path.stat().st_size
        result["nsf_bytes"]=size
        raw_start=nsd["first_raw_sector"]*SECTOR if nsd["version"]=="v1" else 0
        if raw_start>size:raise ValueError("Raw extent beyond NSF")
        with path.open("rb") as f:
            for i,desc in enumerate(nsd["compressed_descriptors"]):
                length=(desc&63)*SECTOR
                offset=(desc>>6)*SECTOR
                if not length or offset+length>size:
                    result["warnings"].append(f"compressed {i}: bad extent")
                    continue
                f.seek(offset)
                try:
                    chunk=inflate_page(f.read(length))
                    subdir=(out/"gool"/stem/f"packed_{i}" if dump_gool else None)
                    item=decode_page(chunk,subdir)
                    item.update({"storage":"packed","byte_offset":offset})
                    result["pages"].append(item)
                except ValueError as exc:
                    result["warnings"].append(f"packed {i}: {exc}")
            f.seek(raw_start)
            i=0
            while f.tell()+PAGE<=size:
                offset=f.tell()
                try:
                    subdir=(out/"gool"/stem/f"raw_{i}" if dump_gool else None)
                    item=decode_page(f.read(PAGE),subdir)
                    item.update({"storage":"raw","byte_offset":offset})
                    result["pages"].append(item)
                except ValueError as exc:
                    result["warnings"].append(f"raw {i}: {exc}")
                i+=1
            if f.tell()<size:
                result["warnings"].append(f"{size-f.tell()} trailing bytes")
    result["asset_types"]=dict(Counter(e["kind"] for page in result["pages"]
                                        for e in page["entries"]))
    return result

def analyze_exe(data):
    if len(data)<2048 or data[:8]!=b"PS-X EXE":
        return {"valid":False}
    fields={"entry_pc":0x10,"initial_gp":0x14,"load":0x18,
            "code_size":0x1c,"bss":0x28,"bss_size":0x2c,"stack":0x30}
    return {"valid":True,"sha256":hashlib.sha256(data).hexdigest(),
            "bytes":len(data),
            **{k:f"0x{u32(data,p):08X}" for k,p in fields.items()}}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("archive",type=Path)
    parser.add_argument("--out",type=Path,default=Path("CrashNative-output"))
    parser.add_argument("--limit",type=int,default=0,help="0=all pairs; 1=first")
    parser.add_argument("--dump-gool",action="store_true")
    parser.add_argument("--no-preview",action="store_true")
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    report={"game":"Crash Bandicoot PS1 SCUS-94900",
            "levels":[],"warnings":[]}
    with zipfile.ZipFile(args.archive) as z:
        names={i.filename.replace("\\","/").upper():i.filename for i in z.infolist()
               if not i.is_dir()}
        if "SCUS_949.00" in names:
            report["executable"]=analyze_exe(z.read(names["SCUS_949.00"]))
        else:
            report["warnings"].append("SCUS_949.00 missing")
        nsds=sorted(x for x in names if x.endswith(".NSD"))
        if args.limit>0:nsds=nsds[:args.limit]
        for item in nsds:
            nsf=item[:-4]+".NSF"
            if nsf not in names:
                report["warnings"].append("missing "+nsf)
                continue
            print("Analyzing",item,flush=True)
            try:
                report["levels"].append(inspect_pair(
                    z,names[item],names[nsf],args.out,
                    args.dump_gool,not args.no_preview))
            except (ValueError,OSError) as exc:
                report["warnings"].append(f"{item}: {exc}")
    (args.out/"analysis.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    summary=["CrashNative v0.1: resource inspection, NOT a playable port",
             f"Pairs analyzed: {len(report['levels'])}",
             f"PS-X EXE: {report.get('executable',{})}"]
    summary += [f"{x['name']}: pages {len(x['pages'])}; assets {x['asset_types']}; "
                f"warnings {len(x['warnings'])}" for x in report["levels"]]
    summary += ["WARNING "+w for w in report["warnings"]]
    (args.out/"summary.txt").write_text("\n".join(summary)+"\n",encoding="utf-8")
    print("Reports written to",args.out.resolve())
if __name__=="__main__":
    main()
