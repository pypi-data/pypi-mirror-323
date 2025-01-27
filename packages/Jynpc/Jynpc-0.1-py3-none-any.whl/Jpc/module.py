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
import time
import shutil
import psutil
import subprocess
import json
import mouse
from tkinter import simpledialog
import sys

def find_files_by_extension(directory, extension):
    return [f for f in os.listdir(directory) if f.endswith(extension)]

def get_curr_dir():
    return os.getcwd()

def ccc(core_count, function, *args, **kwargs):
    total_cores = os.cpu_count()
    if core_count > total_cores:
        raise ValueError(f"Your input core count ({core_count}) can't be bigger than total core count ({total_cores}).")
    core_nums = list(range(core_count))
    p = psutil.Process(os.getpid())
    p.cpu_affinity(core_nums)
    return function(*args, **kwargs)

def check_if_file_exists(file_path):
    return os.path.exists(file_path)

def monitor_new_files(directory, callback):
    known_files = set(os.listdir(directory))
    while True:
        current_files = set(os.listdir(directory))
        new_files = current_files - known_files
        if new_files:
            callback(new_files)
        known_files = current_files
        time.sleep(1)

def get_system_uptime():
    return time.time() - psutil.boot_time()

def get_cpu_templinux():
    if sys.platform == 'linux':
        try:
            return float(subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])) / 1000
        except (subprocess.CalledProcessError, FileNotFoundError, PermissionError) as e:
            print(f"Error retrieving CPU temperature: {e}")
            return None
    return None


def monitor_file_changes(file_path, callback):
    last_modified = os.path.getmtime(file_path)
    while True:
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:
            last_modified = current_modified
            callback()
        time.sleep(1)

def write_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def read_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def parse_json(json_string):
    return json.loads(json_string)

def create_file_if_not_exists(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write('')

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def track_mouse_position(callback):
    def on_move(x, y):
        callback(x, y)
    with mouse.Listener(on_move=on_move) as listener:
        listener.join()

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    return psutil.virtual_memory().percent

def create_zip_file(source_dir, output_zip):
    shutil.make_archive(output_zip, 'zip', source_dir)

def extract_zip_file(zip_file, extract_dir):
    shutil.unpack_archive(zip_file, extract_dir)

def move_file(source, destination):
    shutil.move(source, destination)

def copy_file(source, destination):
    shutil.copy(source, destination)

def show_file_properties(file_path):
    stats = os.stat(file_path)
    return f"Size: {stats.st_size} bytes, Last Modified: {time.ctime(stats.st_mtime)}"

def run_shell_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return result.stdout.decode(), result.stderr.decode()
