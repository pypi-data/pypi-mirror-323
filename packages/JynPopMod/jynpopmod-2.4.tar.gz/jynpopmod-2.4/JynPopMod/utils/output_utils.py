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

import sys
import functools

class LoadingBar:
    def __init__(self, total_steps, bar_length=40):
        self.total_steps = total_steps
        self.bar_length = bar_length
        self.progress = 0

    def load(self):
        self.progress += 1
        bar = '█' * (self.progress * self.bar_length // self.total_steps)
        spaces = ' ' * (self.bar_length - len(bar))
        sys.stdout.write(f'\rProcessing: |{bar}{spaces}| {((self.progress) / self.total_steps) * 100:.2f}%')
        sys.stdout.flush()

    def finish(self):
        sys.stdout.write(f'\rProcessing: |{"█" * self.bar_length}| 100.00%\n')
        sys.stdout.flush()

def track_function_start_end(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.bar.load()
        result = func(*args, **kwargs)
        wrapper.bar.load()
        return result
    return wrapper

def loading_bar(code):
    lines = code.splitlines()
    steps = sum(1 for line in lines if '(' in line and ')' in line)
    bar = LoadingBar(steps)
    track_function_start_end.bar = bar
    exec(code)
    bar.finish()

def JynPopMod():
    print("Click to see about JynPopMod https://github.com/Jynoqtra/JynPopMod that made by Jynoqtra")
