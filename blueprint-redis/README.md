## Redis

- Versatile technology that can be used in number of circumstances: 
  - Caches
  - Distributed Locks
  - Leaderboards
  - as a replacement for Kafka in certain instances

- Single Threaded, In-Memory Data Structure Server


### Install Redis & Start redis Server

```shell 
brew --version

brew install redis

# To launch Redis Server in Foreground
redis-server 

# To launch Redis Server in Background
brew services start redis
brew services info redis
brew services stop redis

# Connect to Redis (via Terminal)
redis-cli
```

```shell
# Pull and run Redis
docker run -d -p 6379:6379 --name local-standalone-redis redis:7-alpine

# Verify it's running
docker ps

# Connect to Redis (via Docker)
docker exec -it local-standalone-redis redis-cli
```

Gossip Protocol -> Redis shares updates to replica nodes
