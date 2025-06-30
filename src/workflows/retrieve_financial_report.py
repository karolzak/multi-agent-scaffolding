import asyncio

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AgentRegistry, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.kernel import Kernel
from src.tools.financial_report import FinancialReportPlugin 

"""
The following sample demonstrates how to create an Azure AI agent that retrieves financial reports
using a custom implementation of Semantic Kernel Plugin. The agent is created using a yaml declarative spec
and can retrieve financial reports based on user queries.
"""

# Simulate a conversation with the agent
USER_INPUTS = [
    "Hello",
    "I want to get the financial report data for Apple Inc.",
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
        # kernel = Kernel()
        # kernel.add_plugin(FinancialReportPlugin())

        # 2. Create a Semantic Kernel agent for the Azure AI agent
        agent: AzureAIAgent = await AgentRegistry.create_from_file(
            "src/agents/declarative/financial_report.yaml",
            # kernel=kernel,
            plugins=[FinancialReportPlugin()],
            settings=settings,
            client=client,
        )
        
        # # Create agent definition
        # agent_definition = await client.agents.create_agent(
        #     model=settings.model_deployment_name,
        #     name="FinancialReportAgent",
        #     instructions="You are a financial report agent. Use the provided tools to retrieve financial reports data for different companies based on the company code.",
        # )

        # # Create the AzureAI Agent using the defined client and agent definition
        # agent = AzureAIAgent(
        #     client=client,
        #     definition=agent_definition,
        #     plugins=[FinancialReportPlugin()],
        # )

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
            await client.agents.delete_agent(agent.id)


if __name__ == "__main__":
    asyncio.run(main())
