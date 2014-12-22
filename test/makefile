
load:
	cd ../data/; python parse.py rawdata data.jsonl
	python load_data.py

1_basic:
	python test_basic.py

# Chapter2: Controller
2_controller:
	python test_controller.py
	
2_controller_heart_beat:
	python test_controller.py HeartBeatTestCase

2_controller_files:
	python test_controller.py FilesTestCase

# Chapter3: Model
3_model:
	python test_model.py

3_model_search:
	python test_model.py SearchTestCase

3_model_article:
	python test_model.py ArticleTestCase

3_model_follow:
	python test_model.py FollowRelationTestCase



install:
	pip install mysql-python
	pip install monsql
	pip install pyquery