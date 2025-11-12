import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
# from langchain_ollama import OllamaLLM

# llm = OllamaLLM(model="llama3.2:3b",
#                 base_url="http://localhost:11434",)



llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.8
)

def generate_response(prompt: str) -> str:
    """
    Genera una respuesta del asistente Nayra (Hotel Horizonte Azul)
    usando el modelo ChatOpenAI integrado con LangSmith.
    """

    try:
        print("\n🧠 [LangChain] Generando respuesta con GPT-4o-mini...")
        print(f"📨 Prompt enviado (resumen): {prompt[:80]}...")

       
        system_prompt = (
            "Eres **Nayra**, la asistente virtual del **Hotel Horizonte Azul**, "
            "un hotel costero en Tenerife. Tu tono es cálido, profesional y natural, "
            "como el de una recepcionista amable. Hablas siempre en primera persona, "
            "sin mencionar tecnología, IA ni sistemas. Tu objetivo es ayudar a los huéspedes "
            "a disfrutar su estancia: darles la bienvenida, ofrecer actividades, "
            "recomendar planes según el clima y coordinar transporte si lo desean. "
            "Tu estilo es breve, claro y humano — siempre terminas tus mensajes con una nota amable o de cortesía."
        )

       
        response = llm.invoke([
            ("system", system_prompt),
            ("user", prompt)
        ])

        answer = response.content.strip()
       

        print("✅ [LangChain] Respuesta recibida correctamente.\n")
        return answer

    except Exception as e:
        print(f"❌ [Error LLM]: {e}\n")
        return "⚠️ Lo siento, no puedo generar una respuesta en este momento."