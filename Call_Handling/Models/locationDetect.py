import spacy

nlp=spacy.load("Models/LocationModel/model-best")

#Function processes an address using a spaCy NLP model and returns any address entities found
def identifyAddress(address):
  doc=nlp(address)
  ent_list=[(ent.text, ent.label_) for ent in doc.ents]
  output = []
  outputLen = len(ent_list)
  if outputLen == 0:
    return [None]
  elif outputLen == 1:
    return [ent_list[0][0]+', Jamaica']
  else:
    for x in ent_list:
      output.append(str(x[0])+', Jamaica')
    return output

