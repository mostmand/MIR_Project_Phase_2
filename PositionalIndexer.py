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

    def index(self, file_name, is_persian: bool):
        for (word, document_number, position, doc_class) in IOUtility.get_word_by_word(file_name):
            tokens = self.preprocessor.pre_process(word, is_persian)
            document_name = file_name + '_' + str(document_number)
            doc_id = self.id_manager.get_document_id(document_name)
            for token in tokens:
                self.index_db.index(token, doc_id, position, doc_class)

    def process_given_text(self, text, is_persian: bool):
        result = []
        for word in text.split(' '):
            result.extend(self.preprocessor.pre_process(word, is_persian))
        return result

    def save(self):
        ids_filename = 'Index/ids.mir'
        Serialization.save(self.id_manager, ids_filename)
        index_filename = 'Index/index.mir'
        Serialization.save(self.index_db, index_filename)

    def load(self):
        ids_filename = 'Index/ids.mir'
        self.id_manager = Serialization.load(ids_filename)
        index_filename = 'Index/index.mir'
        self.index_db = Serialization.load(index_filename)

    def search(self, query: str, is_persian: bool):
        vectors_dictionary: Dict[int, List[float]] = {}  # Dictionary from docId to vector
        idf_vector: List[float] = []
        query_terms: List[str] = []
        for token in list(set(query.split(' '))):
            distinct_terms = list(set(self.preprocessor.pre_process(token, is_persian)))
            query_terms.extend(distinct_terms)

        query_terms = list(set(query_terms))
        for j in range(len(query_terms)):
            term = query_terms[j]
            posting_list = self.index_db.find(term)
            document_frequency = len(posting_list)
            idf = self.calculate_idf(document_frequency)
            idf_vector.append(idf)
            for i in range(document_frequency):
                document_id = posting_list[i].document_id
                term_frequency = 0
                while posting_list[i].document_id == document_id:
                    term_frequency += 1
                    i += 1
                    if i >= len(posting_list):
                        break
                i -= 1
                if document_id not in vectors_dictionary:
                    vectors_dictionary[document_id] = [0] * len(query_terms)

                tf = calculate_tf(term_frequency)
                vectors_dictionary[document_id][j] = (tf * idf)

        term_frequencies = self.calculate_query_term_frequency(query_terms, query, is_persian)
        query_vector: List[float] = []
        for i in range(len(query_terms)):
            query_term = query_terms[i]
            idf = idf_vector[i]
            tf = calculate_tf(term_frequencies[query_term])
            query_vector.append(tf * idf)

        scores = []
        for document_id in vectors_dictionary.keys():
            scores.append((document_id, calculate_similarity(vectors_dictionary[document_id], query_vector)))

        scores.sort(key=lambda x: x[1], reverse=True)

        selected_scores = scores[0:19]

        result = []
        for i in range(len(selected_scores)):
            document = ''.join(open(self.id_manager.get_file_path(selected_scores[i][0])).readlines())
            result.append((document, selected_scores[i][1]))
        return result

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

    def calculate_idf(self, document_frequency):
        return math.log(len(self.id_manager.ids_dic) / document_frequency)

    def get_100_highest_frequency_terms(self):
        result = []
        for word in self.index_db.dictionary.keys():
            result.append((word, len(self.index_db.dictionary[word])))
        result.sort(key=lambda x: x[1], reverse=True)

        return result[0:99]

    def get_posting_list(self, word, is_persian):
        result = []
        tokens = self.process_given_text(word, is_persian)
        for token in tokens:
            posting_list = []
            if token in self.index_db.dictionary:
                posting_list = self.index_db.dictionary[token]
            result.append((token, posting_list))
        return result
