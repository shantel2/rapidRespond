import joblib
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

categories = ['Fire','Police','Medical']

def EmergencyPrediction(text):
  #Load in models
  clf1 = joblib.load('Models/EmergencyModel/nb_model.joblib')
  vectorizer1 = joblib.load('Models/EmergencyModel/vectorizer.joblib')
  clf2 = joblib.load('Models/EmergencyModel/svm_model.joblib')
  vectorizer2 = joblib.load("Models/EmergencyModel/vectorizer2.joblib")
  clf3 = joblib.load('Models/EmergencyModel/gradient_boosting_model.joblib')
  vectorizer3 = joblib.load('Models/EmergencyModel/vectorizer3.joblib') 
  #Make Prediction - Naive Bayes
  
  input_vector = vectorizer1.transform([text])
  prediction = clf1.predict(input_vector)
  outcome1 = categories[prediction[0]]

  #Make Prediction - SVM
  input_vector = vectorizer2.transform([text])
  prediction = clf2.predict(input_vector)
  outcome2 = categories[prediction[0]]

  #Make Prediction - Gradient Boosting
  input_vector = vectorizer3.transform([text])
  prediction = clf3.predict(input_vector)
  outcome3 = categories[prediction[0]]
  print(outcome1, outcome2, outcome3)
  #Concensus Prediction Return
  if outcome1==outcome2==outcome3:
    return outcome1
  if outcome1 != outcome2 and outcome1 != outcome3 and outcome2 != outcome3:
    return outcome3
  if outcome1 == outcome2:
    return outcome1
  if outcome1 == outcome3:
    return outcome1
  else:
    return outcome2


