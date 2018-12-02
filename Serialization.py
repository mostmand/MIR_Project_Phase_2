from IOUtility import IOUtility
import pickle


class Serialization:
    @staticmethod
    def save(obj, filename):
        IOUtility.check_path(filename)
        with open(filename, 'wb') as output:
            pickle.dump(obj, output)

    @staticmethod
    def load(filename: str):
        with open(filename, 'rb') as inp:
            obj = pickle.load(inp)
            return obj
