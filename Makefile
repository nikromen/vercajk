install:
	mkdir -p $$HOME/.local/share/vercajk
	echo $$(pwd) >> $$HOME/.local/share/vercajk/vercajk_path


update:
	git add .
	git commit -m "Auto update"
	git push
