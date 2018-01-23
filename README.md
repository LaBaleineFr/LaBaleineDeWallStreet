
How to deploy and start
=======================

docker build -t bot .
docker run --env SETTINGS=config/<name>.yml --env DISCORD_TOKEN=<token> bot
