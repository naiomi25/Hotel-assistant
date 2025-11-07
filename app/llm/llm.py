# from langchain_ollama import OllamaLLM

# llm = OllamaLLM(model="llama3.2:3b",
#                 base_url="http://localhost:11434",)

# def generate_response(prompt: str) -> str:

#     response = llm.invoke(prompt)
#     return response.strip()
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(prompt: str) -> str:
   

    try:
        print("\n🧠 [OpenAI] Generando respuesta con GPT-5 Mini...")
        print(f"📨 Prompt enviado (resumen): {prompt[:80]}...")  
        

        response = client.chat.completions.create(
              model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres **Nayra**, la asistente virtual del **Hotel Horizonte Azul**, un hotel costero en Tenerife. "
                        "Tu tono es cálido, profesional y natural, como el de una recepcionista amable. "
                        "Hablas siempre en primera persona, sin mencionar tecnología, IA ni sistemas. "
                        "Tu objetivo es ayudar a los huéspedes a disfrutar su estancia: darles la bienvenida, "
                        "ofrecer actividades, recomendar planes según el clima y coordinar transporte si lo desean. "
                        "Tu estilo es breve, claro y humano — siempre terminas tus mensajes con una nota amable o de cortesía."
                                        ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )

        answer = response.choices[0].message.content.strip()
        total_tokens = getattr(response.usage, "total_tokens", "N/A") if hasattr(response, "usage") else "N/A"
        print(f"🔢 Tokens usados: {total_tokens}")
        print("✅ [OpenAI] Respuesta recibida correctamente.\n")
        return answer

    except Exception as e:
        print(f"❌ [Error OpenAI]: {e}\n")
        return "⚠️ Lo siento, no puedo generar una respuesta en este momento."
