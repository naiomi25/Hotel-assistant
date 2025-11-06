from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.2:3b",
                base_url="http://localhost:11434",)

def generate_response(prompt: str) -> str:

    response = llm.invoke(prompt)
    return response.strip()