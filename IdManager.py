from typing import Dict, Optional


class IdManager:
    ids_dic: Dict[str, int]
    id_to_key_dic: Dict[int, str]
    first_available_id: int

    def __init__(self):
        self.ids_dic = {}
        self.first_available_id = 1
        self.id_to_key_dic = {}

    def get_available_id(self) -> int:
        self.first_available_id += 1
        return self.first_available_id - 1

    def get_id(self, key: str) -> int:
        if key not in self.ids_dic:
            self.ids_dic[key] = self.get_available_id()

        id = self.ids_dic[key]
        self.id_to_key_dic[id] = key

        return id

    def get_key(self, id: int) -> Optional[str]:
        if id in self.id_to_key_dic:
            return self.id_to_key_dic[id]
        return None
