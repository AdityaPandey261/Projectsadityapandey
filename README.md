# Password Generator

A simple and interactive **Password Generator** tool built using **Python** and the **Tkinter** library. This program allows users to generate complex, random passwords based on their specific requirements. Users can customize the password length and select character types (uppercase letters, lowercase letters, numbers, and special characters) for a personalized password.

## Features

- **Customizable Password Length**: Users can specify the length of the password.
- **Character Type Selection**: 
  - Uppercase letters (A-Z)
  - Lowercase letters (a-z)
  - Numbers (0-9)
  - Special characters (e.g., `!@#$%^&*`)
- **Real-Time Password Generation**: Generate a random password that meets the selected criteria.
- **User-Friendly Interface**: Built using Python's Tkinter library for an interactive graphical interface.

## Requirements

- Python 3.x
- Tkinter (usually included with Python by default)

## Installation

1. Clone this repository to your local machine:
    ```bash
    git clone https://github.com/your-username/password-generator.git
    ```

2. Navigate to the project directory:
    ```bash
    cd password-generator
    ```

3. Make sure you have Python 3.x installed (Tkinter should come pre-installed with Python, but if not, install it using the following command):
    ```bash
    pip install tk
    ```

4. Run the `password_generator.py` script:
    ```bash
    python password_generator.py
    ```

## How to Use

1. When you run the program, a GUI window will appear.
2. Enter the desired password length in the "Password Length" field.
3. Use the checkboxes to select which types of characters you want in the password:
    - Uppercase Letters
    - Lowercase Letters
    - Numbers
    - Special Characters
4. Click on the "Generate Password" button.
5. The generated password will be displayed below the button. If no valid character type is selected, an error message will prompt you to select at least one character type.
6. If the entered password length is less than 6, an error message will be displayed.

## Example

- **Password Length**: 12
- **Selected Character Types**: Uppercase, Lowercase, Numbers, Special Characters

Generated password example: sT531@$scboi
