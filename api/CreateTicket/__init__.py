import os
import json
import logging
import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.cosmos import CosmosClient, PartitionKey
import uuid
import datetime

def classify_ticket(description: str) -> str:
    """
    Sends the description to Azure AI Language to extract key phrases, 
    then matches them against our university Helpdesk categories.
    """
    try:
        # Connect to Azure AI Language
        ai_endpoint = os.environ["AI_LANGUAGE_ENDPOINT"]
        ai_key = os.environ["AI_LANGUAGE_KEY"]
        text_client = TextAnalyticsClient(endpoint=ai_endpoint, credential=AzureKeyCredential(ai_key))
        
        # Extract Key Phrases (Zero Training)
        response = text_client.extract_key_phrases(documents=[description])[0]
        logging.info(f"AI Response: {response}")
        
        if not response.is_error:
            # Convert extracted phrases to lowercase for easy matching
            phrases = [phrase.lower() for phrase in response.key_phrases]
            logging.info(f"AI Extracted Phrases: {phrases}")
            
            # Map the AI's findings to your Helpdesk categories
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
                    
        # Fallback if Azure AI returns no strong keywords
        return "General Enquiry"
        
    except Exception as e:
        logging.error(f"AI Classification Error: {e}")
        return "General Enquiry"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing new ticket submission.')

    try:
        # 1. Read data from the frontend form
        req_body = req.get_json()
        description = req_body.get('description', '')
        
        # 2. Run the AI classification
        suggested_category = classify_ticket(description)
        
        # 3. Prepare the document for Cosmos DB
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
        
        # 4. Connect to Cosmos DB and save the ticket
        cosmos_string = os.environ["COSMOS_CONNECTION_STRING"]
        cosmos_client = CosmosClient.from_connection_string(cosmos_string)
        database = cosmos_client.get_database_client("Helpdesk")
        container = database.get_container_client("Tickets")
        
        container.create_item(body=ticket_document)
        
        # 5. Return success response to the frontend
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