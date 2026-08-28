import os
import json
import logging
import azure.functions as func


CATEGORIES = [
    {
        "id": "it-support",
        "name": "IT Support",
        "description": "Hardware, software, network, and account issues"
    },
    {
        "id": "facilities",
        "name": "Facilities",
        "description": "Building maintenance, cleaning, and equipment"
    },
    {
        "id": "course-registration",
        "name": "Course Registration",
        "description": "Enrollment, timetables, and academic records"
    },
    {
        "id": "student-finance",
        "name": "Student Finance",
        "description": "Fees, payments, scholarships, and financial aid"
    },
    {
        "id": "library-services",
        "name": "Library Services",
        "description": "Books, journals, study spaces, and resources"
    },
    {
        "id": "general-enquiry",
        "name": "General Enquiry",
        "description": "General questions and information requests"
    }
]


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Categories requested.')

    return func.HttpResponse(
        json.dumps(CATEGORIES),
        mimetype="application/json",
        status_code=200
    )
