from IOUtility import IOUtility
from IdManager import IdManager
from PositionalIndexer import PositionalIndexer
from PreProcess import PreProcessor
from sklearn.metrics import classification_report
from sklearn.svm import SVC

from Serialization import Serialization


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


def classify_documents(file_path: str):
    y_test = []
    x_test = []
    for category, title, description in IOUtility.get_doc_by_doc(file_path):
        vector = create_text_vector(title + ' ' + description)
        new_vector = create_new_vector(vector)
        x_test.append(new_vector)
        y_test.append(str(category.value))

    y_predicted = svclassifier.predict(x_test)
    print(classification_report(y_test, y_predicted))


def create_new_vector(vector):
    last_id = terms_id_manager.first_available_id - 1
    new_vector = []
    sorted_vector = sorted(vector.items(), key=lambda kv: terms_id_manager.get_id(kv[0]))

    counter = 1
    for term, tf_idf in sorted_vector:
        term_id = terms_id_manager.get_id(term)
        while counter < term_id:
            new_vector.append(0)
            counter += 1
        new_vector.append(tf_idf)
        counter += 1
    while counter <= last_id:
        new_vector.append(0)
        counter += 1

    return new_vector


def create_new_vectors():
    # new_vectors = []
    # labels = []
    # for doc_id, vector in positional_indexer.vectors_by_doc_id.items():
    #     new_vector = create_new_vector(vector)
    #     labels.append(str(positional_indexer.category_by_doc_id[doc_id].value))
    #     new_vectors.append(new_vector)
    #
    # result = [new_vectors, labels]
    #
    # Serialization.save(result, 'Index/vectors.mir')

    result = Serialization.load('Index/vectors.mir')

    return result[0], result[1]


c = float(input('Please input C:\n'))
positional_indexer = PositionalIndexer()
positional_indexer.load()
terms_id_manager = IdManager()
for term in positional_indexer.index_db.dictionary:
    terms_id_manager.get_id(term)
path = 'ag_news_csv/test2.csv'
pre_processor = PreProcessor()

x_train, y_train = create_new_vectors()
svclassifier = SVC(C=c, kernel='linear')
svclassifier.fit(x_train, y_train)
classify_documents(path)
