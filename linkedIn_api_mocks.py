def search_candidates(keywords):
    # TODO: connect to real LinkedIn API
    return [
        {"id": "123", "name": "Alice Johnson", "title": "Software Engineer"},
        {"id": "456", "name": "Bob Lee", "title": "Data Scientist"},
    ]

def send_message(candidate_id, message):
    print(f"Sending message to {candidate_id}: {message}")
    return True
