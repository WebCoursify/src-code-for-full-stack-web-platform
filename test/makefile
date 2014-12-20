
load:
	cd ../data/; python parse.py rawdata data.jsonl
	python load_data.py

1_basic:
	python test_basic.py

2_controller:
	python test_controller.py
	
2_controller_heart_beat:
	python test_controller.py HeartBeatTestCase

2_controller_files:
	python test_controller.py FilesTestCase

install:
	pip install mysql-python
	pip install monsql
	pip install pyquery