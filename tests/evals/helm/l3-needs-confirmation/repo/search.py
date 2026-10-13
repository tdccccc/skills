def search(articles, query, tag=None):
    """Return articles whose title contains query, optionally limited to one tag."""
    hits = [article for article in articles if query.lower() in article["title"].lower()]
    if tag is not None:
        hits = [article for article in hits if tag in article["tags"]]
    return hits
