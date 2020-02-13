import pickle
import config
import os


class PersonalLoanPredictionModel(object):
    MODEL_FILE_NAME = os.path.join(config.basedir, 'machine_learning', 'personal_loan_model.pkl')
    SCALER_FILE_NAME = os.path.join(config.basedir, 'machine_learning', 'personal_loan_scaler.pkl')

    def __init__(self):
        self.model = self._load_model()
        self.scaler = self._load_scaler()

    def _load_model(self):
        model_pkl = open(self.MODEL_FILE_NAME, 'rb')
        model = pickle.load(model_pkl)
        print("Loaded Random Forest Classifier model :: ", model)

        return model

    def _load_scaler(self):
        scaler_pkl = open(self.SCALER_FILE_NAME, 'rb')
        scaler = pickle.load(scaler_pkl)
        print("Loaded model scaler :: ", scaler)

        return scaler

    def predict_customer_responses(self, data_frame):
        # Scale data
        customers_scaled = self.scaler.transform(data_frame)

        # Predict
        predictions = self.model.predict(customers_scaled)
        prediction_probabilities = self.model.predict_proba(customers_scaled)

        # Form the response
        prediction_probability_list = []
        for i in range(len(predictions)):
            probability = prediction_probabilities[i][predictions[i]]
            prediction_probability_list.append(probability)

        data_frame['Prediction'] = predictions
        data_frame['PredictionProbability'] = prediction_probability_list

        # Return response
        return data_frame
