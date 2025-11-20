import requests
import random

API_BASE = "https://rickandmortyapi.com/api"

def get_character(name, max_results=30):
    characters = []
    url = f"{API_BASE}/character"
    params = {"name": name}

    while url and len(characters) < max_results:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            break
        data = response.json()
        for char in data.get("results", []):
            characters.append({
                "name": char["name"],
                "status": char["status"],
                "species": char["species"],
                "location": char["location"]["name"],
                "episodes_count": len(char["episode"]),
                "image": char["image"]
            })
            if len(characters) >= max_results:
                break

        # Для следующей страницы
        url = data.get("info", {}).get("next")
        params = None  # Параметры нужны только для первой страницы

    return characters


def get_random_character():
    rid = random.randint(1, 826)
    response = requests.get(f"{API_BASE}/character/{rid}")
    if response.status_code == 200:
        char = response.json()
        return {
            "name": char["name"],
            "status": char["status"],
            "species": char["species"],
            "location": char["location"]["name"],
            "episodes_count": len(char["episode"]),
            "image": char["image"]
        }
    return None

def get_episode(number):
    response = requests.get(f"{API_BASE}/episode/{number}")
    if response.status_code == 200:
        ep = response.json()
        characters = []
        for c in ep["characters"][:5]:
            cdata = requests.get(c).json()
            characters.append(cdata["name"])
        return {
            "name": ep["name"],
            "air_date": ep["air_date"],
            "episode": ep["episode"],
            "characters": characters
        }
    return None

def get_location(name):
    params = {"name": name}
    response = requests.get(f"{API_BASE}/location", params=params)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and data["results"]:
            loc = data["results"][0]
            return {
                "name": loc["name"],
                "type": loc["type"],
                "dimension": loc["dimension"],
                "residents_count": len(loc["residents"])
            }
    return None

def get_all_episodes():
    episodes = []
    url = f"{API_BASE}/episode"
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for ep in data["results"]:
                episodes.append({
                    "id": ep["id"],
                    "name": ep["name"],
                    "code": ep["episode"],
                    "air_date": ep["air_date"]
                })
            url = data["info"]["next"]
        else:
            break
    return episodes
