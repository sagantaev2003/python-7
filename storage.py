import json

def load_encyclopedia():
    try:
        with open("encyclopedia.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_encyclopedia(entry):
    data = load_encyclopedia()
    data.append(entry)
    with open("encyclopedia.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def remove_encyclopedia(name):
    data = load_encyclopedia()
    data = [c for c in data if c["name"] != name]
    with open("encyclopedia.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_history():
    try:
        with open("history.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    except:
        return []

def save_history(history):
    with open("history.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(history))
