SHELL = /bin/sh
CURRENT_UID := $(shell id -u)

shell:
	docker-compose exec ugc_api bash

format:
	docker run --rm -v $(CURDIR):/data cytopia/black . -l 120 -t py38
	docker run --rm -v $(CURDIR):/data chelovek/cisort --profile black --line-length 120 .
