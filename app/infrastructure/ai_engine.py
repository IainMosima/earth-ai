import logging
import os
from typing import Union

import httpx
from langgraph_sdk import get_client

from app.requests import AIRequest, AerialResultOutput
from app.requests.ai import AIResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai-engine")


class AIService:
    client = get_client(
        url=os.environ.get("LANGGRAPH_URL", "http://localhost:8123"),
        api_key=os.environ.get("LANGGRAPH_API_KEY")
    )

    @classmethod
    async def get_default_assistant(cls):
        assistants = await cls.client.assistants.search(
            metadata=None,
            offset=0,
            limit=1
        )
        return assistants[0]

    @classmethod
    async def create_thread(cls):
        try:
            return await cls.client.threads.create()
        except Exception as error:
            print(f"Error creating thread: {error}")
            raise error

    @classmethod
    async def list_runs(cls, thread_id: str):
        try:
            return await cls.client.runs.list(thread_id)
        except Exception as error:
            print(f"Error listing runs: {error}")
            raise error

    @classmethod
    async def get_complete_response(cls, thread_id: str, message: str) -> AIResponse:
        """
        Get a complete response from the assistant without streaming.
        Waits for the full response before returning.
        """
        try:
            assistant = await cls.get_default_assistant()

            # Check if the thread has any active runs
            runs = await cls.list_runs(thread_id)
            active_runs = [run for run in runs if run["status"] in ["queued", "in_progress"]]

            if active_runs:
                # Wait for active runs to complete or consider creating a new thread
                logging.warning(f"Thread {thread_id} has active runs. Creating a new thread.")
                thread = await cls.create_thread()
                thread_id = thread["thread_id"]

            # Create a run and wait for it to complete
            run = await cls.client.runs.create(
                thread_id,
                assistant["assistant_id"],
                input=dict(content=message)
            )

            # Wait for the run to complete
            run = await cls.client.runs.wait(thread_id, run["run_id"])
            print("Completed run:", run)
            return run

            # Rest of your existing code...
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 409:
                logging.error(
                    "Thread is already running. Try creating a new thread or wait for current run to complete.")
            raise error
        except Exception as error:
            logging.error(f"Error getting complete response: {error}")
            raise error

    @classmethod
    async def send_message(cls, message: AIRequest) -> Union[AerialResultOutput, str]:
        """
        Create a new thread and send a message, returning the complete response.
        """
        try:
            thread = await cls.create_thread()
            chat_message = await cls.get_complete_response(thread["thread_id"], message.json())

            if cls.is_thread_busy(thread["thread_id"]):
                return "Thread is busy. Please try again later."
            else:
                # Convert the chat message to AerialResultOutput
                return AerialResultOutput(
                    content=chat_message.text,  # Assuming text is the content of the response
                    additional_kwargs={},  # You may populate this based on the response
                    response_metadata={},  # Similar for this field if needed
                    type="ai",  # Or another value depending on your logic
                    name=chat_message.text,  # Set name as the content or another identifier
                    id=thread.thread_id,  # Generate or extract an ID as needed
                    example=False,  # Set as needed
                    tool_calls=[],  # Populate this if necessary
                    invalid_tool_calls=[],  # Populate if necessary
                    usage_metadata=None  # Set this as per your logic
                )
        except Exception as error:
            print(f"Error sending message: {error}")
            raise error

    @classmethod
    async def is_thread_busy(cls, thread_id: str) -> bool:
        try:
            # Get all runs for the thread
            runs = await cls.list_runs(thread_id)

            # Check if any runs are in active states (queued, in_progress)
            active_states = ["queued", "in_progress", "requires_action"]
            active_runs = [run for run in runs if run.get("status") in active_states]

            return len(active_runs) > 0
        except Exception as error:
            # Log the error but don't raise it - return True as a safety measure
            # This way, if we can't check status, we assume it might be busy
            logger.error(f"Error checking thread status: {error}")
            return True


# Example usage with your test data
test_data = {
    "user_id": "xyz",
    "aerial_key": "20180627_seq_50m_NC.tif",
    "ground_key": "Maize.jpg"
}


class AIInputData:
    pass



# Example of how to use with send_message (assuming it's from ai_engine.py)
async def test_send_message():
    # Initialize AI service
    ai_service = AIService()

    # Create a message using the test data
    message = AIRequest(
        user_id= "xyz",
        aerial_key= "20180627_seq_50m_NC.tif",
        ground_key= "Maize.jpg"
    )

    # Send the message and get response
    response = await ai_service.send_message(
        message=message
    )

    print("Response received from ai:", response)
    return response