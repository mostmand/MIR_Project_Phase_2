import csv
import errno
import os
from Category import Category


class IOUtility:
    @staticmethod
    def check_path(path):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    @staticmethod
    def get_word_by_word(file_path: str) -> (str, str, int, Category):
        document_number = 0

        position = 0

        for doc_class, title, description in IOUtility.get_doc_by_doc(file_path):
            words = title.split(' ') + description.split(' ')

            for word in words:
                yield (word, document_number, position, doc_class)
                position += len(word) + 1
            position = 0
            document_number += 1

    @staticmethod
    def get_doc_by_doc(file_path: str) -> (Category, str, str):
        with open(file_path, newline='\n') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

            for row in csv_reader:
                yield Category(int(row[0])), row[1], row[2]
