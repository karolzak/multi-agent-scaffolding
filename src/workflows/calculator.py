import asyncio
from typing import Annotated

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AgentRegistry, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.kernel import Kernel
from src.tools.calculator import CalculatorPlugin

"""
The following sample demonstrates how to create an Azure AI agent that can serve user as a calculator
using a custom implementation of Semantic Kernel Plugin. The agent is created using a yaml declarative spec.
The agent can perform basic arithmetic operations like addition and multiplication.
"""

# Simulate a conversation with the agent
USER_INPUTS = [
    "Hello",
    "I want to add two numbers, 453 and 789.",
    "Now, multiply the result by 3",
    "Thank you",
]


async def main() -> None:
    settings = AzureAIAgentSettings()
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 1. Create a Kernel instance
        # For declarative agents, the kernel is required to resolve the plugin(s)
        kernel = Kernel()
        kernel.add_plugin(CalculatorPlugin())

        # 2. Create a Semantic Kernel agent for the Azure AI agent
        agent: AzureAIAgent = await AgentRegistry.create_from_file(
            "src/agents/declarative/calculator.yaml",
            kernel=kernel,
            settings=settings,
            client=client,
        )

        # 3. Create a thread for the agent
        # If no thread is provided, a new thread will be
        # created and returned with the initial response
        thread = None

        try:
            for user_input in USER_INPUTS:
                print(f"# User: {user_input}")
                # 4. Invoke the agent for the specified thread for response
                async for response in agent.invoke(
                    messages=user_input,
                    thread=thread,
                ):
                    print(f"# {response.name}: {response}")
                    thread = response.thread
        finally:
            # 5. Cleanup: Delete the thread and agent
            await thread.delete() if thread else None
            # await client.agents.delete_agent(agent.id)


if __name__ == "__main__":
    asyncio.run(main())
