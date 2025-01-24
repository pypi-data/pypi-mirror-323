import os

def run_script():
    print("Hello from Python Script")
    os.makedirs("my_directory", exist_ok=True)
    open("my_directory/sample.txt", "a").close()

