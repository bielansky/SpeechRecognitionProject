# Python semestral project
# Speech to text -> Translation -> Save to .txt
# Open .txt and add text to it
# Make .mp3 text to speech

import speech_recognition as sr                 #speech recognition
import deepl                                    #translation
from gtts import gTTS                           #text to speech
from playsound import playsound as mp3player    #sound player
import PySimpleGUI as psGUI                     #gui
import os


class SpeechRecognition:
    language_dictionary = {'Bulgarian': 'BG', 'Chinese': 'ZH', 'Czech': 'CS', 'Danish': 'DA', 'Dutch': 'NL', 'English': 'EN',
                           'Estonian': 'ET', 'Finnish': 'FI', 'French': 'FR', 'German': 'DE', 'Greek': 'EL', 'Hungarian': 'HU',
                           'Italian': 'IT', 'Japanese': 'JA', 'Latvian': 'LV', 'Lithuanian': 'LT', 'Polish': 'PL',
                           'Portuguese': 'PT', 'Romanian': 'RO', 'Russian': 'RU', 'Slovak': 'SK', 'Slovenian': 'SL',
                           'Spanish': 'ES', 'Svedish': 'SV'}

    def __init__(self):
        self.currentTranslation = None
        self.openApp()

    def openApp(self):
        pathToTXTFolder = os.path.join(os.path.dirname(__file__), r"Translated txt files\\")
        psGUI.theme("DarkGrey5")
        first_column_layout = [[psGUI.Text('Speech Recognition & Translation', font="Any 20")],
                               [psGUI.Text('Spoken language'), psGUI.Combo(values=list(self.language_dictionary.keys()), key="-SPK_LAN-", default_value="English")],                             # layout okna
                               [psGUI.Text('Translation language'), psGUI.Combo(values=list(self.language_dictionary.keys()), key="-TRANS_LAN-", default_value="English")],
                               [psGUI.Button('Record', key="-REC_BTN-")]]

        second_column_layout = [[psGUI.Listbox(values=os.listdir(pathToTXTFolder), enable_events=True, key="-FILE_LIST-", size=(33, 10), select_mode="single")],
                                [psGUI.Button('Make an MP3 file', key="-MP3_MAKER-"), psGUI.Button("Edit file", key="-EDIT_TXT-"), psGUI.Button("Remove file", key="-RMV_FILE-")]]

        layout = [[psGUI.Column(first_column_layout, element_justification="center"),
                  psGUI.VSeparator(),
                  psGUI.Column(second_column_layout, element_justification="center")]]

        window = psGUI.Window('Speech Recognition', layout, font="Any 15")  # runs the gui

        while True:
            event, values = window.read()  # gets inputs and calls functions
            if event == psGUI.WIN_CLOSED:
                break
            if event == "-REC_BTN-":
                self.record(self.language_dictionary[values["-SPK_LAN-"]], self.language_dictionary[values["-TRANS_LAN-"]])
                window["-FILE_LIST-"].update(values=os.listdir(pathToTXTFolder))
                window.refresh()
            if event == "-MP3_MAKER-" and values["-FILE_LIST-"] is not None:
                self.makeMP3File(values["-FILE_LIST-"][0])
            if event == "-EDIT_TXT-" and values["-FILE_LIST-"] is not None:
                self.editTXTFile(values["-FILE_LIST-"][0])
            if event == "-RMV_FILE-" and values["-FILE_LIST-"] is not None:
                os.remove(os.path.join(pathToTXTFolder, values["-FILE_LIST-"][0]))
                window["-FILE_LIST-"].update(values=os.listdir(pathToTXTFolder))
                window.refresh()


        window.close()

    def record(self, spoken_language, translation_language):
        r = sr.Recognizer()  # speech recognition
        mic = sr.Microphone()  # mic input
        pathToMP3 = os.path.join(os.path.dirname(__file__), "record_sound.mp3")

        with mic as source:
            r.adjust_for_ambient_noise(source, duration=2)
            mp3player(pathToMP3, True)
            audio = r.listen(source, timeout=5, snowboy_configuration=None)
        try:
            received_voice_text = r.recognize_google(audio, language=spoken_language)
        except sr.UnknownValueError as e:
            received_voice_text = None
            psGUI.popup("Google Speech Recognition could not understand audio\nTry again", title="Exception")
        except sr.RequestError as e:
            received_voice_text = None
            psGUI.popup("Could not request results from Google Speech Recognition service\nTry again", title="Exception")
        except sr.WaitTimeoutError as e:
            received_voice_text = None
            psGUI.popup("Listening timed out while waiting for phrase to start\nTry again", title="Exception")

        if received_voice_text is not None:
            if spoken_language == translation_language:
                layout = [[psGUI.Text("You said:\n" + received_voice_text + "\n\nIf output isn't correct try again :(")],
                          [psGUI.Button("Ok", key="-OK-"), psGUI.Button('Make a txt file', key="-MAKE_TXT-")]]
            else:
                self.currentTranslation = deepl.translate(source_language=spoken_language,target_language=translation_language, text=received_voice_text)
                layout = [[psGUI.Text("You said:\n" + received_voice_text + "\n\nTranslation:\n" + self.currentTranslation + "\n\nIf output isn't correct try again :(")],
                          [psGUI.Button("Ok", key="-OK-"), psGUI.Button('Make a txt file', key="-MAKE_TXT-")]]

            window = psGUI.Window("Your recording", layout, font="Any 15")

            while True:
                event, values = window.read()
                if event == psGUI.WIN_CLOSED or event == "-OK-":
                    break
                if event == "-MAKE_TXT-":
                    self.makeTXTFile(spoken_language, translation_language)
                    break

            window.close()

    def makeMP3File(self, txt_file_name):
        pathToMP3 = os.path.join(os.path.dirname(__file__), r"Recorded MP3s\\" + txt_file_name.rstrip(".txt") + ".mp3")
        pathToTXT = os.path.join(os.path.dirname(__file__), r"Translated txt files\\" + txt_file_name)
        file = open(pathToTXT, "r")
        mp3file = gTTS(text=file.read(), lang=(txt_file_name[-6:])[:2].lower(), slow="false")
        file.close()
        mp3file.save(pathToMP3)
        layout = [[psGUI.Text("Successfully created an MP3 file based on: \n" + txt_file_name + "!")],
                  [psGUI.Button("Ok", key="-OK-"), psGUI.Button("Play", key="-PLAY-")]]

        window = psGUI.Window("Done!", layout, font="Any 15")

        while True:
            event, values = window.read()
            if event == psGUI.WIN_CLOSED or event == "-OK-":
                break
            if event == "-PLAY-":
                mp3player(pathToMP3, True)

        window.close()

    def makeTXTFile(self, spoken_language, translated_language):
        pathToFolder = os.path.join(os.path.dirname(__file__), r"Translated txt files\\")
        layout = [[psGUI.Text("Set file name"), psGUI.InputText(key="-FILE_NAME-")],
                  [psGUI.Button("Create", key="-CREATE_FILE-")]]
        window = psGUI.Window("Create txt file", layout)

        while True:
            event, values = window.read()
            if event == psGUI.WIN_CLOSED:
                break
            if event == "-CREATE_FILE-" and values["-FILE_NAME-"] is not None and self.currentTranslation is not None:
                try:
                    with open(pathToFolder + values["-FILE_NAME-"] + " " + spoken_language + "-" + translated_language + ".txt", "x") as f:
                        f.write(self.currentTranslation + ".\n")
                        f.close()
                        psGUI.popup("Successfully created a file!", title="Done!")
                        window.close()
                except FileExistsError:
                    psGUI.popup("File with this name already exists!", title="File exists!")

        window.close()

    def editTXTFile(self, txt_file_name):
        pathToTXTFile = os.path.join(os.path.dirname(__file__), r"Translated txt files\\" + txt_file_name)
        spoken_language = txt_file_name[-9:][:2]
        translation_language = txt_file_name[-6:][:2]

        layout = [[psGUI.Text('Spoken language'), psGUI.Combo(values=list(self.language_dictionary.keys()), default_value=[k for k, v in self.language_dictionary.items() if v == spoken_language][0], disabled= True)],                             # layout okna
                  [psGUI.Text('Translation language'), psGUI.Combo(values=list(self.language_dictionary.keys()), default_value=[k for k, v in self.language_dictionary.items() if v == translation_language][0], disabled= True)],
                  [psGUI.Button('Record', key="-REC_BTN-")]]

        window = psGUI.Window("Edit a file", layout, font="Any 15")

        while True:
            event, values = window.read()
            if event == psGUI.WIN_CLOSED:
                break
            if event == "-REC_BTN-":
                r = sr.Recognizer()
                mic = sr.Microphone()
                pathToMP3 = os.path.join(os.path.dirname(__file__), r"record_sound.mp3")

                with mic as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    mp3player(pathToMP3, True)
                    audio = r.listen(source, timeout=5, snowboy_configuration=None)
                try:
                    received_voice_text = r.recognize_google(audio, language=spoken_language)
                except sr.UnknownValueError as e:
                    received_voice_text = None
                    psGUI.popup("Google Speech Recognition could not understand audio\nTry again", title="Exception")
                except sr.RequestError as e:
                    received_voice_text = None
                    psGUI.popup("Could not request results from Google Speech Recognition service\nTry again",
                                title="Exception")
                except sr.WaitTimeoutError as e:
                    received_voice_text = None
                    psGUI.popup("Listening timed out while waiting for phrase to start\nTry again", title="Exception")

                if received_voice_text is not None:
                    if spoken_language == translation_language:
                        layout = [[psGUI.Text(
                            "You said:\n" + received_voice_text + "\n\nIf output isn't correct try again :(")],
                                  [psGUI.Button("Ok", key="-OK-"), psGUI.Button('Add', key="-ADD-")]]
                    else:
                        self.currentTranslation = deepl.translate(source_language=spoken_language, target_language=translation_language, text=received_voice_text)
                        layout = [[psGUI.Text(
                            "You said:\n" + received_voice_text + "\n\nTranslation:\n" + self.currentTranslation + "\n\nIf output isn't correct try again :(")],
                                  [psGUI.Button("Try again", key="-TRY_AG-"), psGUI.Button('Add', key="-ADD-")]]

                    window_h = psGUI.Window("Your recording", layout, font="Any 15")

                    while True:
                        event, values = window_h.read()
                        if event == psGUI.WIN_CLOSED or event == "-TRY_AG-":
                            break
                        if event == "-ADD-":
                            file = open(pathToTXTFile, "a")
                            file.write(self.currentTranslation + ".\n")
                            file.close()
                            psGUI.popup("Successfully edited a file!", title="Done!")
                            break

                    window_h.close()

        window.close()


runApp = SpeechRecognition()
