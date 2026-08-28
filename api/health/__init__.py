import os
import json
import logging
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health check requested.')

    cosmos_configured = bool(os.environ.get("COSMOS_CONNECTION_STRING"))
    ai_configured = bool(os.environ.get("AI_LANGUAGE_ENDPOINT") and os.environ.get("AI_LANGUAGE_KEY"))

    health = {
        "status": "healthy",
        "storage": "cosmos" if cosmos_configured else "in-memory",
        "classifier": "azure-ai-language" if ai_configured else "keyword-rules",
        "cosmos": {
            "configured": cosmos_configured,
            "endpoint": os.environ.get("COSMOS_ENDPOINT", "not set")
        },
        "aiLanguage": {
            "configured": ai_configured,
            "endpoint": os.environ.get("AI_LANGUAGE_ENDPOINT", "not set")
        }
    }

    return func.HttpResponse(
        json.dumps(health, indent=2),
        mimetype="application/json",
        status_code=200
    )
