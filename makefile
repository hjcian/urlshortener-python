SHORT_NAME=surl
NAME="hjcian/surl"

.PHONY: test cachemode dbmode build run dbrun cacherun

test:
	./env/bin/pytest -v . --cov --cov-config=./.coveragerc

cachemode:
	DBMODE=cachedb python main.py

dbmode:
	DBMODE=mongodb python main.py

build:
	docker image build -f docker/Dockerfile -t ${NAME} .

run:
	docker-compose -f docker/docker-compose.yml up

dbrun:
	docker-compose -f docker/docker-compose.db.yml up

cacherun:
	docker-compose -f docker/docker-compose.cache.db.yml up