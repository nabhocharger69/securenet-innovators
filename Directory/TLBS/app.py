import tkinter as tk
from tkinter import messagebox
import yaml
import subprocess


# Function to generate the config.yaml file
def load_config():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a valid URL")
        return

    config_data = {
        'RequestRatePerSec': 200,
        'Duration': '10s',
        'Request': {
            'URL': url
        }
    }

    # Write to config.yaml
    with open('config.yaml', 'w') as file:
        yaml.dump(config_data, file)

    messagebox.showinfo("Success", "config.yaml file generated successfully!")


# Function to run the benchmarking executable and store the output in output.txt
def run_benchmark():
    try:
        # Run the benchmarking.exe and capture the output
        result = subprocess.run(['benchmarking.exe'], capture_output=True, text=True, check=True)

        # Write the captured output to output.txt
        with open('output.txt', 'w') as file:
            file.write(result.stdout)

        messagebox.showinfo("Success", "Benchmark executed successfully and output saved!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error while running benchmark: {e}")


# Function to display the results from the output.txt file
def show_results():
    try:
        with open('output.txt', 'r') as file:
            output_content = file.read()

        # Create a new window to display the results
        result_window = tk.Toplevel(root)
        result_window.title("Benchmark Results")

        text_widget = tk.Text(result_window, wrap='word', width=80, height=20)
        text_widget.insert(tk.END, output_content)
        text_widget.config(state=tk.DISABLED)  # Make text widget read-only
        text_widget.pack(padx=10, pady=10)

    except FileNotFoundError:
        messagebox.showerror("Error", "output.txt file not found!")


# Create the main Tkinter window
root = tk.Tk()
root.title("Benchmark Tool")

# Create UI elements
url_label = tk.Label(root, text="Enter HTTP Server URL:")
url_label.pack(pady=5)

url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

load_button = tk.Button(root, text="Load", command=load_config)
load_button.pack(pady=5)

benchmark_button = tk.Button(root, text="Benchmark", command=run_benchmark)
benchmark_button.pack(pady=5)

show_results_button = tk.Button(root, text="Show Results", command=show_results)
show_results_button.pack(pady=5)

# Start the Tkinter event loop
root.mainloop()
