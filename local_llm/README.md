# Running LLM Locally

## Ollama

### Chat With Ollama LLMs

- install ollama or build from source code
- run `ollama serve`
- Then you can chat with a selected model either

  - in Terminal

  ```
      ./ollama run llama2
  ```

  - or create an Ollama instance in script

    ```
    llm = Ollama(
    model="mistral",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    )
    print(llm("Tell me riddle"))

    ```

    - `ollam_mistral.py`
