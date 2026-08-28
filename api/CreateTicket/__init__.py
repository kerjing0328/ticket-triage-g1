import os
import json
import logging
import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.cosmos import CosmosClient, PartitionKey
import uuid
import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared.secrets import get_secret

def classify_ticket(description: str) -> str:
    try:
        ai_endpoint = get_secret("AI_LANGUAGE_ENDPOINT")
        ai_key = get_secret("AI_LANGUAGE_KEY")
        text_client = TextAnalyticsClient(endpoint=ai_endpoint, credential=AzureKeyCredential(ai_key))
        
        response = text_client.extract_key_phrases(documents=[description])[0]
        logging.info(f"AI Response: {response}")
        
        if not response.is_error:
            phrases = [phrase.lower() for phrase in response.key_phrases]
            logging.info(f"AI Extracted Phrases: {phrases}")
            
            for phrase in phrases:
                if any(word in phrase for word in ["wifi", "password", "login", "laptop", "network", "software"]):
                    return "IT Support"
                elif any(word in phrase for word in ["aircon", "toilet", "light", "cleaning", "door", "broken"]):
                    return "Facilities"
                elif any(word in phrase for word in ["timetable", "drop", "enroll", "class", "subject"]):
                    return "Course Registration"
                elif any(word in phrase for word in ["fee", "invoice", "payment", "scholarship", "loan"]):
                    return "Student Finance"
                elif any(word in phrase for word in ["book", "journal", "borrow", "return", "database"]):
                    return "Library Services"
                    
        return "General Enquiry"
        
    except Exception as e:
        logging.error(f"AI Classification Error: {e}")
        return "General Enquiry"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing new ticket submission.')

    try:
        req_body = req.get_json()
        description = req_body.get('description', '')
        
        suggested_category = classify_ticket(description)
        
        ticket_document = {
            "id": str(uuid.uuid4()),
            "name": req_body.get('name', 'Anonymous'),
            "email": req_body.get('email', 'No email provided'),
            "title": req_body.get('title', 'No Title'),
            "description": description,
            "category": suggested_category,
            "priority": req_body.get('priority', 'Medium'),
            "status": "New",
            "createdAt": datetime.datetime.utcnow().isoformat() + "Z"
        }
        
        cosmos_string = get_secret("COSMOS_CONNECTION_STRING")
        cosmos_client = CosmosClient.from_connection_string(cosmos_string)
        database = cosmos_client.get_database_client("Helpdesk")
        container = database.get_container_client("Tickets")
        
        container.create_item(body=ticket_document)
        
        return func.HttpResponse(
            json.dumps({
                "message": "Ticket created successfully",
                "ticketId": ticket_document["id"],
                "category": suggested_category
            }),
            mimetype="application/json",
            status_code=201
        )
        
    except ValueError:
        return func.HttpResponse("Invalid JSON format.", status_code=400)
    except Exception as e:
        logging.error(f"Database Error: {e}")
        return func.HttpResponse("Internal Server Error.", status_code=500)