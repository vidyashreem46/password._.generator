# SecurePass Pro

**SecurePass Pro** is a modern Python desktop application built with **CustomTkinter**. It helps users generate strong passwords, analyze password strength, view security details, and save password history in JSON format.

This project is developed as a **B.Sc. (Hons.) Data Science & Artificial Intelligence**as a student

---

## Project Subtitle

**Smart Password Generator & Analyzer**

---

## Features
- Modern dark mode GUI
- User-friendly scrollable interface
- Password length slider from 8 to 64 characters
- Synchronized password length entry box
- Include uppercase letters
- Include lowercase letters
- Include numbers
- Include symbols
- Avoid ambiguous characters such as `0`, `O`, `l`, `I`, `1`
- Platform-based password recommendations
- Apply recommended settings button
- Generate strong random passwords
- Show / hide generated password
- Copy password to clipboard
- Password strength analysis:
  - Very Weak
  - Weak
  - Medium
  - Strong
  - Very Strong
- Entropy calculation
- Estimated crack time
- Character pool size
- Platform policy check
- Security advice
- Password history using `history.json`
- View history in a separate window
- Delete history with confirmation
- Menu bar with File, Generate, History, and Help options
- Status bar and footer

---

## Platform-Based Recommendations
SecurePass Pro includes real-world password suggestions for different platforms:

- Gmail
- Instagram
- Facebook
- Banking
- GitHub
- College Portal
- Other

Each platform has recommended password settings such as length, character types, and security level.

---

## Technologies Used
- Python 3.10+
- CustomTkinter
- pyperclip
- random
- string
- json
- os
- datetime
- math
- tkinter

---

## Installation
First, clone the repository:
