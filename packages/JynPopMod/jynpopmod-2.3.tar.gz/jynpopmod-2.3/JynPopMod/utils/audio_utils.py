"""                                               PRIVATE USE AND DERIVATIVE LICENSE AGREEMENT 

        By using this software (the "Software"), you (the "User") agree to the following terms:  

1. Grant of License:  
    The Software is licensed to you for personal and non-commercial purposes, as well as for incorporation into your own projects, whether for private or public release.  

2. Permitted Use:  
    - You may use the Software as part of a larger project and publish your program, provided you include appropriate attribution to the original author (the "Licensor").  
    - You may modify the Software as needed for your project but must clearly indicate any changes made to the original work.  

3. Restrictions:  
     - You may not sell, lease, or sublicense the Software as a standalone product.  
     - If using the Software in a commercial project, prior written permission from the Licensor is required.(Credit,Cr)
     - You may not change or (copy a part of) the original form of the Software.  

4. Attribution Requirement:  
      Any published program or project that includes the Software, in whole or in part, must include the following notice:  
      *"This project includes software developed by [Jynoqtra], © 2025. Used with permission under the Private Use and Derivative License Agreement."*  

5. No Warranty:  
      The Software is provided "as is," without any express or implied warranties. The Licensor is not responsible for any damage or loss resulting from the use of the Software.  

6. Ownership:  
      All intellectual property rights, including but not limited to copyright and trademark rights, in the Software remain with the Licensor.  

7. Termination:  
     This license will terminate immediately if you breach any of the terms and conditions set forth in this agreement.  

8. Governing Law:  
      This agreement shall be governed by the laws of [the applicable jurisdiction, without regard to its conflict of law principles].  

9. Limitation of Liability:  
     In no event shall the Licensor be liable for any direct, indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or use, incurred by you or any third party, whether in an action in contract, tort (including but not limited to negligence), or otherwise, even if the Licensor has been advised of the possibility of such damages.  

            Effective Date: [2025]  

            © 2025 [Jynoqtra]
"""

import pyttsx3
import speech_recognition as sr
import requests
from better_profanity import profanity

def play_audio(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Could not request results; check your network connection."

def check_website_status(url):
    response = requests.get(url)
    return response.status_code == 200

def filter_swears_in_text(text):
    return profanity.censor(text)

def speech_to_text_with_filter():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for speech...")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            cleaned_text = filter_swears_in_text(text)
            print(f"Filtered text: {cleaned_text}")
            return cleaned_text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return ""
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
            return ""

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results"
