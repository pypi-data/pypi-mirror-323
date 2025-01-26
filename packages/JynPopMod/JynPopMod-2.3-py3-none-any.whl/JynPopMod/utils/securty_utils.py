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

import os
import base64
import hmac
import hashlib
import time
import qrcode
from tkinter import simpledialog, Tk, Label, Button
from PIL import Image, ImageTk
from better_profanity import profanity

def popinp(_p, _t="Input"):
    return simpledialog.askstring(_t, _p) or None

def genSK(secret_key, time_step=30, digits=6):
    epoch_time = int(time.time())
    time_counter = epoch_time // time_step
    time_counter_bytes = time_counter.to_bytes(8, 'big')
    key = base64.b32decode(secret_key)
    hmac_hash = hmac.new(key, time_counter_bytes, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 15
    binary_code = (hmac_hash[offset] & 127) << 24 | (hmac_hash[offset + 1] & 255) << 16 | (hmac_hash[offset + 2] & 255) << 8 | (hmac_hash[offset + 3] & 255)
    otp = binary_code % 10**digits
    return str(otp).zfill(digits)

def generate_qr(secret_key, app_name, user_name):
    uri = f"otpauth://totp/{app_name}:{app_name}?secret={secret_key}&issuer={user_name}&algorithm=SHA1&digits=6&period=30"
    qr = qrcode.make(uri)
    qr.save('qrcode.png')

def verify_code(secret_key, func, result_label, window):
    user_code = popinp('Enter the code in the Authenticator app: ')
    if user_code == genSK(secret_key):
        result_label.config(text='Auth is done!', fg='green')
        window.after(2000, lambda: [window.destroy(), func()])
    else:
        result_label.config(text='Wrong code or misspell!', fg='red')

def show_qr(func, app_name, user_name):
    secret_key = base64.b32encode(b'mysecretkey12345').decode()
    generate_qr(secret_key, app_name, user_name)
    
    window = Tk()
    window.title('JynAuth')

    img = Image.open('qrcode.png').resize((300, 300))
    img = ImageTk.PhotoImage(img)
    qr_label = Label(window, image=img)
    qr_label.pack()

    result_label = Label(window, text='')
    result_label.pack()

    verify_button = Button(window, text='Verify', command=lambda: verify_code(secret_key, func, result_label, window))
    verify_button.pack()

    if os.path.exists('qrcode.png'):
        os.remove('qrcode.png')

    window.mainloop()

def Jynauth(func, user_name, app_name):
    show_qr(func, app_name, user_name)

def Jctb(input_string):
    def char_to_binary(c):
        if c == ' ':
            return '0000000001'
        elif c == '\n':
            return '0000000010'
        alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alphabet_lower = 'abcdefghijklmnopqrstuvwxyz'
        if c in alphabet_upper:
            return format(alphabet_upper.index(c), '010b')
        elif c in alphabet_lower:
            return format(alphabet_lower.index(c) + 26, '010b')
        return None

    binary_string = ''.join(char_to_binary(char) for char in input_string if char_to_binary(char))
    return binary_string

def Jbtc(binary_input):
    def binary_to_char(binary_vector):
        if binary_vector == '0000000001':
            return ' '
        elif binary_vector == '0000000010':
            return '\n'
        alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alphabet_lower = 'abcdefghijklmnopqrstuvwxyz'
        num = int(binary_vector, 2)
        if 0 <= num <= 25:
            return alphabet_upper[num]
        elif 26 <= num <= 51:
            return alphabet_lower[num - 26]
        return None

    char_list = [binary_to_char(binary_input[i:i+10]) for i in range(0, len(binary_input), 10)]
    return ''.join(char_list)
