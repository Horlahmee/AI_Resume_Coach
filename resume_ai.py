import subprocess
import datetime
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox

LOG_FILE = "ai_responses.log"  # Log file to store responses
PROMPTS_FILE = "saved_prompts.txt"  # File to save prompts
RESPONSES_FILE = "saved_responses.txt"  # File to save responses

def get_ai_response(prompt):
    if prompt.lower() in ["what is your name?", "who are you?"]:
        return "My name is ResumeGenie, I'm an AI designed to help you craft the perfect resume and give you career-boosting insights. Feel free to ask me anything."
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt], capture_output=True, text=True
        )
        response = result.stdout.strip()
        log_response(prompt, response)  # Log the response
        return response
    except FileNotFoundError:
        return "Error: AI model not found. Please ensure the model is properly installed."
    except subprocess.CalledProcessError:
        return "Error: An issue occurred while running the AI model."
    except Exception as e:
        return f"Unexpected error: {e}"

def log_response(prompt, response):
    """Logs the prompt and AI response to a file with a timestamp."""
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] Prompt: {prompt}\n")
        log.write(f"[{timestamp}] Response: {response}\n\n")

def save_prompt(prompt, response):
    """Saves the prompt and response separately for reuse."""
    with open(PROMPTS_FILE, "a") as p_file, open(RESPONSES_FILE, "a") as r_file:
        prompt_number = sum(1 for _ in open(PROMPTS_FILE, "r")) + 1
        p_file.write(f"{prompt_number}. {prompt}\n")
        r_file.write(f"{prompt_number}. {response}\n")

def display_saved_prompts():
    """Displays previously saved prompts with numbering."""
    try:
        with open(PROMPTS_FILE, "r") as file:
            content = file.read().strip()
            if not content:
                messagebox.showinfo("Saved Prompts", "No saved prompts yet.")
                return
            prompts = content.split("\n")
            prompt_list = "\n".join(prompts)
            prompt_number = simple_input_dialog("Select a prompt number to view its response:", prompt_list)
            if prompt_number and prompt_number.isdigit():
                display_saved_response(prompt_number)
    except FileNotFoundError:
        messagebox.showinfo("Saved Prompts", "No saved prompts found.")

def display_saved_response(prompt_number):
    """Displays the response linked to a selected prompt."""
    try:
        with open(RESPONSES_FILE, "r") as file:
            responses = file.readlines()
            for response in responses:
                if response.startswith(f"{prompt_number}."):
                    messagebox.showinfo("Response", response.strip())
                    return
        messagebox.showinfo("Response", "Response not found.")
    except FileNotFoundError:
        messagebox.showinfo("Response", "No saved responses found.")

def delete_prompt():
    """Deletes all saved prompts and responses."""
    if os.path.exists(PROMPTS_FILE):
        os.remove(PROMPTS_FILE)
    if os.path.exists(RESPONSES_FILE):
        os.remove(RESPONSES_FILE)
    messagebox.showinfo("Delete Prompts", "All saved prompts and responses deleted successfully!")

def simple_input_dialog(title, prompt_list):
    """Creates a simple input dialog to select a prompt number."""
    dialog = tk.Toplevel(root)
    dialog.title(title)
    tk.Label(dialog, text=prompt_list).pack()
    entry = tk.Entry(dialog)
    entry.pack()
    result = []
    
    def submit():
        result.append(entry.get())
        dialog.destroy()
    
    tk.Button(dialog, text="OK", command=submit).pack()
    dialog.wait_window()
    return result[0] if result else None

def on_submit():
    prompt = user_input.get()
    if not prompt:
        return
    response = get_ai_response(prompt)
    output_text.insert(tk.END, f"You: {prompt}\n")
    output_text.insert(tk.END, f"AI: {response}\n\n")
    output_text.yview(tk.END)
    
    # Ask user if they want to save the prompt/response
    save_response = messagebox.askyesno("Save Response", "Do you want to save this prompt and response?")
    if save_response:
        save_prompt(prompt, response)
        messagebox.showinfo("Saved", "Prompt and response saved!")

def clear_text():
    output_text.delete(1.0, tk.END)

def exit_app():
    root.destroy()

# Tkinter GUI setup
root = tk.Tk()
root.title("ResumeGenie - AI Resume & Career Assistant")
root.geometry("600x500")

frame = tk.Frame(root)
frame.pack(pady=10)

user_input = tk.Entry(frame, width=60)
user_input.pack(side=tk.LEFT, padx=5)

submit_button = tk.Button(frame, text="Ask", command=on_submit)
submit_button.pack(side=tk.RIGHT)

output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
output_text.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

clear_button = tk.Button(button_frame, text="Clear", command=clear_text)
clear_button.pack(side=tk.LEFT, padx=5)

view_saved_button = tk.Button(button_frame, text="View Saved Prompts", command=display_saved_prompts)
view_saved_button.pack(side=tk.LEFT, padx=5)

delete_saved_button = tk.Button(button_frame, text="Delete Saved Prompts", command=delete_prompt)
delete_saved_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(button_frame, text="Exit", command=exit_app)
exit_button.pack(side=tk.RIGHT, padx=5)

root.mainloop()
