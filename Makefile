build:
	pip install build
	pip install twine
	python -m build
	python -m twine upload dist/*
	$(MAKE) doc
	$(MAKE) clear

test-build:
	pip install -e .
	$(MAKE) doc
	$(MAKE) clear

doc:
	bash scripts/build.sh

clear:
#                                Change app_name below
	rm -rf pc_zap_scrapper.egg-info
	rm -rf dist
	
uninstall:
#                                Change app_name below
	pip uninstall pc_zap_scrapper -y

activate:
#                                Change app_name below
	conda activate pc_zap_scrapper

env-create:
#                                Change app_name below
	conda env create -n pc_zap_scrapper --file environment.yml

env-clear:
#                                Change app_name below
	conda env remove -n pc_zap_scrapper