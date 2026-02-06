"""
DGB AUDIO - AI Support Chat Service
====================================
Intelligent chat trained for different support departments.
Uses user's own OpenAI API key (BYOK) for requests.
"""

from datetime import datetime
from typing import Optional, List
import json

# Department configurations with specialized knowledge
DEPARTMENTS = {
    "technical": {
        "name": "Soporte Técnico",
        "icon": "🔧",
        "system_prompt": """Eres un experto técnico de DGB AUDIO. Tu conocimiento incluye:
        
- Configuración de samples de música tropical (Bolero, Bachata, Merengue, Salsa)
- Conversión de audio a MIDI
- Grabación en tiempo real de instrumentos
- Formatos de audio (WAV, MP3, AIFF, FLAC)
- Integración con DAWs (Logic Pro, Ableton, FL Studio)
- Configuración de API Keys de OpenAI
- Solución de problemas de upload y procesamiento

Responde siempre en español de manera clara y paso a paso.
Si no sabes algo, admítelo y sugiere contactar a un humano."""
    },
    "sales": {
        "name": "Ventas",
        "icon": "💼",
        "system_prompt": """Eres un representante de ventas de DGB AUDIO. Tu conocimiento incluye:

PLANES DISPONIBLES:
- Starter (Gratis): 1GB storage, 30s grabación, 2 proyectos
- Creator ($19/mes): 10GB storage, 60s grabación, 20 proyectos  
- Pro ($49/mes): 50GB storage, grabación ilimitada, proyectos ilimitados
- Studio ($149/mes): 200GB storage, API access, soporte prioritario

CARACTERÍSTICAS:
- BYOK (Bring Your Own Key): Cada usuario usa su propia API de OpenAI
- Sample Library para música tropical
- Generación de música por prompts
- Grabación en tiempo real
- Exportación a MIDI y audio

Responde amablemente, destaca beneficios, y guía hacia la compra."""
    },
    "billing": {
        "name": "Facturación",
        "icon": "💳",
        "system_prompt": """Eres un agente de facturación de DGB AUDIO. Tu conocimiento incluye:

POLÍTICAS:
- Pagos mensuales via Stripe
- Cancelación en cualquier momento
- Reembolso proporcional si cancela antes del fin del mes
- Upgrades se aplican inmediatamente
- Downgrades al final del período

PRECIOS:
- Starter: Gratis
- Creator: $19/mes
- Pro: $49/mes
- Studio: $149/mes

Ayuda con problemas de facturación, cambios de plan, y métodos de pago."""
    },
    "general": {
        "name": "Asistente General",
        "icon": "🎵",
        "system_prompt": """Eres el asistente virtual de DGB AUDIO - La Inteligencia de la Música Tropical.

DGB AUDIO es una plataforma SaaS para crear música tropical auténtica usando IA:
- Géneros: Bolero, Bachata, Merengue, Salsa, Vallenato, Cumbia
- Herramientas: Sample Library, Generación por prompts, Grabación real-time
- Para: Productores, artistas, compositores de música latina

Puedes ayudar con:
- Preguntas generales sobre la plataforma
- Cómo empezar
- Redirigir a departamentos especializados

Si la pregunta es técnica, de ventas o facturación, sugiere el departamento apropiado."""
    }
}


def get_departments() -> List[dict]:
    """Get list of available departments"""
    return [
        {
            "id": dept_id,
            "name": dept["name"],
            "icon": dept["icon"]
        }
        for dept_id, dept in DEPARTMENTS.items()
    ]


async def chat_with_support(
    message: str,
    department: str,
    api_key: str,
    conversation_history: List[dict] = None
) -> dict:
    """
    Send a message to the AI support chat.
    Uses the user's own OpenAI API key.
    """
    if not api_key:
        return {
            "error": "API key not configured",
            "message": "Por favor configura tu API Key de OpenAI en el Dashboard."
        }
    
    dept_config = DEPARTMENTS.get(department, DEPARTMENTS["general"])
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Build messages
        messages = [
            {"role": "system", "content": dept_config["system_prompt"]}
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Estimate cost (GPT-4o-mini pricing)
        cost_estimate = tokens_used * 0.00015 / 1000  # ~$0.15 per 1M tokens
        
        return {
            "success": True,
            "department": department,
            "department_name": dept_config["name"],
            "message": assistant_message,
            "tokens_used": tokens_used,
            "cost_estimate": cost_estimate,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": "Chat failed",
            "message": str(e)
        }


def get_quick_responses(department: str) -> List[str]:
    """Get quick response suggestions for a department"""
    quick_responses = {
        "technical": [
            "¿Cómo subo mis samples?",
            "¿Cómo convierto audio a MIDI?",
            "¿Por qué mi archivo no se procesa?",
            "¿Cómo configuro mi API Key?"
        ],
        "sales": [
            "¿Cuál plan me recomiendas?",
            "¿Qué incluye el plan Pro?",
            "¿Hay descuentos anuales?",
            "¿Puedo probar antes de comprar?"
        ],
        "billing": [
            "¿Cómo cambio mi plan?",
            "¿Puedo obtener un reembolso?",
            "¿Cómo cancelo mi suscripción?",
            "¿Dónde veo mis facturas?"
        ],
        "general": [
            "¿Qué es DGB AUDIO?",
            "¿Cómo empiezo?",
            "¿Qué géneros musicales soporta?",
            "¿Necesito saber programar?"
        ]
    }
    
    return quick_responses.get(department, quick_responses["general"])
