SHORT_NAME=surl
NAME=hjcian/surl

.PHONY: cachemode dbmode build run dbrun

cachemode:
	DBMODE=cachedb python main.py

dbmode:
	DBMODE=mongodb python main.py

build:
	docker image build -t ${NAME} .

run:
	docker run -it --rm -p 12345:12345 --name ${SHORT_NAME} ${NAME}

dbrun:
	docker-compose -f docker-compose.db.yml up

cacherun:
	docker-compose -f docker-compose.cache.db up