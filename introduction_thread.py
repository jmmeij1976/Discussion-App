import csv
import os

questions = [
    "What is your name?",
    "What is your major?",
    "What made you enroll in this course?",
    "What are you most excited about to learn in this course?",
    "What is your biggest fear about this course?",
    "What are three things about yourself that people cannot tell by looking at you?",
    "What is the best way to contact you? (e.g., cell phone or email address)",
    "What would you like to know about the professor?"
]

answers = []

for question in questions:
    answer = input(question + " ")
    answers.append(answer)

# Save answers to CSV file
filename = 'student_introductions.csv'
file_exists = os.path.isfile(filename)
with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    if not file_exists:
        writer.writerow(questions)  # Write header if file doesn't exist
    writer.writerow(answers)  # Append the student's answers

# Format the introduction based on the answers
introduction = f"Hello everyone! My name is {answers[0]}, and my major is {answers[1]}. I enrolled in this course because {answers[2]}. I'm most excited to learn {answers[3]}. My biggest fear about this course is {answers[4]}. Three things about myself that people cannot tell by looking at me are {answers[5]}. The best way to contact me is {answers[6]}. What I would like to know about the professor is {answers[7]}."

print(introduction)