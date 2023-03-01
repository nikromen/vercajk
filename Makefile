update-autostart:
	mkdir -p $$HOME/.config/startup-scripts; \
	\cp -f ./autostart/* $$HOME/.config/startup-scripts

update-conky:
	mkdir -p $$HOME/.config/conky; \
	\cp -f ./conky $$HOME/.config/conky

update-konsave:
	konsave -r the-best-kde-profile; \
	konsave -i ./konsave/the-best-kde-profile.knsv; \
	konsave -a the-best-kde-profile

update-git:
	\cp -f ./git/.gitconfig $$HOME

update-bash:
	mkdir -p $$HOME/.config/shell; \
	\cp -f ./shell/bash/* $$HOME/.config/shell

update-fish:
	\cp -f ./shell/fish/config.fish $$HOME/.config/fish/config.fish

update-shell: update-bash update-fish

update-vim:
	\cp -f ./vim/.vimrc $$HOME/; \
	vim $$HOME/.vimrc -c PlugInstall -c wqa

update: update-autostart update-conky update-konsave update-git update-shell \
            update-vim
