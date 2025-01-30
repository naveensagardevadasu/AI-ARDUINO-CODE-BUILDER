import openai
import os
import re
import subprocess
from datetime import datetime

# Set up your OpenAI API key
openai.api_key = "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"

#AI + Arduino

print("Hello World!")

# Function to get Arduino code from ChatGPT based on the prompt
def generate_arduino_code(prompt):
    detailed_prompt = f"{prompt}\nPlease provide only the Arduino code between /* START */ and /* END */ comments."
    
    messages = [
        {"role": "system", "content": "You are an assistant that generates Arduino code based on user requests."},
        {"role": "user", "content": detailed_prompt}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Or "gpt-4" if available
        messages=messages,
        max_tokens=300,  # Adjust as needed for Arduino code size
        temperature=0.2  # Lower temperature for more deterministic output
    )
    
    # Extract the generated code
    raw_code = response['choices'][0]['message']['content']
    
    # Use regex to extract code between /* START */ and /* END */
    match = re.search(r'/\* START \*/(.*?)/\* END \*/', raw_code, re.DOTALL)
    if match:
        code = match.group(1).strip()
        return code
    else:
        raise ValueError("Code delimiters not found in the generated response.")

# Function to save code in a new folder with a meaningful name
def save_code_in_folder(code, prompt):
    # Generate a folder name based on the prompt or timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"Arduino_Code_{timestamp}"
    os.makedirs(folder_name, exist_ok=True)
    
    # Create the .ino file in the new folder
    file_path = os.path.join(folder_name, "generated_code.ino")
    with open(file_path, "w") as file:
        file.write(code)
    
    return file_path

# Function to upload the code to Arduino board using Arduino CLI
def upload_to_arduino(file_path, port, board):
    try:
        # Compile the code
        compile_command = ["arduino", "--verbose","--board", board,"--verify", file_path]
        subprocess.run(compile_command, check=True)
        
        # Upload the code to the specified port
        upload_command = ["arduino", "--verbose", "--board", board, "--upload",file_path, "--port", port]
        subprocess.run(upload_command, check=True)
        
        print("Code uploaded successfully!")
    except subprocess.CalledProcessError as e:
        print("Error during compilation or upload:", e)

# Main function
def main():
    # Ask the user for a prompt
    prompt = input("Enter your Arduino project description: ")
    
    # Generate Arduino code from the prompt
    try:
        arduino_code = generate_arduino_code(prompt)
        print("Extracted Code:\n", arduino_code)
        
        # Save the code to a uniquely named folder in the current directory
        file_path = save_code_in_folder(arduino_code, prompt)
        print(f"Code saved to: {file_path}")
        
        # Set your Arduino port and board fully qualified board name (FQBN)
        arduino_port = "/dev/ttyACM0"  # Example for Linux (modify based on your system)
        board_fqbn = "arduino:avr:uno"  # Adjust to your board type

        # Upload the code to the Arduino board
        upload_to_arduino(file_path, arduino_port, board_fqbn)

    except ValueError as e:
        print("Error extracting code:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)

if __name__ == "__main__":
    main()
