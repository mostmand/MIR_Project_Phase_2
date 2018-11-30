import math

from IOUtility import IOUtility
import IndexCreator
from PreProcess import PreProcessor

preprocessor = PreProcessor()


def calculate_term_category_dic():
    index = IndexCreator.index_test_documents()
    term_category_dic = {}
    for (term, category_dic) in index.index_db.dictionary:
        if term not in term_category_dic:
            term_category_dic[term] = {}
        for (category, indices) in category_dic:
            if category not in term_category_dic[term]:
                term_category_dic[term][category] = len(indices)
    return term_category_dic


def calculate_vocabulary_length(term_category_dic):
    return len(term_category_dic)


def calculate_category_term_sums(term_category_dic):
    category_term_sums = {}
    for term, category_dic in term_category_dic:
        for category, number_of_terms in category_dic:
            if category not in category_term_sums:
                category_term_sums[category] = 0
            category_term_sums[category] += number_of_terms
    return category_term_sums


def classify_documents(file_path: str):
    term_category_dic = calculate_term_category_dic()
    vocabulary_length = calculate_vocabulary_length(term_category_dic)
    category_term_sums = calculate_category_term_sums(term_category_dic)

    for category, title, description in IOUtility.get_doc_by_doc(file_path):
        calculated_category = classify(title + ' ' + description, term_category_dic, vocabulary_length, category_term_sums)


def classify(document: str, term_category_dic, vocabulary_length, category_term_sums):
    categories_score = {}
    for word in document.split(' '):
        for token in preprocessor.pre_process_english(word):
            category_dic = term_category_dic[token]
            for (category, number_of_terms) in category_dic:
                if category not in categories_score:
                    categories_score[category] = 0  # we can calculate pHat(c) instead of 0
                categories_score[category] += math.log((number_of_terms + 1)/(category_term_sums[category] + vocabulary_length))

    maximum_score_category = next(iter(categories_score.keys()))
    for category, score in categories_score:
        if score > maximum_score_category:
            maximum_score_category = category

    return maximum_score_category
