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
	\cp -f ./shell/bash/config.fish $$HOME/.config/fish/config.fish

update-shell: update_bash update_fish

update-vim:
	\cp -f ./vim/.vimrc $$HOME/; \
	vim $$HOME/.vimrc -c PlugInstall -c wqa

update: update_autostart update_conky update_konsave update_git update_shell \
            update_vim
