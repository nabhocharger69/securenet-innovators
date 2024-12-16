import tkinter as tk
from tkinter import filedialog, messagebox
from huggingface_hub import InferenceClient

# Hardcoded HuggingFace API token
HF_API_KEY = "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"
client = InferenceClient("microsoft/Phi-3-mini-4k-instruct", token=HF_API_KEY)

# Function to read the content of a file
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read the file: {e}")
        return None

# Function to generate explanation using HuggingFace model
def generate_explanation(file_content):
    messages = [
        {
            "role": "user",
            "content": f"The following is an intrusion detection and prevention benchmarking report:\n{file_content}\nPlease explain the report and provide actionable suggestions to improve the system."
        }
    ]
    response = ""
    try:
        for message in client.chat_completion(messages=messages, max_tokens=500, stream=True):
            response += message.choices[0].delta.content
        return response
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate explanation: {e}")
        return None

# Function to handle file selection and processing
def process_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return

    file_content = read_file(file_path)
    if file_content:
        explanation = generate_explanation(file_content)
        if explanation:
            text_box.config(state=tk.NORMAL)
            text_box.delete(1.0, tk.END)
            text_box.insert(tk.END, explanation)
            text_box.config(state=tk.DISABLED)

# Set up the Tkinter window
root = tk.Tk()
root.title("Intrusion Detection Report Analysis")
root.geometry("600x400")
root.config(bg="#f2f2f2")

# Main frame for user inputs and action buttons
main_frame = tk.Frame(root, bg="#f2f2f2")
main_frame.pack(pady=20, padx=20)

# Header label
header_label = tk.Label(
    main_frame, text="Intrusion Detection Report Analyzer", font=("Arial", 16), bg="#f2f2f2"
)
header_label.grid(row=0, column=0, columnspan=2, pady=10)

# File selection button
file_button = tk.Button(
    main_frame, text="Select Report File", font=("Arial", 12), bg="#4CAF50", fg="white", command=process_file
)
file_button.grid(row=1, column=0, columnspan=2, pady=20)

# Frame for displaying the explanation
explanation_frame = tk.Frame(root, bg="#e0e0e0", relief="sunken", bd=2)
explanation_frame.pack(padx=20, pady=10)

# Text box to display the explanation
explanation_label = tk.Label(
    explanation_frame, text="Explanation and Suggestions:", font=("Arial", 12), bg="#e0e0e0"
)
explanation_label.grid(row=0, column=0, padx=10, pady=10)

text_box = tk.Text(
    explanation_frame, height=10, width=60, font=("Arial", 10), state=tk.DISABLED, wrap="word"
)
text_box.grid(row=1, column=0, padx=10, pady=10)

# Run the application
root.mainloop()
