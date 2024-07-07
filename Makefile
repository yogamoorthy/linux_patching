
MAKEFLAGS += --silent

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

run:      ## Provision and executes ansible
	./do/run

test:	## Test ansible execution
	./do/run -c

setup: ## Provision the workspace
	./do/setup
	echo "INFO: Remember to load the python Workspace"
	echo "\t RUN: source ./venv/bin/activate"

cleanup: ## cleanup the workspace
	./do/cleanup
	echo "INFO: Remember drop from your Workspace"
	echo "\t RUN: deactivate"

prune:	## Cleanup the Ansible workspace - keeps python venv
	rm -fr ./ansible/roles
	rm -fr ./ansible/inventories
	rm -fr ./ansible/modules
