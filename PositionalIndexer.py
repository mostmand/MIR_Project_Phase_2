import math
from typing import Dict, List, Optional
from IOUtility import IOUtility
from Index import Index
from PreProcess import PreProcessor
from Serialization import Serialization


def combine_path(parent_directory: str, file_name: str) -> str:
    return parent_directory + '/' + file_name


class IdManager:
    ids_dic: Dict[str, int]
    id_to_file_dic: Dict[int, str]
    first_available_id: int

    def __init__(self):
        self.ids_dic = {}
        self.first_available_id = 1
        self.id_to_file_dic = {}

    def get_available_id(self) -> int:
        self.first_available_id += 1
        return self.first_available_id - 1

    def get_document_id(self, path: str) -> int:
        if path not in self.ids_dic:
            self.ids_dic[path] = self.get_available_id()

        doc_id = self.ids_dic[path]
        self.id_to_file_dic[doc_id] = path

        return doc_id

    def get_file_path(self, doc_id: int) -> Optional[str]:
        if doc_id in self.id_to_file_dic:
            return self.id_to_file_dic[doc_id]
        return None


def calculate_tf(term_frequency):
    return 1 + math.log(term_frequency)


def calculate_vector_magnitude(d1):
    result = 0
    for item in d1:
        result += math.pow(item, 2)
    result = math.sqrt(result)
    return result


def calculate_similarity(d1: List[float], d2: List[float]):
    multiply = multiply_vectors(d1, d2)
    d1_magnitude = calculate_vector_magnitude(d1)
    d2_magnitude = calculate_vector_magnitude(d2)
    return multiply / (d1_magnitude * d2_magnitude)


def multiply_vectors(d1: List[float], d2: List[float]) -> float:
    multiply = 0.0
    for i in range(len(d1)):
        multiply += d1[i] * d2[i]
    return multiply


class PositionalIndexer:
    def __init__(self):
        self.index_db = Index()
        self.preprocessor = PreProcessor()
        self.id_manager = IdManager()
        self.category_by_doc_id = {}
        self.vectors_by_doc_id = {}
        self.idf_by_term = {}

    def index(self, file_name):
        for (word, document_number, position, doc_class) in IOUtility.get_word_by_word(file_name):
            tokens = self.preprocessor.pre_process_english(word)
            document_name = file_name + '_' + str(document_number)
            doc_id = self.id_manager.get_document_id(document_name)
            if doc_id not in self.category_by_doc_id:
                self.category_by_doc_id[doc_id] = doc_class
            for token in tokens:
                self.index_db.index(token, doc_id, position)

    def save(self):
        ids_filename = 'Index/ids.mir'
        Serialization.save(self.id_manager, ids_filename)
        index_filename = 'Index/index.mir'
        Serialization.save(self.index_db, index_filename)
        category_by_doc_id_filename = 'Index/category_by_doc_id.mir'
        Serialization.save(self.category_by_doc_id, category_by_doc_id_filename)
        vectors_by_doc_id_filename = 'Index/vectors_by_doc_id.mir'
        Serialization.save(self.vectors_by_doc_id, vectors_by_doc_id_filename)

    def load(self):
        ids_filename = 'Index/ids.mir'
        self.id_manager = Serialization.load(ids_filename)
        index_filename = 'Index/index.mir'
        self.index_db = Serialization.load(index_filename)
        category_by_doc_id_filename = 'Index/category_by_doc_id.mir'
        self.category_by_doc_id = Serialization.load(category_by_doc_id_filename)
        vectors_by_doc_id_filename = 'Index/vectors_by_doc_id.mir'
        self.vectors_by_doc_id = Serialization.load(vectors_by_doc_id_filename)

    def create_documents_vectors(self):
        for term, indices in self.index_db.dictionary.items():
            for index in indices:
                if index.document_id not in self.vectors_by_doc_id:
                    self.vectors_by_doc_id[index.document_id] = {}
                if term not in self.vectors_by_doc_id[index.document_id]:
                    self.vectors_by_doc_id[index.document_id][term] = 0
                self.vectors_by_doc_id[index.document_id][term] += 1

        for doc_id in self.vectors_by_doc_id:
            for term in self.vectors_by_doc_id[doc_id]:
                self.vectors_by_doc_id[doc_id][term] *= self.calculate_idf(term)

    def calculate_query_term_frequency(self, terms, query, is_persian: bool):
        result: Dict[str, int] = {}
        for w in query.split(' '):
            for t in self.preprocessor.pre_process(w, is_persian):
                for term in terms:
                    if term == t:
                        if term not in result:
                            result[term] = 0
                        result[term] += 1

        return result

    def calculate_idf(self, term):
        if term in self.idf_by_term:
            return self.idf_by_term[term]
        posting_list = self.index_db.find(term)
        doc_ids = [index.document_id for index in posting_list]
        document_frequency = len(set(doc_ids))
        if document_frequency == 0:
            return None
        idf = math.log(len(self.id_manager.ids_dic) / document_frequency)
        self.idf_by_term[term] = idf
        return idf
