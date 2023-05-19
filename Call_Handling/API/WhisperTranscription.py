import requests
import openai

#Transcribes all requests using WhisperAPI
def transcribe_audio(recording_url):
    # Download the recording from the given URL
    response = requests.get(recording_url)
    i = 0

    #Iteration block checks max 5 times for the availability of
    # Client Voice Recording
    # Voice Recording is downloaded if available 
    while True:
        if i == 5:
            break
        if response.status_code == 200:
            print("status OK")
            recording_content = response.content
            with open('recording.mp3', 'wb') as f:
                f.write(recording_content)
            print("Recording found")
            break
        response = requests.get(recording_url)
        i += 1

 
    model_id = 'whisper-1'
    media_file_path = "recording.mp3"
    media_file = open(media_file_path, 'rb')
    openai.api_key = '<API Key Here>'
    response = openai.Audio.transcribe(
        model = model_id,
        file = media_file,
        prompt = "User is calling in to report an emergency and location of emergency with a Jamaican accent and poor call quality"

    )
    #Removal of certain punctuations from the transcription
    transcription = response['text']
    TempTranscription = transcription
    transcription = ''
    for x in TempTranscription:
        if x!=',' and x!="." and x!="!":
            transcription+=x

    print(">>Transcription: ",TempTranscription)
   

    return transcription