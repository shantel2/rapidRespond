import spacy

#Load in the custom trained spaCy model
nlp=spacy.load("Models/LocationModel/model-best")

#Finds and returns the detected address aspect for the functions input
def identifyAddress(address):
    # Process the address using a natural language processing model
    doc = nlp(address)
    
    # Extract the entities (text and label) from the processed document
    ent_list = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Initialize variables for the output
    output = []
    outputLen = len(ent_list)
    
    # Check the number of identified entities
    if outputLen == 0:
        # Return a list with a single element containing None if no entities are found
        return [None]
    elif outputLen == 1:
        # Return a list with a single element containing the identified entity and 'Jamaica'
        return [ent_list[0][0] + ', Jamaica']
    else:
        # Iterate over the identified entities and append 'Jamaica' to each entity
        for x in ent_list:
            output.append(str(x[0]) + ', Jamaica')
        # Return the list of identified entities with 'Jamaica' appended to each entity
        return output

  
