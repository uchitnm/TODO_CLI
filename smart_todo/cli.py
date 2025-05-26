#!/usr/bin/env python3

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
import inquirer
from dateutil import parser
from inquirer import errors
from google import genai
from google.genai import types

console = Console()

class Task:
    MOOD_ICONS = {
        "any": "*",
        "energetic": "[E]",
        "focused": "[F]",
        "creative": "[C]",
        "relaxed": "[R]",
        "tired": "[T]"
    }

    STATUS_OPTIONS = ["Not Started", "In Progress", "Completed"]
    EFFORT_LEVELS = ["Short", "Medium", "Long"]  # 15-30min, 30min-1hr, >1hr
    DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
    ENERGY_LEVELS = ["Low", "Medium", "High"]
    PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]

    def __init__(self, title: str, description: str, deadline: str, 
                 priority: int = 1, mood_required: str = "any",
                 effort: str = "Medium", difficulty: str = "Medium",
                 energy_required: str = "Medium"):
        self.title = title
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.mood_required = mood_required
        self.effort = effort
        self.difficulty = difficulty
        self.energy_required = energy_required
        self.completed = False
        self.status = "Not Started"  # Not Started, In Progress, Completed
        self.suggestion_reason = ""

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline,
            "priority": self.priority,
            "mood_required": self.mood_required,
            "effort": self.effort,
            "difficulty": self.difficulty,
            "energy_required": self.energy_required,
            "completed": self.completed,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        task = cls(
            data["title"],
            data["description"],
            data["deadline"],
            data["priority"],
            data.get("mood_required", "any"),
            data.get("effort", "Medium"),
            data.get("difficulty", "Medium"),
            data.get("energy_required", "Medium")
        )
        task.completed = data.get("completed", False)
        task.status = data.get("status", "Not Started")
        return task

    def calculate_urgency_score(self) -> float:
        """Calculate urgency score based on deadline and priority"""
        try:
            deadline = parser.parse(self.deadline)
            now = datetime.now()
            hours_until_deadline = (deadline - now).total_seconds() / 3600

            # Base urgency score based on time until deadline
            if hours_until_deadline <= 24:
                urgency = 100
            elif hours_until_deadline <= 48:
                urgency = 80
            elif hours_until_deadline <= 72:
                urgency = 60
            else:
                urgency = max(10, 100 - (hours_until_deadline / 24))

            # Adjust based on priority (1-3 scale)
            priority_multiplier = {1: 0.8, 2: 1.0, 3: 1.2}
            urgency *= priority_multiplier.get(self.priority, 1.0)

            return min(100, urgency)
        except:
            return 10  # Default low urgency for tasks without valid deadlines

    def get_mood_with_icon(self) -> str:
        return f"{self.MOOD_ICONS.get(self.mood_required, '')} {self.mood_required}"

class TodoManager:
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(task_data) for task_data in data]

    def save_tasks(self):
        with open(self.filename, 'w') as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=2)

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.save_tasks()

    def get_suggested_task(self, current_mood: str) -> Task:
        now = datetime.now()
        available_tasks = [
            task for task in self.tasks 
            if not task.completed and task.status != "Completed"
        ]

        if not available_tasks:
            return None

        # Prepare task data for AI analysis
        tasks_info = []
        for task in available_tasks:
            deadline = parser.parse(task.deadline)
            time_until_deadline = (deadline - now).total_seconds() / 3600  # hours
            urgency_score = task.calculate_urgency_score()
            
            tasks_info.append({
                "title": task.title,
                "description": task.description,
                "hours_until_deadline": time_until_deadline,
                "urgency_score": urgency_score,
                "priority": task.priority,
                "mood_required": task.mood_required,
                "effort": task.effort,
                "difficulty": task.difficulty,
                "energy_required": task.energy_required,
                "status": task.status
            })

        # Use Gemini API for smart task suggestion
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        prompt = f"""
        You are a task recommendation engine. Your goal is to suggest the best task for the user to work on right now.
        
        User's Current State:
        - Mood: {current_mood}
        - Current Time: {now.strftime('%Y-%m-%d %H:%M')}
        
        Available Tasks:
        {json.dumps(tasks_info, indent=2)}
        
        Consider these factors in order of importance:
        1. Task urgency (based on deadline and urgency_score)
        2. Match between task's energy/difficulty requirements and user's current mood
        3. Priority level of the task
        4. Task complexity and estimated effort
        
        Guidelines:
        - If user is energetic: Prefer challenging tasks that require high energy
        - If user is focused: Prefer complex tasks that require concentration
        - If user is creative: Prefer tasks that involve planning or creative work
        - If user is relaxed: Prefer lighter tasks unless there's something urgent
        
        Format your response exactly like this:
        TASK: [Suggested Task Title]
        REASON: [1-2 sentences explaining why this task is the best choice right now]
        """

        try:
            model = "gemini-2.5-flash-preview-04-17"
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=generate_content_config,
            ).text.strip()

            # Parse the response
            task_line = ""
            reason = ""
            for line in response.split('\n'):
                if line.startswith('TASK:'):
                    task_line = line.replace('TASK:', '').strip()
                elif line.startswith('REASON:'):
                    reason = line.replace('REASON:', '').strip()

            # Find the task with the suggested title
            suggested_task = None
            for task in available_tasks:
                if task.title.lower() in task_line.lower():
                    suggested_task = task
                    suggested_task.suggestion_reason = reason
                    return suggested_task

            # Fallback to original sorting method if AI suggestion fails
            available_tasks.sort(key=lambda x: (
                parser.parse(x.deadline),
                -x.priority
            ))
            return available_tasks[0]

        except Exception as e:
            console.print(f"AI suggestion failed: {str(e)}", style="yellow")
            # Fallback to original sorting method
            available_tasks.sort(key=lambda x: (
                parser.parse(x.deadline),
                -x.priority
            ))
            return available_tasks[0]

    def mark_completed(self, title: str):
        for task in self.tasks:
            if task.title == title:
                task.completed = True
                break
        self.save_tasks()

    def list_tasks(self, show_completed: bool = False):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title")
        table.add_column("Description")
        table.add_column("Deadline")
        table.add_column("Priority")
        table.add_column("Mood")
        table.add_column("Status")
        table.add_column("Effort")
        table.add_column("Energy")

        for task in self.tasks:
            if show_completed or not task.completed:
                priority_style = {
                    1: "blue",
                    2: "yellow",
                    3: "red bold",
                    4: "red bold reverse"
                }.get(task.priority, "white")
                
                status_style = {
                    "Not Started": "yellow",
                    "In Progress": "blue bold",
                    "Completed": "green"
                }.get(task.status, "white")

                table.add_row(
                    task.title,
                    task.description,
                    task.deadline,
                    Text(str(task.priority), style=priority_style),
                    task.get_mood_with_icon(),
                    Text(task.status, style=status_style),
                    task.effort,
                    task.energy_required
                )

        console.print(table)

    def update_task_status(self, title: str, new_status: str):
        for task in self.tasks:
            if task.title == title:
                if new_status == "Completed":
                    task.completed = True
                task.status = new_status
                break
        self.save_tasks()

def validate_date(answers, current):
    if not current:
        raise errors.ValidationError('', reason='Deadline cannot be empty')
    try:
        date = parser.parse(current)
        now = datetime.now()
        if date < now:
            raise errors.ValidationError('', reason='Deadline cannot be in the past')
        return True
    except ValueError:
        raise errors.ValidationError('', reason='Please use format YYYY-MM-DD HH:MM')

def suggest_deadline():
    """Suggest some common deadline options"""
    now = datetime.now()
    today_end = now.replace(hour=17, minute=0, second=0, microsecond=0)
    tomorrow_end = (now + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
    next_week = (now + timedelta(days=7)).replace(hour=17, minute=0, second=0, microsecond=0)
    
    if now.hour < 17:  # If it's before 5 PM
        today = today_end.strftime("%Y-%m-%d %H:%M")
    else:
        today = tomorrow_end.strftime("%Y-%m-%d %H:%M")
        
    tomorrow = tomorrow_end.strftime("%Y-%m-%d %H:%M")
    week = next_week.strftime("%Y-%m-%d %H:%M")
    
    return [
        f"Today ({today})",
        f"Tomorrow ({tomorrow})",
        f"Next week ({week})",
        "Custom date"
    ]

@click.group()
def cli():
    """Smart Todo List - Helps you manage tasks based on time and mood"""
    pass

@cli.command()
def add():
    """Add a new task interactively"""
    questions = [
        inquirer.Text('title', message="Task title"),
        inquirer.Text('description', message="Task description"),
        inquirer.List('deadline_option',
                     message="Choose deadline",
                     choices=suggest_deadline()),
        inquirer.Text('custom_deadline',
                     message="Enter custom deadline (YYYY-MM-DD HH:MM)",
                     validate=validate_date,
                     ignore=lambda x: not x['deadline_option'].startswith("Custom")),
        inquirer.List('priority',
                     message="Priority level",
                     choices=['1 [Low]', '2 [Medium]', '3 [High]', '4 [Critical]'],
                     default='2 [Medium]'),
        inquirer.List('effort',
                     message="Estimated effort",
                     choices=['Short [15-30min]', 'Medium [30min-1hr]', 'Long [>1hr]'],
                     default='Medium [30min-1hr]'),
        inquirer.List('difficulty',
                     message="Task difficulty",
                     choices=['Easy', 'Medium', 'Hard'],
                     default='Medium'),
        inquirer.List('energy',
                     message="Energy required",
                     choices=['Low', 'Medium', 'High'],
                     default='Medium'),
        inquirer.List('mood',
                     message="Required mood",
                     choices=['any [*]', 'energetic [E]', 'focused [F]', 'creative [C]', 'relaxed [R]', 'tired [T]'],
                     default='any [*]')
    ]
    
    answers = inquirer.prompt(questions)
    if answers:
        # Process the deadline
        if answers['deadline_option'].startswith("Custom"):
            deadline = answers['custom_deadline']
        else:
            deadline = answers['deadline_option'].split('(')[1].rstrip(')')
            
        # Extract the mood and priority without the ASCII indicator
        mood = answers['mood'].split(' [')[0]
        priority = int(answers['priority'].split(' [')[0])
        
        task = Task(
            answers['title'],
            answers['description'],
            deadline,
            priority,
            mood
        )
        todo_manager = TodoManager()
        todo_manager.add_task(task)
        console.print("Task added successfully!", style="green")
        
        # Show the added task
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title")
        table.add_column("Description")
        table.add_column("Deadline")
        table.add_column("Priority")
        table.add_column("Mood")
        
        table.add_row(
            task.title,
            task.description,
            task.deadline,
            str(task.priority),
            task.get_mood_with_icon()
        )
        console.print("\nTask details:", style="bold blue")
        console.print(table)

@cli.command()
@click.option('--all', '-a', is_flag=True, help='Show all tasks including completed ones')
def list(all):
    """List tasks"""
    todo_manager = TodoManager()
    todo_manager.list_tasks(show_completed=all)

@cli.command()
@click.argument('title')
@click.argument('status', type=click.Choice(['Not Started', 'In Progress', 'Completed']))
def status(title, status):
    """Update a task's status"""
    todo_manager = TodoManager()
    todo_manager.update_task_status(title, status)
    console.print(f"Task '{title}' status updated to '{status}'!", style="green")

@cli.command()
def suggest():
    """Get a task suggestion based on current mood"""
    questions = [
        inquirer.List('current_mood',
                     message="How are you feeling right now?",
                     choices=['energetic [E]', 'focused [F]', 'creative [C]', 'relaxed [R]', 'tired [T]'],
                     default='focused [F]'),
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        return
        
    # Extract the mood without the ASCII indicator
    mood = answers['current_mood'].split(' [')[0]
    
    todo_manager = TodoManager()
    suggested_task = todo_manager.get_suggested_task(mood)
    
    if suggested_task:
        console.print("\nBased on your current mood and priorities, I suggest:", style="bold blue")
        if suggested_task.suggestion_reason:
            console.print(f"\nReason: {suggested_task.suggestion_reason}", style="bold green")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title")
        table.add_column("Description")
        table.add_column("Deadline")
        table.add_column("Priority")
        table.add_column("Effort")
        table.add_column("Energy")
        table.add_column("Status")
        
        priority_style = {
            1: "blue",
            2: "yellow",
            3: "red bold",
            4: "red bold reverse"
        }.get(suggested_task.priority, "white")

        table.add_row(
            suggested_task.title,
            suggested_task.description,
            suggested_task.deadline,
            Text(str(suggested_task.priority), style=priority_style),
            suggested_task.effort,
            suggested_task.energy_required,
            suggested_task.status
        )
        console.print(table)

        # Add feedback option
        if click.confirm("\nWas this suggestion helpful?", default=True):
            console.print("Thanks for your feedback!", style="green")
        else:
            console.print("I'll try to provide better suggestions next time.", style="yellow")
    else:
        console.print("No suitable tasks found for your current mood.", style="yellow")

@cli.command()
@click.argument('title')
def complete(title):
    """Mark a task as completed"""
    todo_manager = TodoManager()
    todo_manager.mark_completed(title)
    console.print(f"Task '{title}' marked as completed!", style="green")

if __name__ == '__main__':
    cli()
