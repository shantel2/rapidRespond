from google.cloud import speech
from twilio.rest import Client
from google.oauth2 import service_account
import requests
import speech_recognition as sr
import spacy, openai
import speech_recognition as sr
#from emergency_classifer_load import makePrediction
#from locationDetect import identifyAddress
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather

from API.LocationToGeo import get_location_by_address as GetGeo
from API.ClosestResponder import find_closest_person as CloseResponder
from API.WhisperTranscription import transcribe_audio
from Models.emergencyDetect import EmergencyPrediction
from Models.locationDetect import identifyAddress




# Initialize the Twilio client
account_sid = "Twilio Account SID Here"
auth_token = "<Twilio Authentication Token Here>"
client = Client(account_sid, auth_token)



app = Flask(__name__)

#Global Variables used for various function communication
GlobalLocation = []
GlobalEmergency = ""
GlobalEmerFirstRun = 0
GlobalLocaFirstRun = 0
TranscriptionLog = [] #Holds log for transcript communication between Client and System.


#First function that connect the system with Twilio, calls are routed here.
@app.route('/twilio/webhook', methods=['POST'])
def twilio_webhook():
    global GlobalLocation, GlobalEmerFirstRun, GlobalLocaFirstRun, TranscriptionLog
    GlobalLocation = []
    GlobalEmerFirstRun = 0
    GlobalLocaFirstRun = 0
    TranscriptionLog = []
    response = VoiceResponse()
    
    #Welcome Message and Client Voice Recording Block /START/
    response.say('Welcome to Rapid Respond. Your Emergency Partner')
    TranscriptionLog.append('<>System: Welcome to Rapid Respond. Your Emergency Partner')
    response.say('Please state your emergency and location then hold the line for a few seconds.')
    TranscriptionLog.append('<>System: Please state your emergency and location then hold the line for a few seconds.')
    response.record(transcribe=True, maxLength='30', action='/transcription')
    #Welcome Message and Client Voice Recording Block /END/
    return str(response)

#Function twilio_transcription handles the transcription flow.
@app.route('/transcription', methods=['POST'])
def twilio_transcription():
    global GlobalLocation, GlobalEmerFirstRun, GlobalLocaFirstRun, GlobalEmergency, TranscriptionLog
    response = VoiceResponse()
    recording_url = request.form['RecordingUrl']
    
    transcription = transcribe_audio(recording_url)
    TranscriptionLog.append(f'[]User: {transcription}')
    # Check if it is the first run for both global emergency and global location
    if GlobalEmerFirstRun == 0 and GlobalLocaFirstRun == 0:
        # Perform emergency prediction based on the transcription
        emergency_T = EmergencyPrediction(transcription)
        GlobalEmergency = emergency_T
        print(">>Emergency Type: ", emergency_T)
        
        # Identify the location(s) from the transcription
        GlobalLocation = identifyAddress(transcription)
        print(">>Detected Location(s): ", GlobalLocation)
        
        # Create a gather object to prompt for confirmation
        gather = Gather(num_digits=1, action="/handle_gather", method="POST")
        gather.say(f"Your emergency type is {emergency_T}. Press 1 to confirm or 2 to re-enter your information.")
        
        # Log the transcription information
        TranscriptionLog.append(f'<>System: Your emergency type is {emergency_T}. Press 1 to confirm or 2 to re-enter your information.')
        
        # Add the gather object to the response
        response.append(gather)
        
        # Set the flag to indicate the first run has occurred for the global emergency
        GlobalEmerFirstRun = 1

        # Check if it is the first run for the global emergency and the second run for the global location
    elif GlobalEmerFirstRun == 1 and GlobalLocaFirstRun == 0:
        # Perform emergency prediction based on the transcription
        emergency_T = EmergencyPrediction(transcription)
        print(">>Emergency Type: ", emergency_T)
        GlobalEmergency = emergency_T
        
        # Create a gather object to prompt for confirmation
        gather = Gather(num_digits=1, action="/handle_gather", method="POST")
        gather.say(f"Your emergency type is {emergency_T}. Press 1 to confirm else hang up and call back.")
        
        # Log the transcription information
        TranscriptionLog.append(f'<>System: Your emergency type is {emergency_T}. Press 1 to confirm else hang up and call back.')
        
        # Add the gather object to the response
        response.append(gather)
        
        # Set the flag to indicate the second run for the global emergency has occurred
        GlobalEmerFirstRun = 2

    # Check if it is the second run for the global emergency and the first run for the global location
    elif GlobalEmerFirstRun > 1 and GlobalLocaFirstRun == 1:
        # Identify the location(s) from the transcription
        GlobalLocation = identifyAddress(transcription)
        print(">>Detected Location(s): ", GlobalLocation)
        
        # Check if a single location is detected and it is not None
        if len(GlobalLocation) == 1 and GlobalLocation[0] != None:
            # Create a gather object to prompt for confirmation
            gather = Gather(num_digits=1, action="/handle_location_confirmation", method="POST")
            gather.say(f"Emergency location is {GlobalLocation}. Press 1 to confirm else hang up and call back.")
            
            # Log the location information
            TranscriptionLog.append(f'<>System: Emergency location is {GlobalLocation}. Press 1 to confirm else hang up and call back.')
            
            # Add the gather object to the response
            response.append(gather)
            
            # Set the flag to indicate the second run for the global location has occurred
            GlobalLocaFirstRun = 2
        else:
            # Hang up the response as no valid location is detected
            response.hangup()

        


    return str(response)

# Define a handler for the gather response
@app.route("/handle_gather", methods=['GET', 'POST'])
def handle_gather():
    global GlobalLocation, GlobalEmerFirstRun, GlobalLocaFirstRun, TranscriptionLog
    response = VoiceResponse()
    # Get the user's response
    #location_Predict = request.args.get('location')
    #print(location_Predict)
    user_response = request.form["Digits"]
    if user_response == "1":
        GlobalEmerFirstRun = 2
        TranscriptionLog.append('|User Press 1 Key|')
        # User confirmed their location and emergency type
        response.say("Thank you for confirming your emergency type.")
        TranscriptionLog.append('<>System: Thank you for confirming your emergency type.')

        #Location is structurally valid and can move on
        if len(GlobalLocation) == 1 and GlobalLocation[0] != None:
            gather = Gather(num_digits=1, action="/handle_location_confirmation", method="POST")
            gather.say(f"Emergency location has been detected as {GlobalLocation[0]}. Press 1 to confirm or 2 to re-enter your information.")
            TranscriptionLog.append(f'<>System: Emergency location has been detected as {GlobalLocation[0]}. Press 1 to confirm or 2 to re-enter your information.')
            response.append(gather)
        #Multiple locations detected, confirm one.
        elif len(GlobalLocation) > 1:
            response.say("Multiple locations detected. Please state the direct emergency location.")
            TranscriptionLog.append('<>System: Multiple locations detected. Please state the direct emergency location.')
            response.record(transcribe=True, maxLength='30', action='/transcription')
            GlobalLocaFirstRun = 1
        #No location returned
        elif GlobalLocation[0] == None:
            GlobalEmergency = "Not stated clearly."
            response.say("No location detected. Please state the direct emergency location.")
            TranscriptionLog.append('<>System: No location detected. Please state the direct emergency location.')
            response.record(transcribe=True, maxLength='30', action='/transcription')
            GlobalLocaFirstRun = 1

    elif user_response == "2" and GlobalEmerFirstRun != 2:
        # User wants to re-enter their information
        TranscriptionLog.append('|User Press 2 Key|')
        response.say("Please state your emergency again")
        TranscriptionLog.append('<>System: Please state your emergency again')
        response.record(transcribe=True, maxLength='30', action='/transcription')
        GlobalEmerFirstRun = 1

    elif user_response != "2" and user_response != "1" and GlobalEmerFirstRun !=2:
        # User made an invalid input but has chances left to correct it
        TranscriptionLog.append(f'|User Press {user_response} Key|')
        gather = Gather(num_digits=1, action="/handle_gather", method="POST")
        gather.say("Invalid Selection, Try again. Press 1 to confirm or 2 to re-enter your information.")
        TranscriptionLog.append("Invalid Selection, Try again. Press 1 to confirm or 2 to re-enter your information.")
        response.append(gather)
        GlobalEmerFirstRun = 1
    else:
        # User made an invalid input but has not chance left to correct it
        response.say("Sorry, I didn't understand your response. Please try again.")
        TranscriptionLog.append("<>System: Sorry, I didn't understand your response. Please try again.")
        response.hangup()
        GlobalEmerFirstRun = 0

    return str(response)

# Define a handler for the location confirmation gather response
@app.route("/handle_location_confirmation", methods=["POST"])
def handle_location_confirmation():
    global GlobalLocation, GlobalLocaFirstRun, TranscriptionLog
    response = VoiceResponse()
    user_response = request.form["Digits"]
    responders = {
        "Medical": [(18.016588, -76.784518),  # Kingston
        (18.468846, -77.895684),  # Montego Bay
        (18.405063, -77.085725),  # Ocho Rios
        (17.9853, -76.8764),  # Portmore
        (18.010689, -76.797437),  # Half Way Tree
        (18.490139, -77.660010),  # Falmouth
        (18.272352, -78.345982),  # Negril
        (17.992597, -76.948397),  # Spanish Town
        ],
    "Fire": [(18.016588, -76.784518),  # Kingston
        (18.468846, -77.895684),  # Montego Bay
        (18.405063, -77.085725),  # Ocho Rios
        (17.9853, -76.8764),  # Portmore
        (18.010689, -76.797437),  # Half Way Tree
        (18.490139, -77.660010),  # Falmouth
        (18.272352, -78.345982),  # Negril
        (17.992597, -76.948397),  # Spanish Town
        ],
    "Police": [(18.016588, -76.784518),  # Kingston
        (18.468846, -77.895684),  # Montego Bay
        (18.405063, -77.085725),  # Ocho Rios
        (17.9853, -76.8764),  # Portmore
        (18.010689, -76.797437),  # Half Way Tree
        (18.490139, -77.660010),  # Falmouth
        (18.272352, -78.345982),  # Negril
        (17.992597, -76.948397),  # Spanish Town
        ]
}
    if user_response == "1":
        TranscriptionLog.append('|User Press 1 Key|')
        # User confirmed their location and emergency type
        GeoLocation = GetGeo(GlobalLocation[0])
        print(">>User's GeoLocation is: ",GeoLocation)
        if GeoLocation == "None":
            response.say("Thank you for confirming your location. Unfortunately we cannot get your Geo-Coordinates. Please try calling again.")
            TranscriptionLog.append("<>System: Thank you for confirming your location. Unfortunately we cannot get your Geo-Coordinates. Please try calling again.")
                
        else:
            ClosestResponder = CloseResponder(GeoLocation[0], GeoLocation[1], responders[GlobalEmergency])
            print(">>Closest Responder is at: ",ClosestResponder)
            if ClosestResponder == None:
                response.say("Thank you for confirming your location. Unfortunately cannot find closest responder. Please try calling again.")
                TranscriptionLog.append("<>System: Thank you for confirming your location. Unfortunately we cannot get your Geo-Coordinates. Please try calling again.")
                
            else:
                response.say("Thank you for confirming your location. Hold tight, help is on the way!")
                TranscriptionLog.append("<>System: Thank you for confirming your location. Hold tight, help is on the way!")

                

        
        print("\n")
        print(">>Transcript Log Begin")
        for x in TranscriptionLog:
            print(x)
        print(">>Transcript Log End")
        response.hangup()


        
    elif user_response == "2" and GlobalLocaFirstRun != 2:
        # User wants to re-enter their information
        TranscriptionLog.append('|User Press 2 Key|')
        response.say("Please state your direct location again.")
        TranscriptionLog.append("<>System: Please state your direct location again.")
        response.record(transcribe=True, maxLength='30', action='/transcription')
        GlobalLocaFirstRun = 1
    
    elif user_response != "2" and user_response != "1" and GlobalLocaFirstRun !=2:
        # User made an invalid input but has chances left to correct it
        TranscriptionLog.append(f'|User Press {user_response} Key|')
        gather = Gather(num_digits=1, action="/handle_location_confirmation", method="POST")
        gather.say("Invalid Selection, Try again. Press 1 to confirm or 2 to re-enter your information.")
        TranscriptionLog.append("Invalid Selection, Try again. Press 1 to confirm or 2 to re-enter your information.")
        response.append(gather)
        GlobalLocaFirstRun = 1

    else:
        # User made an invalid input but has no chance left to correct it
        response.say("Sorry, I didn't understand your response. Please try again.")
        TranscriptionLog.append("<>System: Sorry, I didn't understand your response. Please try again.")
        response.hangup()
        GlobalLocaFirstRun = 0

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
