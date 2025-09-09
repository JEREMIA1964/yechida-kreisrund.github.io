#!/usr/bin/env python3
# YAML -> VTT-R + JSONL-Index, optional Glossarprüfung (L2)
import sys, json, hashlib, pathlib, re
from datetime import datetime
import yaml

X_UNITS = "ticks"

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_yaml(p):
    with open(p, 'rb') as f:
        data = f.read()
    obj = yaml.safe_load(data)
    return obj, data

class Glossar:
    def __init__(self, path: pathlib.Path|None):
        self.path = path
        self.alias = {}
        self.kanon = {}
        if path:
            self._load(path)

    def _load(self, path: pathlib.Path):
        obj, _ = load_yaml(path)
        for g in obj.get('begriffe', []):
            gid = g['id']; self.kanon[gid] = g
            names = set()
            names.update(g.get('regeln', {}).get('erlaubte_schreibungen', []))
            l = g.get('lemma', {})
            if isinstance(l, dict):
                for k in ('de','translit','he'):
                    v = l.get(k);  v and names.add(str(v))
            for a in g.get('abk', []): names.add(a)
            for name in names: self.alias[name] = gid
        for k, v in obj.get('alias', {}).items():
            self.alias[k] = v

    def scan_text(self, text: str):
        hits = []
        for name, gid in sorted(self.alias.items(), key=lambda x: -len(x[0])):
            pattern = r'(?:\b|^)' + re.escape(name) + r'(?:\b|$)'
            if re.search(pattern, text):
                hits.append({'name': name, 'gid': gid})
        uniq = {}
        for h in hits: uniq.setdefault(h['gid'], h)
        return list(uniq.values())

def emit_vttr(obj, gloss: 'Glossar|None'):
    lines = ["WEBVTT", f"X-UNITS: {X_UNITS}"]
    for s in obj.get('spur',{}).get('segmente',[]):
        if 'ende' in s: end = s['ende']
        elif 'end' in s: end = s['end']
        else: raise ValueError('Segment ohne ende/end')
        start = s['start']; sid = s['sid']
        ringe = s.get('ringe',{})
        l2 = str(ringe.get('L2',''))
        gloss_hits = gloss.scan_text(l2) if gloss else []
        paradigma = s.get('paradigma')  # z.B. "checksum"

        lines.append("")
        lines.append(sid)
        lines.append(f"t={start} --> t={end}")
        for L in ('L0','L1','L2','L3','L4','L5'):
            lines.append(f"{L}: {ringe.get(L,'')}")
        if gloss_hits:
            annot = ",".join([f"{h['gid']}({h['name']})" for h in gloss_hits])
            lines.append(f"X-GLOSS: {annot}")
        if paradigma:
            lines.append(f"X-PARADIGMA: {paradigma}")
    return ("\n".join(lines) + "\n").encode('utf-8')

def emit_index(obj, src_bytes, vttr_bytes, src_path):
    now = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    entry = {
        'id': obj['id'],
        'stable_ref': obj.get('stable_ref'),
        'src_path': str(src_path),
        'src_sha256': sha256_bytes(src_bytes),
        'vttr_sha256': sha256_bytes(vttr_bytes),
        'units': X_UNITS,
        'count_segments': len(obj.get('spur',{}).get('segmente',[])),
        'created_utc': now
    }
    return (json.dumps(entry, ensure_ascii=False) + "\n").encode('utf-8')

def main():
    import argparse
    ap = argparse.ArgumentParser(description='etz-compile (ticks) + Glossar + Paradigma')
    ap.add_argument('--src', default='data/etz/segments', help='YAML-Segmente')
    ap.add_argument('--out', default='out', help='Ausgabeverzeichnis')
    ap.add_argument('--index', default='data/etz/etz.jsonl', help='Index-Datei')
    ap.add_argument('--gloss', default=None, help='Glossar YAML (optional)')
    args = ap.parse_args()

    src_dir = pathlib.Path(args.src)
    out_dir = pathlib.Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    index_path = pathlib.Path(args.index); index_path.parent.mkdir(parents=True, exist_ok=True)
    gloss = Glossar(pathlib.Path(args.gloss)) if args.gloss else None

    with open(index_path, 'ab') as idx:
        for yp in sorted(src_dir.glob('*.yaml')):
            obj, ybytes = load_yaml(yp)
            vttr = emit_vttr(obj, gloss)
            base = obj['id'].replace(':','_')
            vttr_path = out_dir / f"{base}.vtt-r"
            with open(vttr_path, 'wb') as f:
                f.write(vttr)
            idx.write(emit_index(obj, ybytes, vttr, yp))
            print(f"OK {yp.name} -> {vttr_path.name}")

if __name__ == '__main__':
    main()
