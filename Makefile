install:
	install -p -m 0755 ./cli/vercajk $$HOME/.local/bin
	mkdir -p $$HOME/.local/share/vercajk
	echo $$(pwd) >> vercajk_path
	mv vercajk_path $$HOME/.local/share/vercajk
	vercajk update
