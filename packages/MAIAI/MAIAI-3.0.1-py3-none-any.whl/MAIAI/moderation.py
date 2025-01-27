from .agent import client  # Import the shared OpenAI client

def moderation_check(goal):
    """
    Checks the input goal content for any potentially inappropriate or flagged content using the OpenAI Moderation API.

    Args:
        goal (str): The goal or input content that needs to be checked for moderation compliance.

    Raises:
        Exception: If the content is flagged by the moderation system, an exception is raised with an error message.

    Returns:
        None
    """
    response = client.moderations.create(
        model="omni-moderation-latest",
        input=goal,
    )

    # Check if the content is flagged by moderation system
    if response.results[0].flagged:
        raise Exception("The content has been flagged by the moderation system. Task execution aborted.")
