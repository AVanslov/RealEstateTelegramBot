up:
	sudo docker compose up
	
rebuild:
	sudo docker compose down --volumes --remove-orphans && sudo docker compose up --build

clear_docker:
	sudo docker container prune
	sudo docker container ls -a
	sudo docker image prune
	sudo docker image rm serbia-real-estate-bot2-0-api serbia-real-estate-bot2-0-nginx
	sudo docker image ls -a
	sudo docker volume ls
