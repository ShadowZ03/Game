import yaml

def load_abilities(file_path):
    with open(file_path) as f:
        data = yaml.safe_load(f)

    abilities = {}
    for ability in data:
        abilities[ability["id"]] = ability

    return abilities