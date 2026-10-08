import subprocess

subprocess.call(["python", "merge listings.py"])
subprocess.call(["python", "Cleaning.py"])
subprocess.call(["python", "Get Area Codes.py"])
subprocess.call(["python", "combining datasets and plots.py"])

print("success....")
