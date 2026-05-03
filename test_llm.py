from crewai import LLM

llm = LLM(
    model="ollama/qwen2.5",
    base_url="http://localhost:11434/v1"
)

response = llm.call(messages=[{"role": "user", "content": "Hello"}])
print(response)
