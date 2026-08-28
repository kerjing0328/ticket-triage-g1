import os
import json
import logging
import azure.functions as func
from azure.cosmos import CosmosClient
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared.secrets import get_secret


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request to get all tickets.')

    try:
        cosmos_string = get_secret("COSMOS_CONNECTION_STRING")
        cosmos_client = CosmosClient.from_connection_string(cosmos_string)
        database = cosmos_client.get_database_client("Helpdesk")
        container = database.get_container_client("Tickets")

        items = list(container.read_all_items())
        
        return func.HttpResponse(
            json.dumps(items),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error fetching tickets: {e}")
        return func.HttpResponse("Internal Server Error.", status_code=500)
