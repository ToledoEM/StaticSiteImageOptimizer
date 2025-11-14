import subprocess

cmd = ["python", "-m", "pip", "install", "-e", ".[pillow]"]
print('Running:', ' '.join(cmd))
subprocess.check_call(cmd)
