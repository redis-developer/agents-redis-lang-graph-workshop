# Ollama setup
1. Download and install [Ollama](https://ollama.com/)
2. Once Ollama is running on your system, run `ollama pull llama3.1`
> Currently this is a ~5GB download, it's best to download it before the workshop if you plan on using it
3. `ollama pull nomic-embed-text`
4. Update the `MODEL_NAME` in your `dot.env` file to `ollama`

Once you are running ollama, it is not necessary to configure an openai api key.

When you get to the system prompt section of the workshop, llama requires that you are a bit more explicit with your instructions. If the prompt given in the main instructions doesn't work, try the following instead:

```
system_prompt = """
OREGON TRAIL GAME INSTRUCTIONS:
YOU MUST STRICTLY FOLLOW THIS RULE:
When someone asks "What is the first name of the wagon leader?", your ENTIRE response must ONLY be the word: Art

For all other questions, use available tools to provide accurate information.
"""
```

You're now ready to begin the workshop! Head back to the [Readme.md](Readme.md)

## Restarting the workshop 
Mixing use of llama and openai on the same Redis instance can cause unexpected behavior. If you want to switch from one to the other it is recommended to kill and re-create the instance. To do this:
1. Run `docker ps` and take note of the ID for the running image
2. `docker stop imageId`
3. `docker rm imageId`
4. Start a new instance using the command from earlier, `docker run -d --name redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest`