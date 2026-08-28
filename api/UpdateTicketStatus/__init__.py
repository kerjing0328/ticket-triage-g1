import os
import json
import logging
import azure.functions as func
from azure.cosmos import CosmosClient
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared.secrets import get_secret


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request to update ticket status.')

    try:
        req_body = req.get_json()
        ticket_id = req_body.get('id')
        new_status = req_body.get('status')

        if not ticket_id or not new_status:
            return func.HttpResponse("Missing 'id' or 'status' in request body.", status_code=400)

        cosmos_string = get_secret("COSMOS_CONNECTION_STRING")
        cosmos_client = CosmosClient.from_connection_string(cosmos_string)
        database = cosmos_client.get_database_client("Helpdesk")
        container = database.get_container_client("Tickets")

        query = "SELECT * FROM c WHERE c.id = @id"
        items = list(container.query_items(
            query=query,
            parameters=[{"name": "@id", "value": ticket_id}],
            enable_cross_partition_query=True
        ))

        if not items:
            return func.HttpResponse("Ticket not found.", status_code=404)

        item = items[0]
        item['status'] = new_status

        container.replace_item(item=item['id'], body=item)

        return func.HttpResponse(
            json.dumps({"message": "Ticket status updated successfully"}),
            mimetype="application/json",
            status_code=200
        )

    except ValueError:
        return func.HttpResponse("Invalid JSON format.", status_code=400)
    except Exception as e:
        logging.error(f"Error updating ticket status: {e}")
        return func.HttpResponse("Internal Server Error.", status_code=500)
