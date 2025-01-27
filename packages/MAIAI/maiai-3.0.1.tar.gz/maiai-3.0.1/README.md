# MAIAI (Multi-Agentic Instructor AI)

This package provides tools to make building workflows with GPT models simple and efficient.

## Installation

You can install this package using pip:

```bash
pip install MAIAI
```

## Components

This package contains two main components: `Agent`, `Task`.

## Agent

The `Agent` class is defined in the `MAIAI` module. An `Agent` represents an AI model that can perform tasks. It has the following attributes:

- `model`: The name of the AI model.
- `temperature`: The temperature parameter for the AI model, which controls the randomness of the model's output.
- `role`: The role or purpose of the AI agent, which can guide its responses.

## Task

The `Task` class represents a task that an `Agent` can perform. It has the following attributes:

- `agent`: The `Agent` that will perform the task.
- `goal`: The goal or prompt for the task.
- `expected_output`: The expected format or type of output (optional).
- `retries`: The number of attempts to complete the task in case of failure (default is 3).
- `validate`: A validation function to check the output's correctness (optional).

### Task Methods

1. **`execute`**: 
   - Executes the main message of the task, optionally formatting the response as JSON.
   - Returns the output of the task execution, in JSON format if `response_type` is "json", else as text.
   - Includes retries and enhanced response handling.

2. **`chat`**:
   - Processes a chat session by formatting the chat history, appending system and user messages, and sending it to an API for a response.
   - Supports retries and handles errors.

3. **`retry`**:
   - Allows for automatic retries when performing a task if an error occurs.
   - Attempts the specified number of retries before returning a failure message.

4. **`read_image`**:
   - Processes an image by encoding it to base64 and sends it to the API for processing.
   - Can return the extracted content as text or JSON, depending on the `json` argument.

## Moderation Check

The `moderation_check` function is a standalone function that checks the content of the `goal` for compliance using the OpenAI Moderation API. If the content is flagged, an exception is raised, preventing the task from executing.

## Usage

Here's a basic example of how to use these classes:

```python
from MAIAI import Agent, Task

# Create an agent
agent = Agent(model="gpt-4o-mini", temperature=0.5, role="Translate text from English to French.")

# Create a task with a goal
task = Task(agent=agent, goal="Hello world!", expected_output="French Sentence")

# Execute the task
output = task.execute()
print("Output:", output)
```

### Using Additional Features

1. **Chat Functionality**:
   - Example to utilize the `chat` method with a session history:

    ```python
    chat_history = [("Hello", "Hi, how can I help you?"), ("What's your name?", "I am MAIAI.")]
    task = Task(agent=agent, goal="What's the weather today?")
    output = task.chat(chat_history)
    print("Chat Output:", output)
    ```

2. **Retry Mechanism**:
   - Example to test the retry functionality with a function that may fail:

    ```python
    # Initialize an agent
    agent = Agent(model="gpt-4o-mini", temperature=0.5, role="Retry Test Agent")

    # Define a goal for the task
    goal = "Give me your favorite line."

    # Create a validation function that checks if "MAIAI" is in the output
    def contains_maiai(output):
        return "MAIAI" in output

    # Create a Task instance with the validation function
    task = Task(agent=agent, goal=goal, retries=3, validate=contains_maiai)

    # Execute the task with retry if "MAIAI" is not in the response
    output = task.execute()
    print("Retry Test Output:", output)
    ```

3. **Reading Images**:
   - Use the `read_image` method to process an image file:

    ```python
    image_path = "path/to/image.png"
    image_task = Task(agent=agent, goal="Extract text from this image.")

    # Get the response as text or JSON
    output = image_task.read_image(image_path, json=False)
    print("Image Output:", output)
    ```

## Summary

With MAIAI, you have a flexible and reliable way to interact with GPT models, providing tools for moderation, retries, and even image processing. The `Task` and `Agent` classes allow building robust Multi-Model Agentic Architectures with simple setups, enhancing productivity in AI-driven workflows.
