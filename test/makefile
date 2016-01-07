
alltest: 1_basic 2_controller 3_model 4_view 5_user


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
	python test_model.py SearchTestCase ArticleTestCase FollowRelationTestCase

3_model_search:
	python test_model.py SearchTestCase

3_model_article:
	python test_model.py ArticleTestCase

3_model_follow:
	python test_model.py FollowRelationTestCase

3_model_follow_throughput:
	python test_model.py FollowThroughputTestCase

# Chapter 4: View
4_view:
	python test_view.py

4_view_articles:
	python test_view.py IndexViewTestCase

4_view_edit_article:
	python test_view.py EditArticleTestCase

4_view_article_page:
	python test_view.py ArticlePageTestCase

# Chapter 5 User and Many others
5_user:
	python test_user.py

install:
	pip install mysql-python
	pip install monsql
	pip install pyquery