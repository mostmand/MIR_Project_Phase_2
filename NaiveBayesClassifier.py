import math
from typing import Dict, List, Set
from Category import Category
from IOUtility import IOUtility
import IndexCreator
from PositionalIndexer import PositionalIndexer
from PreProcess import PreProcessor

preprocessor = PreProcessor()
index = PositionalIndexer()
index.load()


def calculate_term_category_dic():
    term_category_dic = {}
    for term in index.index_db.dictionary:
        category_dic = index.index_db.dictionary[term]
        if term not in term_category_dic:
            term_category_dic[term] = {}
        for category in category_dic:
            indices = category_dic[category]
            if category not in term_category_dic[term]:
                term_category_dic[term][category] = len(indices)
    return term_category_dic


def calculate_vocabulary_length(term_category_dic):
    return len(term_category_dic)


def calculate_category_term_sums(term_category_dic):
    category_term_sums = {}
    for term in term_category_dic:
        category_dic = term_category_dic[term]
        for category in category_dic:
            number_of_terms = category_dic[category]
            if category not in category_term_sums:
                category_term_sums[category] = 0
            category_term_sums[category] += number_of_terms
    return category_term_sums


def calculate_p_hat_by_category():
    p_hat_by_category = {}
    docs_by_category: Dict[Category, Set[int]] = {}

    for term, category_dic in index.index_db.dictionary.items():
        for category, indices in category_dic.items():
            if category not in docs_by_category:
                docs_by_category[category] = set()
            for positional_index in indices:
                docs_by_category[category].add(positional_index.document_id)

    for category, docs in docs_by_category.items():
        if category not in p_hat_by_category:
            p_hat_by_category[category] = 0
        p_hat_by_category[category] += len(docs)

    number_of_all_docs = 0
    for category in p_hat_by_category:
        number_of_all_docs += p_hat_by_category[category]

    for category in p_hat_by_category:
        p_hat_by_category[category] = math.log(p_hat_by_category[category] / number_of_all_docs)

    return p_hat_by_category


def classify_documents(file_path: str):
    term_category_dic = calculate_term_category_dic()
    vocabulary_length = calculate_vocabulary_length(term_category_dic)
    category_term_sums = calculate_category_term_sums(term_category_dic)

    number_of_true_positives = 0
    number_of_false_positives = 0

    p_hat_by_category = calculate_p_hat_by_category()
    for category, title, description in IOUtility.get_doc_by_doc(file_path):
        calculated_category = classify(title + ' ' + description, term_category_dic, vocabulary_length
                                       , category_term_sums, p_hat_by_category)
        if calculated_category == category:
            number_of_true_positives += 1
        else:
            number_of_false_positives += 1

    return number_of_true_positives / (number_of_true_positives + number_of_false_positives)


def classify(document: str, term_category_dic, vocabulary_length, category_term_sums, p_hat_by_category):
    categories_score = {}
    for word in document.split(' '):
        for token in preprocessor.pre_process_english(word):
            if token in term_category_dic:
                category_dic = term_category_dic[token]
                for (category, number_of_terms) in category_dic.items():
                    if category not in categories_score:
                        categories_score[category] = p_hat_by_category[category]
                    categories_score[category] += math.log((number_of_terms + 1)/(category_term_sums[category]
                                                                                  + vocabulary_length))

    maximum_score_category, maximum_score = next(iter(categories_score.items()))
    for category in categories_score:
        score = categories_score[category]
        if score > maximum_score:
            maximum_score_category = category
            maximum_score = score

    return maximum_score_category


print(classify_documents(IndexCreator.test_samples_path))
