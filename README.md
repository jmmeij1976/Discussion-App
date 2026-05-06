# Student Introduction Thread Generator

This Python script helps students create personalized introduction posts for a course discussion thread. It prompts users with a series of questions, collects their answers, and generates a formatted introduction text that can be copied into a forum or discussion board. Additionally, it saves all responses to a CSV file for record-keeping.

## Features

- Interactive prompts for 8 introduction questions
- Generates a cohesive introduction paragraph
- Saves responses to `student_introductions.csv` with questions as columns and students as rows
- Easy to run and customize

## Requirements

- Python 3.x
- No external libraries required (uses built-in `csv` and `os` modules)

## Usage

1. Download or clone this repository.
2. Run the script: `python introduction_thread.py`
3. Answer each question when prompted.
4. The script will display the formatted introduction text.
5. Responses are automatically saved to `student_introductions.csv` in the same directory.

## Questions Asked

1. What is your name?
2. What is your major?
3. What made you enroll in this course?
4. What are you most excited about to learn in this course?
5. What is your biggest fear about this course?
6. What are three things about yourself that people cannot tell by looking at you?
7. What is the best way to contact you? (e.g., cell phone or email address)
8. What would you like to know about the professor?

## Output

- **Console**: A formatted introduction paragraph ready for posting.
- **CSV File**: `student_introductions.csv` containing all student responses, which can be opened in Excel or any spreadsheet application.

## Example Output

```
Hello everyone! My name is John Doe, and my major is Computer Science. I enrolled in this course because I want to learn about AI. I'm most excited to learn machine learning. My biggest fear about this course is falling behind. Three things about myself that people cannot tell by looking at me are I love hiking, I'm a vegetarian, and I play the guitar. The best way to contact me is john.doe@email.com. What I would like to know about the professor is their research interests.
```

## Customization

To modify the questions or introduction format, edit the `questions` list and the `introduction` string in the script.

## License

This project is open-source. Feel free to use and modify as needed.