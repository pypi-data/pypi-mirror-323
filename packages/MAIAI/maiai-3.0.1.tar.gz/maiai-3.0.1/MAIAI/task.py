import json
import base64
from .agent import Agent, client
from .moderation import moderation_check

class Task:
    """
    A class representing a task to be executed by an AI agent. Supports messages with retries, validation, and 
    response handling (text or JSON). It includes image processing functionality where images are read and sent 
    for API processing.
    
    Attributes:
        agent (Agent): The agent used to execute the task.
        message (str): The primary message or objective of the task.
        expected_output (str): Expected format of the output (optional).
        retries (int): Number of retries allowed for task execution (default is 3).
        validate (function): A validation function to check output (optional).
    """

    def __init__(self, agent: Agent, message: str, expected_output: str = "", retries: int = 3, validate=None):
        """
        Initializes the Task with an agent, message, and optional parameters for output format, retries, and validation.

        Args:
            agent (Agent): The agent used to execute the task.
            message (str): The objective or message for the task.
            expected_output (str): Expected format of the task output (default is an empty string).
            retries (int): Number of retries allowed for execution (default is 3).
            validate (function): A function to validate the output; returns True if valid, False otherwise.
        """
        self.agent = agent
        self.message = message
        self.expected_output = expected_output
        self.retries = retries
        self.validate = validate

    def retry(self, function, *args, **kwargs):
        """
        Executes a function with retry logic, attempting up to the specified number of retries on failure.

        Args:
            function (callable): The function to execute with retries.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The output of the function if successful; a failure message after all retries.
        """
        attempt = 0
        output = None
        success = False

        while attempt < self.retries and not success:
            try:
                output = function(*args, **kwargs)
                if self.validate and not self.validate(output):
                    print(f"Attempt {attempt + 1} failed validation.")
                    attempt += 1
                    continue
                success = True
            except Exception as e:
                print(f"Attempt {attempt + 1} failed due to exception: {e}")
                attempt += 1

        if not success:
            output = "Unable to complete the operation after multiple attempts."
        return output

    def read_image(self, image_path, json=False, max_tokens=1000):
        """
        Reads an image, encodes it in base64, and sends it to the API. Supports JSON response format if specified.

        Args:
            image_path (str): The path to the image file.
            json (bool): Whether to return the response in JSON format (default is False).
            max_tokens (int): Maximum tokens for the API response (default is 1000).

        Returns:
            str or dict: The API response; JSON data if `json` is True, otherwise a string response.
        """
        moderation_check(self.message)  # Check moderation before making the API call

        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
            
        local_image_url = f"data:image/jpeg;base64,{encode_image(image_path)}"

        def process_image():
            if json:
                response = client.chat.completions.create(
                    model=self.agent.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"""{self.message}
                                Return JSON document with all text in the receipt. Only return JSON not other text."""},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": local_image_url,
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
                json_data = json.loads(response.choices[0].message.content)
                return json_data
            else:
                response = client.chat.completions.create(
                    model=self.agent.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"""{self.message}"""},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": local_image_url,
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
        
        return self.retry(process_image)

    def execute(self, response_type: str = None):
        """
        Executes the main message of the task, optionally formatting the response as JSON.

        Args:
            response_type (str): Type of response format; if 'json', the response is parsed as JSON (default is None).

        Returns:
            str or dict: The output of the task execution, in JSON format if `response_type` is "json", else as text.
        """
        moderation_check(self.message)  # Check moderation before making the API call
        
        def process_execution():
            try:
                completion = client.chat.completions.create(
                    model=self.agent.model,
                    temperature=self.agent.temperature,
                    messages=[
                        {"role": "developer", "content": f"{self.agent.role}"}, 
                        {"role": "user", "content": f"""{self.message}"""}
                    ]
                )
                return completion.choices[0].message.content
            except Exception as e:
                return f"An error occurred: {str(e)}"

        def process_formatted_execution():
            if response_type == "json":
                completion = client.chat.completions.create(
                    model=self.agent.model,
                    temperature=self.agent.temperature,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "developer", "content": f"""{self.agent.role}
You MUST give your response as json in the following format: {self.expected_output}"""}, 
                        {"role": "user", "content": f"""{self.message}"""}
                    ]
                )
                output = json.loads(completion.choices[0].message.content)
                return output
            else:
                completion = client.chat.completions.create(
                    model=self.agent.model,
                    temperature=self.agent.temperature,
                    messages=[
                        {"role": "developer", "content": f"""{self.agent.role}
You MUST give your response as {self.expected_output}"""}, 
                        {"role": "user", "content": f"""{self.message}"""}
                    ]
                )
                return completion.choices[0].message.content
        
        if self.expected_output == "" and response_type == None:
            return self.retry(process_execution)
        else:
            return self.retry(process_formatted_execution)
    
    def chat(self, chat_history):

            def process_chat():
                try:
                    # Reformat the history into the new required structure
                    message = []
                    for turn in chat_history:
                        if turn[0] is not None:
                            message.append({
                                "role": "user",
                                "content": turn[0]
                            })
                        if turn[1] is not None:
                            message.append({
                                "role": "assistant",
                                "content": turn[1]
                            })
                    
                    # Add the initial role and instruction as a system message
                    message.insert(0, {
                        "role": "developer",
                        "content": self.agent.role
                    })
                    
                    # Append the current user response at the end
                    message.append({
                        "role": "user",
                        "content": self.message
                    })
                    
                    print(message)

                    # Make the API call
                    completion = client.chat.completions.create(
                        model=self.agent.model,
                        temperature=self.agent.temperature,
                        messages=message
                    )
                    return completion.choices[0].message.content
                except Exception as e:
                    return f"An error occurred: {str(e)}"

            return self.retry(process_chat)
