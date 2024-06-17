import requests

def fetch_all_results(api_url, limit):
    offset = 0
    all_results = []

    while True:
        params = {
            "offset": offset,
            "limit": limit
        }

        response = requests.get(url=api_url, params=params).json()

        if "results" not in response:
            break

        all_results.extend(response["results"])

        if len(response["results"]) < limit:
            break

        offset += limit

    return all_results
