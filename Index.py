from typing import List, Dict

import Category


class PositionalIndex:
    def __init__(self, document_id: int, position: int):
        self.document_id = document_id
        self.position = position


class Index:
    def __init__(self):
        self.dictionary = {}

    def index(self, word, document_id, position):
        if word not in self.dictionary:
            self.dictionary[word] = []

        index = PositionalIndex(document_id, position)
        self.dictionary[word].append(index)

    def find(self, word: str) -> List[PositionalIndex]:
        if word in self.dictionary:
            return self.dictionary[word]
        return []
