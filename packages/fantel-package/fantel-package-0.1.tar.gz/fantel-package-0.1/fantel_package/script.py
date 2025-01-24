import os

def run_script():
    print("Hello from Python Script")
    os.makedirs("my_directory", exist_ok=True)
    with open("my_directory/sample.txt", "w") as file:
        file.write("This is a sample file.")
    print("Directory and file created.")

