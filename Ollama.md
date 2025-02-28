# Ollama setup
1. Download and install [Ollama](https://ollama.com/)
2. Once Ollama is running on your system, run `ollama pull llama3.1`
> Currently this is a ~5GB download, it's best to download it before the workshop if you plan on using it
3. Update the `MODEL_NAME` in your `dot.env` file to `ollama`

You're now ready to begin the workshop! Head back to the [Readme.md](Readme.md)

## Restarting the workshop 
Mixing use of llama and openai on the same Redis instance can cause unexpected behavior. If you want to switch from one to the other it is recommended to kill and re-create the instance. To do this:
1. Run `docker ps` and take note of the ID for the running image
2. `docker stop imageId`
3. `docker rm imageId`
4. Start a new instance using the command from earlier, `docker run -d --name redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest`