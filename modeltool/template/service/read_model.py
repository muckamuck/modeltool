import pickle
import joblib
class Model_sklearn(object):
    def predict(self, path, X):
        loaded_model = pickle.load(open(path, 'rb'))
        print('Model Loaded')
        print(loaded_model)
        return loaded_model.predict(X)
