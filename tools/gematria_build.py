#!/usr/bin/env python3
# Erzeugt data/gematria_1_400.json aus data/gematria_base.yml
import json, yaml, pathlib

BASE = pathlib.Path('data/gematria_base.yml')
OUT  = pathlib.Path('data/gematria_1_400.json')

def main():
    base = yaml.safe_load(BASE.read_text(encoding='utf-8'))
    maxv = 400
    table = {str(i): i for i in range(1, maxv+1)}
    OUT.write_text(json.dumps(table, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"OK gematria 1..{maxv} -> {OUT}")

if __name__ == '__main__':
    main()
