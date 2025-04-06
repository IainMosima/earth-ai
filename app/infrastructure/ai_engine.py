import logging
import os

import httpx
from langgraph_sdk import get_client

from app.requests import AIRequest
from app.requests.ai import AIResponse, AerialResult

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai-engine")


class AIEngine:
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
    async def send_and_get_id(cls, thread_id: str, message) -> str:
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

            await cls.client.runs.create(
                thread_id,
                assistant["assistant_id"],
                input=message
            )

            return thread_id

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
    async def send_message(cls, message: AIRequest) -> str:
        """
        Create a new thread and send a message, returning the complete response.
        """
        try:
            thread = await cls.create_thread()
            sent_thread_id = await cls.send_and_get_id(thread["thread_id"], message)

            return sent_thread_id
        except Exception as error:
            print(f"Error sending message: {error}")
            raise error

    @classmethod
    async def get_thread_info(cls, thread_id: str):
        try:
            # Get the thread information
            thread_response = await cls.client.threads.get(thread_id)


            values = thread_response.get("values")

            # Extract aerial_result data
            aerial_result_input = values.get("aerial_result").get("input")

            aerial_result_output = values.get("aerial_result").get("output")


            # Combine the information into a single response
            thread_info = AIResponse(
            user_id=values.get("user_id"),
            aerial_result=AerialResult(
                input=aerial_result_input,
                output=aerial_result_output,
            ),
            carbon_credits=values.get("carbon_credits"),
            )

            return thread_info
        except Exception as error:
            logger.error(f"Error retrieving thread information: {error}")
            raise error

ai_engine = AIEngine()

# Example of how to use with send_message (assuming it's from ai_engine.py)
async def test_send_message():
    # Initialize AI service
    ai_service = AIEngine()

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

    print("new thread id from ai:", response)
    return response

async def check_thread_status(thread_id):
    ai_service = AIEngine()
    thread_info = await ai_service.get_thread_info(thread_id)
    print(thread_info)
    return thread_info