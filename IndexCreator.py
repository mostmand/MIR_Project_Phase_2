from PositionalIndexer import PositionalIndexer

train_samples_path = 'ag_news_csv/train2.csv'
test_samples_path = 'ag_news_csv/test2.csv'


def index_train_documents():
    positional_indexer = PositionalIndexer()
    print('Indexing...')
    positional_indexer.index(train_samples_path)
    print('done!!!')

    return positional_indexer


# positional_indexer = index_train_documents()
# positional_indexer.create_documents_vectors()
# positional_indexer.save()
