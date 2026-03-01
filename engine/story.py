import yaml

class StoryEngine:
    def __init__(self, file_path):
        with open(file_path) as f:
            documents = list(yaml.safe_load_all(f))

        self.nodes = {}
        for doc in documents:
            if doc and "id" in doc:
                self.nodes[doc["id"]] = doc

    def get_node(self, node_id):
        if node_id not in self.nodes:
            raise ValueError(f"Story node '{node_id}' not found.")
        return self.nodes[node_id]