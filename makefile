SHORT_NAME=surl
NAME=hjcian/surl

.PHONY: build start

build:
	docker image build -t ${NAME} .

run:
	docker run -it --rm -p 12345:12345 --name ${SHORT_NAME} ${NAME}

dbrun:
	docker-compose -f docker-compose-db.yml up