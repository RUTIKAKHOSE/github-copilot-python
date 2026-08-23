# Project Instructions

# Project Overview

This project is a Flask-based Sudoku game. The goal is to refactor the existing legacy code and extend the application with modern, maintainable functionality while preserving existing behavior.

# Technology

- Python 3
- Flask
- HTML
- CSS
- JavaScript
- Local Storage for persistent scoreboard data

# Code Quality

- Follow modern Python coding practices.
- Use clear and meaningful variable and function names.
- Keep functions small and focused on one responsibility.
- Prefer reusable functions and modular components over repetitive code.
- Use consistent 4-space indentation.
- Add comments where they help explain non-obvious logic.
- Handle errors gracefully.
- Avoid unnecessary changes to existing working functionality.

# Sudoku Logic

- The Sudoku board must follow standard 9x9 Sudoku rules.
- Generated puzzles must have exactly one unique solution.
- Prefilled cells must remain locked.
- Easy, Medium, and Hard difficulty levels should control the number of prefilled cells.
- Invalid user entries should provide immediate visual feedback.
- A correctly completed puzzle should display a completion message.

# Game Features

The application should support:

- Difficulty selection
- Sudoku puzzle generation
- Unique-solution validation
- Hint functionality
- Check functionality
- Timer
- Top 10 scoreboard
- Local Storage persistence
- Dark mode

# Frontend and Accessibility

- Keep the interface responsive on desktop and mobile screens.
- Ensure the interface works in both light and dark modes.
- Maintain readable text and controls.
- Use clear visual differences between the 3x3 Sudoku sections.
- Avoid layout shifts when the board or controls change.

# Testing

- Do not remove existing functionality while refactoring.
- Run the test suite after significant changes.
- When adding a feature, consider adding or updating tests.
- Do not assume code works without testing it.

# GitHub Copilot Usage

When suggesting code:

1. Explain important changes when requested.
2. Prefer small, understandable changes.
3. Consider the existing project structure before modifying files.
4. Do not introduce unnecessary dependencies.
5. Point out potential problems or trade-offs in a suggestion.
6. Ask for clarification when requirements are ambiguous.

# Project Requirements

All implementation should support the Udacity project rubric, including:

- Modular and reusable code
- Consistent error handling
- Responsive interface
- Light and dark modes
- Unique Sudoku solutions
- Difficulty levels
- Locked prefilled cells
- Invalid-move feedback
- Hint and Check buttons
- Timer
- Persistent Top 10 scoreboard