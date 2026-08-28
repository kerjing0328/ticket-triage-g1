"""
Seed the API with sample tickets for demonstration.

Usage:
    python scripts/seed_api.py [base_url]

Default base_url: http://localhost:7071/api
"""

import sys
import json
import urllib.request
import urllib.error


SAMPLE_TICKETS = [
    {
        "name": "Alice Chen",
        "email": "alice.chen@university.ac.uk",
        "title": "Cannot access campus Wi-Fi",
        "description": "I cannot connect to the campus Wi-Fi from my laptop. It was working yesterday but now it says 'authentication failed'.",
        "priority": "High"
    },
    {
        "name": "Bob Kumar",
        "email": "bob.kumar@university.ac.uk",
        "title": "Broken air conditioning in Library",
        "description": "The air conditioning in the third floor reading room has been broken for two days. It is very hot and uncomfortable.",
        "priority": "Medium"
    },
    {
        "name": "Carol Singh",
        "email": "carol.singh@university.ac.uk",
        "title": "Need to change my course enrollment",
        "description": "I want to drop Mathematics 201 and enroll in Statistics 301 instead. The deadline is next week.",
        "priority": "Medium"
    },
    {
        "name": "David Lee",
        "email": "david.lee@university.ac.uk",
        "title": "Tuition fee payment issue",
        "description": "I tried to pay my tuition fee online but the payment failed. I need help with the invoice.",
        "priority": "High"
    },
    {
        "name": "Emma Wilson",
        "email": "emma.wilson@university.ac.uk",
        "title": "Cannot renew library books",
        "description": "When I try to renew my library books online, it says I have overdue fines. But I returned them on time.",
        "priority": "Low"
    },
    {
        "name": "Frank Zhang",
        "email": "frank.zhang@university.ac.uk",
        "title": "Projector not working in Room 204",
        "description": "The projector in lecture room 204 is not turning on. I have a presentation in 1 hour.",
        "priority": "Urgent"
    },
    {
        "name": "Grace Kim",
        "email": "grace.kim@university.ac.uk",
        "title": "Password reset for student portal",
        "description": "I forgot my password for the student portal and the reset email is not arriving.",
        "priority": "Medium"
    },
    {
        "name": "Henry Brown",
        "email": "henry.brown@university.ac.uk",
        "title": "Scholarship application status",
        "description": "I submitted my scholarship application two weeks ago and haven't heard back. Can you check the status?",
        "priority": "Low"
    },
    {
        "name": "Iris Patel",
        "email": "iris.patel@university.ac.uk",
        "title": "Library database access problem",
        "description": "I cannot access the IEEE database from off-campus. The VPN is not working properly.",
        "priority": "High"
    },
    {
        "name": "Jack Thompson",
        "email": "jack.thompson@university.ac.uk",
        "title": "Leaking pipe in dormitory",
        "description": "There is water leaking from the ceiling in room 312 of the dormitory. It has been dripping for hours.",
        "priority": "Urgent"
    },
    {
        "name": "Kate Martinez",
        "email": "kate.martinez@university.ac.uk",
        "title": "Timetable clash between courses",
        "description": "My timetable shows two courses at the same time on Tuesday afternoon. I need to resolve this.",
        "priority": "Medium"
    },
    {
        "name": "Liam O'Brien",
        "email": "liam.obrien@university.ac.uk",
        "title": "Cannot install software on lab computer",
        "description": "I need to install MATLAB for my assignment but the lab computers do not allow software installation.",
        "priority": "Medium"
    },
    {
        "name": "Mia Johnson",
        "email": "mia.johnson@university.ac.uk",
        "title": "Request for transcript",
        "description": "I need an official transcript for my job application. How do I request one?",
        "priority": "Low"
    },
    {
        "name": "Noah Davis",
        "email": "noah.davis@university.ac.uk",
        "title": "Student loan payment delayed",
        "description": "My student loan payment was supposed to arrive last week but I haven't received it yet.",
        "priority": "High"
    },
    {
        "name": "Olivia White",
        "email": "olivia.white@university.ac.uk",
        "title": "Book loan extension request",
        "description": "Can I extend my book loan for 'Introduction to Machine Learning' for another two weeks?",
        "priority": "Low"
    },
    {
        "name": "Peter Garcia",
        "email": "peter.garcia@university.ac.uk",
        "title": "Network printer jam",
        "description": "The printer on the second floor is jammed and displaying an error message. Multiple students need to print.",
        "priority": "Medium"
    },
    {
        "name": "Quinn Roberts",
        "email": "quinn.roberts@university.ac.uk",
        "title": "Fee refund request",
        "description": "I dropped a course and am entitled to a partial refund. When will it be processed?",
        "priority": "Medium"
    },
    {
        "name": "Rachel Evans",
        "email": "rachel.evans@university.ac.uk",
        "title": "Exam schedule inquiry",
        "description": "When will the final exam schedule be published? I need to book my flight home.",
        "priority": "Low"
    }
]


def seed_tickets(base_url):
    print(f"Seeding tickets to {base_url}/tickets...")
    success = 0
    failed = 0

    for i, ticket in enumerate(SAMPLE_TICKETS, 1):
        try:
            data = json.dumps(ticket).encode("utf-8")
            req = urllib.request.Request(
                f"{base_url}/tickets",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                if resp.status == 201:
                    result = json.loads(resp.read())
                    category = result.get("category", "unknown")
                    print(f"  [{i:2d}] OK  {ticket['title'][:40]:<40} -> {category}")
                    success += 1
                else:
                    print(f"  [{i:2d}] FAIL {ticket['title'][:40]} (status {resp.status})")
                    failed += 1
        except Exception as e:
            print(f"  [{i:2d}] ERROR {ticket['title'][:40]}: {e}")
            failed += 1

    print(f"\nDone: {success} created, {failed} failed")
    return success


def check_health(base_url):
    print(f"Checking health at {base_url}/health...")
    try:
        req = urllib.request.Request(f"{base_url}/health")
        with urllib.request.urlopen(req) as resp:
            health = json.loads(resp.read())
            print(f"  Status: {health.get('status')}")
            print(f"  Storage: {health.get('storage')}")
            print(f"  Classifier: {health.get('classifier')}")
            return health
    except Exception as e:
        print(f"  Error: {e}")
        return None


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7071/api"
    check_health(base)
    print()
    seed_tickets(base)
