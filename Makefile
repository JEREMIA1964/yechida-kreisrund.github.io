SHELL := /bin/zsh
.PHONY: sync
sync:
	git fetch kreis
	git subtree pull --prefix=kreisrund kreis main --squash
	git pull origin main --allow-unrelated-histories || true
	git push --set-upstream origin main
