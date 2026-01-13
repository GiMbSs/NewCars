from openai import OpenAI
import os

def get_ai_description(model, brand, year):
    client = OpenAI(api_key=os.getenv('AI_API_KEY', None), base_url="https://api.deepseek.com")
    prompt = f'Crie uma descrição atraente para um carro {brand} modelo {model} do ano {year}, apontando detalhes especificos do modelo que possam interessar potenciais compradores. Retorne uma resposta com no maximo 300 caracteres.'
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "Você é um especialista em descrições de carros."},
        {"role": "user", "content": prompt},
    ],     max_tokens=300,
    stream=False
    )
    return response.choices[0].message.content