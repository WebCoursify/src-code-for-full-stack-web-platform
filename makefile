
pack:
	git checkout 1-basic
	rm -rf project.tar
	tar --exclude=src/upload --exclude=*.pyc --exclude=src/.idea --exclude=*.DS_Store* --exclude=.git -cvf project.tar src test data
