# Textual Studio Code

A terminal-based code editor built with [Textual](https://github.com/Textualize/textual), featuring:

- Directory tree for file browsing
- Multi-tabbed interface for editing multiple files
- Footer displaying current cursor position and selection status
- Keyboard shortcuts for toggling UI and closing tabs
- Markdown extended support.
- Saving functionality.

---

## Features

- **Directory Tree**  
  Browse files from a configurable root directory on the left panel.

- **Tabbed Editor**  
  Open multiple files in tabs with a syntax-aware `CodeView`.

- **Footer Status Bar**  
  Shows line, column, dynamically. 

---

## Getting Started

### Requirements

- Python 3.10 or newer
- `textual` library

Install dependencies:

```bash
pip install textual
pip install textual[syntax]
```

### How to run?

Simply type:

```bash
python cli.py
```

If you want, you can open the directory tree in a specific folder,
```bash
python cli.py [DIR_NAME]
```

---

Thanks for everything!

This project is still under development, and many functions are not yet disponible.