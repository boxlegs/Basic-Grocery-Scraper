import requests

def publish_notification(url, content, title, priority, tags, markdown=False):
    """
    Publishes a notification to the ntfy server specified by url.  
    """
    req = requests.post(url,
    data=content,
    headers={
        "Title": title,
        "Priority": priority,
        "Tags": tags,
        "Markdown": "yes" if markdown else "no" # Not yet implemented in ntfy
    })
    
    if req.status_code != 200:
        raise Exception(f"Failed to send notification: {req.status_code} - {req.text}")