# Online Code Editor

A modern, feature-rich online code editor built with Django and JavaScript. This editor provides a seamless coding experience with features like file management, syntax highlighting, and code execution.

## Features

- **File Management**
  - Create, rename, and delete files and folders
  - Project-based organization
  - File tree navigation
  - Multiple file tabs

- **Code Editor**
  - Syntax highlighting for multiple languages
  - Auto-indentation
  - Line numbers
  - Code folding
  - Bracket matching
  - Multiple themes

- **Code Execution**
  - Run code directly from the editor
  - Support for multiple programming languages
  - Real-time output display
  - Error handling

- **User Interface**
  - Modern, dark theme
  - Resizable panels
  - Terminal integration
  - Responsive design

## Supported Languages

- Python
- JavaScript
- HTML/CSS
- Java
- C/C++
- PHP
- Ruby
- Go
- Rust
- Swift
- Kotlin
- TypeScript
- And more...

## Prerequisites

- Python 3.8 or higher
- Django 4.0 or higher
- Modern web browser

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/online-code-editor.git
cd online-code-editor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

6. Open your browser and navigate to `http://localhost:8000`

## Project Structure

```
online-code-editor/
├── codeeditor/              # Main Django application
│   ├── migrations/         # Database migrations
│   ├── templates/         # HTML templates
│   ├── static/           # Static files (CSS, JS, images)
│   ├── views.py          # View functions
│   ├── models.py         # Database models
│   └── urls.py           # URL routing
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## Usage

1. **Creating a Project**
   - Click "New Project" in the navigation bar
   - Enter a project name
   - Click "Create"

2. **Managing Files**
   - Use the file explorer to create, rename, or delete files/folders
   - Click on files to open them in the editor
   - Use the tabs to switch between open files

3. **Editing Code**
   - Write code in the editor
   - Use keyboard shortcuts for common operations
   - Code is automatically saved

4. **Running Code**
   - Open a file
   - Click the "Run" button
   - View output in the terminal panel

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CodeMirror](https://codemirror.net/) for the code editor
- [Bootstrap](https://getbootstrap.com/) for the UI framework
- [Font Awesome](https://fontawesome.com/) for icons 