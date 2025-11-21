import google.generativeai as genai

API_KEY = "AIzaSyCgN-Q9ozME_wk7t839tSavXlYOVrzvxWo"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-pro")

def chat_with_ai(prompt):
    response = model.generate_content(prompt)
    return response.text

def get_agriculture_answer(prompt, context=None):
    try:
        if context:
            prompt = f"{prompt} Contexto: {context}"
        answer = model.generate_content(prompt)
        return {"answer": answer.text}
    except Exception as e:
        return {"answer": f"Error interno IA: {str(e)}"}

if __name__ == "__main__":
    user_input = input("Escribe tu mensaje: ")
    print("IA:", chat_with_ai(user_input))
