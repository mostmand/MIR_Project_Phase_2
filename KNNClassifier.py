import math
from IOUtility import IOUtility
from PositionalIndexer import PositionalIndexer
from PreProcess import PreProcessor

k = int(input('Please input k:\n'))
positional_indexer = PositionalIndexer()
positional_indexer.load()
pre_processor = PreProcessor()
test_samples_path = 'ag_news_csv/test2.csv'


def tokenize(text):
    for word in text.split(' '):
        for token in pre_processor.pre_process_english(word):
            yield token


def create_text_vector(text: str):
    tf_vector = {}
    for token in tokenize(text):
        if token not in tf_vector:
            tf_vector[token] = 0
        tf_vector[token] += 1

    idf_vector = {}
    for term in tf_vector:
        idf = positional_indexer.calculate_idf(term)
        if idf is not None:
            idf_vector[term] = tf_vector[term] * idf

    return idf_vector


def calculate_distance(doc_vector, text_vector):
    squared_distance = 0
    for term, tf_idf in doc_vector.items():
        if term in text_vector:
            squared_distance += math.pow(tf_idf - text_vector[term], 2)
        else:
            squared_distance += math.pow(tf_idf, 2)

    for term, tf_idf in text_vector.items():
        if term not in doc_vector:
            squared_distance += math.pow(tf_idf, 2)

    return math.sqrt(squared_distance)


def classify(text: str, k: int):
    text_vector = create_text_vector(text)
    distances_by_doc_id = {}
    for doc_id, doc_vector in positional_indexer.vectors_by_doc_id.items():
        distances_by_doc_id[doc_id] = calculate_distance(doc_vector, text_vector)

    doc_id_distance_tuples = sorted(distances_by_doc_id.items(), key=lambda kv: kv[1])
    k_nearest_neighbors = []
    for i in range(k):
        k_nearest_neighbors.append(doc_id_distance_tuples[i][0])

    labels_count = {}
    for neighbor in k_nearest_neighbors:
        label = positional_indexer.category_by_doc_id[neighbor]
        if label not in labels_count:
            labels_count[label] = 0
        labels_count[label] += 1

    maximum_label, maximum_count = next(iter(labels_count.items()))
    for label, label_count in labels_count.items():
        if label_count > maximum_count:
            maximum_label = label
            maximum_count = label_count

    return maximum_label


def classify_documents(file_path: str, k: int):
    false_positives = 0
    true_positives = 0
    for category, title, description in IOUtility.get_doc_by_doc(file_path):
        calculated_category = classify(title + ' ' + description, k)
        if calculated_category == category:
            true_positives += 1
        else:
            false_positives += 1

    print(true_positives / (true_positives + false_positives))


classify_documents(test_samples_path, k)
