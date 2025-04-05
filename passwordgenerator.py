import tkinter as tk
import random
import string

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("400x400")

        self.create_widgets()

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(self.root, text="Password Generator", font=('Arial', 18))
        title_label.pack(pady=10)

        # Length Label and Entry
        length_label = tk.Label(self.root, text="Password Length:")
        length_label.pack()
        self.length_entry = tk.Entry(self.root)
        self.length_entry.pack(pady=5)

        # Checkboxes for character types
        self.use_uppercase = tk.BooleanVar()
        self.uppercase_checkbox = tk.Checkbutton(self.root, text="Include Uppercase Letters", variable=self.use_uppercase)
        self.uppercase_checkbox.pack()

        self.use_lowercase = tk.BooleanVar()
        self.lowercase_checkbox = tk.Checkbutton(self.root, text="Include Lowercase Letters", variable=self.use_lowercase)
        self.lowercase_checkbox.pack()

        self.use_numbers = tk.BooleanVar()
        self.numbers_checkbox = tk.Checkbutton(self.root, text="Include Numbers", variable=self.use_numbers)
        self.numbers_checkbox.pack()

        self.use_special = tk.BooleanVar()
        self.special_checkbox = tk.Checkbutton(self.root, text="Include Special Characters", variable=self.use_special)
        self.special_checkbox.pack()

        # Generate Button
        generate_button = tk.Button(self.root, text="Generate Password", command=self.generate_password)
        generate_button.pack(pady=20)

        # Result Label
        self.result_label = tk.Label(self.root, text="", font=('Arial', 14))
        self.result_label.pack(pady=10)

    def generate_password(self):
        try:
            length = int(self.length_entry.get())
            if length < 6:
                self.result_label.config(text="Password length should be at least 6.")
                return

            character_pool = ''
            if self.use_uppercase.get():
                character_pool += string.ascii_uppercase
            if self.use_lowercase.get():
                character_pool += string.ascii_lowercase
            if self.use_numbers.get():
                character_pool += string.digits
            if self.use_special.get():
                character_pool += string.punctuation

            if not character_pool:
                self.result_label.config(text="Select at least one character type.")
                return

            password = ''.join(random.choice(character_pool) for _ in range(length))
            self.result_label.config(text=f"Generated Password: {password}")

        except ValueError:
            self.result_label.config(text="Please enter a valid number for length.")

if __name__ == "__main__":
    root = tk.Tk()
    password_generator = PasswordGenerator(root)
    root.mainloop()