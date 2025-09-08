SHELL := /bin/zsh
TZ := Europe/Brussels

.PHONY: build gematria checksums verify push all

all: build verify

build:
	./etz-compile --src data/etz/segments --out out --index data/etz/etz.jsonl --gloss data/glossary.yml
	@for d in data/etz/etzchajim/*; do \
	  ./etz-compile --src "$$d" --out out --index data/etz/etz.jsonl --gloss data/glossary.yml; \
	done

gematria:
	python3 tools/gematria_build.py

checksums:
	rm -f CHECKSUMS.sha256
	find data tools out -type f \
	  ! -name "*.DS_Store" -print0 | sort -z | xargs -0 shasum -a 256 > CHECKSUMS.sha256

verify:
	[ -x verify.sh ] && bash verify.sh || echo "verify.sh (optional) nicht gefunden – ok"

push:
	[ -d .git ] || git init
	git add .
	git commit -m "build(kreisrund): Q! Upgrade (WWAQ, Kaf/Kuf, Gematria); $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
	git branch -M main
	git remote remove origin 2>/dev/null || true
	git remote add origin git@github.com:Jeremia1964/yechida-kreisrund.github.io.git
	git push -u origin main
