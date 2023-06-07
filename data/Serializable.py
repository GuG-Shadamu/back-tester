import pickle


class Serializable:
    @classmethod
    def from_pickle_obj(cls, obj: type):
        """convert from pickle object"""
        return pickle.loads(obj)

    @classmethod
    def from_pickle_file(cls, file_path: str):
        """convert from pickle file"""
        with open(file_path, "rb") as file:
            return pickle.load(file)

    def to_pickle_obj(self) -> bytes:
        """Serialize dataframe into pickle object"""
        return pickle.dumps(self.data)

    def to_pickle_file(self, file_path: str):
        """Serialize dataframe into pickle file"""
        with open(file_path, "wb") as f:
            pickle.dump(self, f)
