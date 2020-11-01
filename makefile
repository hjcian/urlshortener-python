SHORT_NAME=surl
NAME="hjcian/surl"

.PHONY: test cachemode dbmode build run dbrun cacherun

test:
	docker image build -f docker/Dockerfile_test -t ${NAME}-test .
	docker run -it --rm --name=${SHORT_NAME}-test ${NAME}-test

cachemode:
	DBMODE=cachedb python main.py

dbmode:
	DBMODE=mongodb python main.py

build:
	docker image build -f docker/Dockerfile -t ${NAME} .

run: build
	docker-compose -f docker/docker-compose.yml up

dbrun: build
	docker-compose -f docker/docker-compose.db.yml up

cacherun: build
	docker-compose -f docker/docker-compose.cache.db.yml up