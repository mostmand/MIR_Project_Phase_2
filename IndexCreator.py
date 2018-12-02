from PositionalIndexer import PositionalIndexer

train_samples_path = 'ag_news_csv/train.csv'
test_samples_path = 'ag_news_csv/test.csv'


def index_train_documents():
    positional_indexer = PositionalIndexer()
    print('Indexing...')
    positional_indexer.index(train_samples_path, False)
    print('done!!!')

    return positional_indexer


# positional_indexer = index_train_documents()
# positional_indexer.save()
