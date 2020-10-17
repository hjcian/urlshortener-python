SHORT_NAME=surl
NAME=hjcian/surl

.PHONY: build start

build:
	docker image build -t ${NAME} .

run:
	docker run -it --rm -p 12345:12345 --name ${SHORT_NAME} ${NAME}

dbrun:
	DBMODE=mongodb python main.py
# TODO:
# docker run -it --rm -p 12345:12345 -e DBMODE=mongodb --name ${SHORT_NAME} ${NAME}