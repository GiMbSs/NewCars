import logging
import os
from typing import Optional

from openai import OpenAI

logger = logging.getLogger('app')


def get_ai_description(model: str, brand: str, year: int) -> str:
    """Gera uma descrição atraente para um carro usando a API de IA.

    Retorna uma string de fallback caso a API falhe ou não esteja configurada.
    """
    api_key = os.getenv('AI_API_KEY')
    if not api_key:
        logger.warning('AI_API_KEY não configurada. Pulando geração de descrição.')
        return ''

    try:
        client = OpenAI(api_key=api_key, base_url='https://api.deepseek.com')
        prompt = (
            f'Crie uma descrição atraente para um carro {brand} modelo {model} '
            f'do ano {year}, apontando detalhes específicos do modelo que possam '
            f'interessar potenciais compradores. Retorne uma resposta com no '
            f'máximo 300 caracteres.'
        )
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {'role': 'system', 'content': 'Você é um especialista em descrições de carros.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=300,
            stream=False,
        )
        content = response.choices[0].message.content
        return content.strip() if content else ''
    except (IndexError, AttributeError) as exc:
        logger.error('Resposta inesperada da API de IA: %s', exc)
        return ''
    except Exception as exc:
        logger.error('Erro ao chamar API de IA: %s', exc)
        return ''