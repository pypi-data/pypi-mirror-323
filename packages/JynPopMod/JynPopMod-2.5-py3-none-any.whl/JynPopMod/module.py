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

def wait(key="s", num=1):
    import time
    if key == "s" or key == "S":
        time.sleep(num)
    elif key == "m" or key == "M":
        time.sleep(num * 60)
    elif key == "h" or key == "H":
        time.sleep(num * 3600)
    else:
        print("An error occurred. Please use 's' for seconds, 'm' for minutes, or 'h' for hours.")
def ifnull(_v, _d): return _d if _v is None or _v == "" else _v
def switch_case(_v, _c, d=None): return _c.get(_v, d)() if callable(_c.get(_v, d)) else _c.get(_v, d)
def timer_function(func, seconds):import time;time.sleep(seconds);func()
def iftrue(Var, function):
    if Var:function()
def iffalse(Var, function):
    if not Var:function()
def replace(string,replacement,replacment):return string.replace(replacement,replacment)
def until(function,whattodo):
    while True:
        whattodo
        if function():break
def repeat(function, times):
    for _ in range(times):function()
def oncondit(condition, function_true, function_false):
    if condition:function_true()
    else:function_false()
def repeat_forever(function):
    while True:function()
def safe_run(func, *args, **kwargs):
    try:func(*args, **kwargs)
    except Exception as e:print(f"Error occurred in function {func.__name__}: {e}");return None
def start_timer(seconds, callback):import time;time.sleep(seconds);callback()
def generate_random_string(length=15):import random;return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@/-*_', k=length))
def get_ip_address():import socket;return socket.gethostbyname(socket.gethostname())
def send_email(subject, body, to_email, mailname, mailpass):import smtplib;server = smtplib.SMTP('smtp.gmail.com', 587);server.starttls();server.login(mailname, mailpass);message = f"Subject: {subject}\n\n{body}";server.sendmail(mailname, to_email, message);server.quit()
def convert_image_to_grayscale(image_path, output_path):import cv2;image = cv2.imread(image_path);gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);cv2.imwrite(output_path, gray_image)
def get_weather(city,api_key):import requests;url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}";response = requests.get(url);return response.json()
def generate_unique_id():import uuid;return str(uuid.uuid4())
def start_background_task(backtask):
    import threading
    threading.Thread(target=backtask).start()
def nocrash(func): 
    def wrapper(*args, **kwargs):return safe_run(func, *args, **kwargs);return wrapper
def hotdog(k1="",k2="",k3="",k4="",k5=""):import pyautogui;pyautogui.hotkey(k1,k2,k3,k4,k5)
def keypress(key):import pyautogui;pyautogui.keyDown(key);pyautogui.keyUp(key)
def parallel(*functions):
    threads = []
    for func in functions:
        import threading
        thread = threading.Thread(target=func);threads.append(thread);thread.start()
    for thread in threads:thread.join()
def gs(func):import inspect;return inspect.getsource(func)