from PositionalIndexer import PositionalIndexer

train_samples_path = 'ag_news_csv/train.csv'
test_samples_path = 'ag_news_csv/test.csv'
classes_path = 'ag_news_csv/classes.txt'


def index_test_documents():
    positional_indexer = PositionalIndexer()
    print('Indexing...')
    positional_indexer.index(test_samples_path, False)
    print('done!!!')

    return positional_indexer
