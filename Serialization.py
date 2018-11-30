import os
import pickle
from typing import List
from IOUtility import IOUtility
from Index import Index
from VariableByteUtility import VariableByteUtility


class Serialization:
    @staticmethod
    def write_to_file(index_db, filename, compress: bool):
        IOUtility.check_path(filename)
        with open(filename, 'wb') as output:
            for chunk in Serialization.serialize_index(index_db, compress):
                output.write(b''.join(chunk))

    @staticmethod
    def serialize_index(index: Index, compress: bool):
        result: List[bytes] = []
        for key in index.dictionary.keys():
            encoded_word = key.encode('UTF-8')
            result.append(len(encoded_word).to_bytes(4, 'big'))
            result.append(encoded_word)
            posting_list = index.dictionary[key]
            result.append(len(posting_list).to_bytes(4, 'big'))
            for posting in posting_list:
                if compress:
                    result.append(VariableByteUtility.encode(posting.document_id))
                    result.append(VariableByteUtility.encode(posting.position))
                else:
                    result.append(posting.document_id.to_bytes(4, 'big'))
                    result.append(posting.position.to_bytes(4, 'big'))

            if len(result) > 1024 * 1024:
                yield result
                result = []

        if len(result) > 0:
            yield result

    @staticmethod
    def read_from_file(filename: str, compress: bool):
        result = Index()
        if not os.path.exists(os.path.dirname(filename)):
            raise ValueError('The path fo loading the index does not exist.')
        with open(filename, 'rb') as inp:
            while True:
                byte = inp.read(4)
                if byte == b'':
                    break
                word_length = int.from_bytes(byte, 'big')
                if word_length == 0:
                    break
                byte = inp.read(word_length)
                if byte == b'':
                    raise ValueError('Malformed index file.')
                word = byte.decode('UTF-8')
                byte = inp.read(4)
                if byte == b'':
                    raise ValueError('Malformed index file.')
                posting_list_length = int.from_bytes(byte, 'big')
                for i in range(posting_list_length):
                    document_id: int
                    position: int
                    if compress:
                        document_id_array = []
                        while True:
                            byte = inp.read(1)
                            if byte == b'':
                                raise ValueError('Malformed index file.')
                            document_id_array.append(byte)
                            if byte >= b'\x80':
                                break
                        document_id = VariableByteUtility.decode(b''.join(document_id_array))
                        position_array = []
                        while True:
                            byte = inp.read(1)
                            if byte == b'':
                                raise ValueError('Malformed index file.')
                            position_array.append(byte)
                            if byte >= b'\x80':
                                break
                        position = VariableByteUtility.decode(b''.join(position_array))
                    else:
                        byte = inp.read(4)
                        if byte == b'':
                            raise ValueError('Malformed index file.')
                        document_id = int.from_bytes(byte, 'big')
                        byte = inp.read(4)
                        if byte == b'':
                            raise ValueError('Malformed index file.')
                        position = int.from_bytes(byte, 'big')
                    result.index(word, document_id, position)
            return result

    @staticmethod
    def write_ids(id_manager, filename):
        IOUtility.check_path(filename)
        with open(filename, 'wb') as output:
            pickle.dump(id_manager, output)

    @staticmethod
    def load_ids(filename):
        if not os.path.exists(os.path.dirname(filename)):
            raise ValueError('The path fo loading the index does not exist.')
        with open(filename, 'rb') as inp:
            return pickle.load(inp)
