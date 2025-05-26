# Smart Todo List

A sophisticated command-line todo list application that intelligently suggests tasks based on deadlines, priorities, and your current mood. Uses AI-powered suggestions with Google's Gemini API to help you work more effectively.

## Features

- [*] Smart task suggestions based on your current mood and task urgency
- [T] Deadline-aware task management with flexible scheduling
- [+] Beautiful command-line interface with rich color-coded formatting
- [A] AI-powered task prioritization using Google's Gemini API
- [M] Multiple mood contexts for different types of work
- [x] Comprehensive task tracking with status management
- [E] Energy and effort-based task classification
- [F] User feedback loop for improving suggestions

## Task Attributes

### Priority Levels
- Low (Blue): Regular tasks without urgency
- Medium (Yellow): Important but not critical
- High (Red): Urgent tasks requiring attention
- Critical (Red, highlighted): Highest priority tasks

### Effort Levels
- Short: 15-30 minutes
- Medium: 30 minutes to 1 hour
- Long: Over 1 hour

### Task Status
- Not Started (Yellow)
- In Progress (Blue)
- Completed (Green)

## Mood Types and Their Best Use Cases

The application supports different mood contexts to match tasks with your current state:

- [E] energetic: Physical tasks, brainstorming sessions, meetings
- [F] focused: Complex problem-solving, coding, writing
- [C] creative: Design work, content creation, planning
- [R] relaxed: Administrative tasks, email, light reading
- [T] tired: Simple, low-energy tasks
- [*] any: Tasks that can be done in any mood

Tasks can be assigned to specific moods or marked as "any" for flexibility.

## Prerequisites

- Python 3.6 or higher
- Google Gemini API key (for smart suggestions)

## Installation

There are two ways to install and use this tool:

### Method 1: Direct Script Access (Recommended for Development)

This method is ideal if you're working on the code or want to run it directly from the source.
First, clone and navigate to the repository:

```bash
git clone <your-repo-url>
cd smart-todo
```

For macOS (zsh):
```zsh
# Add these lines to your ~/.zshrc
TODO_DIR=$(pwd)
echo "export TODO_CMD=\"python3 $TODO_DIR/smart_todo/cli.py\"" >> ~/.zshrc
echo "alias todo=\"\$TODO_CMD\"" >> ~/.zshrc
echo "export GEMINI_API_KEY=\"your-api-key-here\"" >> ~/.zshrc

# Then reload your shell configuration
source ~/.zshrc
```

For Linux (bash):
```bash
# Add these lines to your ~/.bashrc
TODO_DIR=$(pwd)
echo "export TODO_CMD=\"python3 $TODO_DIR/smart_todo/cli.py\"" >> ~/.bashrc
echo "alias todo=\"\$TODO_CMD\"" >> ~/.bashrc
echo "export GEMINI_API_KEY=\"your-api-key-here\"" >> ~/.bashrc

# Then reload your shell configuration
source ~/.bashrc
```

Note: Make sure to run these commands from the root directory of the project. The commands will automatically use the correct path regardless of where you installed the project.

### Method 2: Global Installation (Recommended for Regular Use)

This method installs the tool system-wide using pip:

1. Install the package globally:
```bash
pip install .
```

2. Set up your environment:

For macOS (zsh):
```zsh
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc
source ~/.zshrc
```

For Linux (bash):
```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

Note: After installation, you may need to restart your terminal for the `todo` command to be available.

## Usage

### Adding Tasks
Simply run:
```bash
todo add
```
This will start an interactive prompt asking for:
- Task title
- Description
- Deadline (YYYY-MM-DD HH:MM) with quick options for today/tomorrow/next week
- Priority level [1-4]
- Required mood [*]/[E]/[F]/[C]/[R]/[T]
- Effort estimation (Short/Medium/Long)
- Task difficulty (Easy/Medium/Hard)
- Energy requirement (Low/Medium/High)

### Managing Tasks
Show incomplete tasks:
```bash
todo list
```

Show all tasks including completed:
```bash
todo list --all
```

Update task status:
```bash
todo status "Task Name" "In Progress"
```

Mark task as complete:
```bash
todo complete "Task Name"
```

### Getting Smart Suggestions
Get AI-powered task suggestions based on your current mood:
```bash
todo suggest
```

The suggestion algorithm considers:
1. Task urgency (deadline proximity)
2. Energy/difficulty match with current mood
3. Task priority level
4. Task complexity and effort
5. Current task status

You can provide feedback on suggestions to help improve future recommendations.

## Task Selection Algorithm

The application uses Google's Gemini API to make intelligent task suggestions based on:

1. **Time Management**
   - Deadline proximity
   - Current time of day
   - Estimated task duration

2. **Energy Matching**
   - User's current mood
   - Task's required energy level
   - Task difficulty

3. **Priority Handling**
   - Task importance
   - Urgency score calculation
   - Status consideration

4. **Adaptive Learning**
   - User feedback collection
   - Suggestion improvement over time

## Data Storage

Tasks are stored locally in a `tasks.json` file, making it easy to back up or version control your tasks. The JSON format includes all task attributes, status, and completion state.

## Error Handling

The application includes robust error handling:
- Deadline validation
- Priority range checks
- Fallback suggestion mechanisms when AI is unavailable
- Invalid status transition prevention

## Contributing

Feel free to open issues or submit pull requests at [github.com/yourusername/smart-todo](https://github.com/yourusername/smart-todo)

## Best Practices

1. **Task Creation**
   - Set realistic deadlines
   - Be specific in task descriptions
   - Accurately estimate effort levels
   - Choose appropriate mood requirements

2. **Task Management**
   - Update task status regularly
   - Provide suggestion feedback
   - Review and adjust priorities as needed
   - Break down long tasks into smaller ones
