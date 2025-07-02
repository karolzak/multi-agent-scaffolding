# Copyright (c) Microsoft. All rights reserved.

import os
import asyncio

from azure.ai.agents.models import FilePurpose
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import (
    AgentRegistry, AzureAIAgent, AzureAIAgentSettings, ConcurrentOrchestration,
    AgentGroupChat
    # Agent, ChatCompletionAgent, 
)
from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents import StreamingChatMessageContent
# from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion


# Flag to indicate if a new message is being received
is_new_message = True

def streaming_agent_response_callback(message: StreamingChatMessageContent, is_final: bool) -> None:
    """Observer function to print the messages from the agents.

    Args:
        message (StreamingChatMessageContent): The streaming message content from the agent.
        is_final (bool): Indicates if this is the final part of the message.
    """
    global is_new_message
    if is_new_message:
        print(f"# {message.name}")
        is_new_message = False
    print(message.content, end="", flush=True)
    if is_final:
        print()
        is_new_message = True


from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel.agents.strategies import (
    KernelFunctionTerminationStrategy,
)
def create_termination_strategy(
    task_completion_condition: str,
    kernel: Kernel,
    maximum_iterations: int = 15,
) -> KernelFunctionTerminationStrategy:
    """
    Create a termination strategy for the task completion process.
    Args:
        task_completion_condition (str): The condition to determine if the task is complete.
        service_id (str): The ID of the service.
        maximum_iterations (int): The maximum number of iterations for the termination strategy.
    Returns:
        KernelFunctionTerminationStrategy: The created termination strategy.
    """

    termination_function = KernelFunctionFromPrompt(
        function_name="termination",
        prompt=f"""
        Determine if {task_completion_condition}. If so, respond with a single word: yes

        History:
        {{{{$history}}}}
        """,
    )

    termination_strategy = KernelFunctionTerminationStrategy(
        function=termination_function,
        kernel=kernel,
        result_parser=lambda result: str(result.value[0]).lower() == "yes", # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportUnknownLambdaType] As required by the Semantic Kernel SDK
        history_variable_name="history",
        maximum_iterations=maximum_iterations,
    )

    return termination_strategy

async def main():
    """Main function to run the agents."""
    # 0. Initialize Agents
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        runtime = InProcessRuntime()
        try:
            concurrent_agents = []
            kernel = Kernel()
            # Create the CSV file path for the sample
            pdf_file_path = os.path.join("data", "tesco", "tesco_ar25_interactive.pdf")

            settings = AzureAIAgentSettings(model_deployment_name="gpt-4o")
            # Load all predefined agents            
            fin_statement_file = await client.agents.files.upload_and_poll(
                file_path=pdf_file_path,
                purpose=FilePurpose.AGENTS,
                filename="tesco_ar25_interactive.pdf"
            )
            
            financial_data_analyst = await AgentRegistry.create_from_file(
                f"src/agents/declarative/financial_data_analyst.yaml",
                kernel=kernel,
                settings=settings,
                client=client,
                extras={
                    "statement": fin_statement_file.id
                }
            )
            print(f"✅ Initialized Financial Data Analyst agent")
            
            financial_data_analysis_reviewer = await AgentRegistry.create_from_file(
                f"src/agents/declarative/financial_data_analysis_reviewer.yaml",
                kernel=kernel,
                settings=settings,
                client=client,
            )
            print(f"✅ Initialized Financial Data Analysis Reviewer agent")
            
            # web_search_agent = await AgentRegistry.create_from_file(
            #     f"src/agents/declarative/web_search.yaml",
            #     kernel=kernel,
            #     settings=settings,
            #     client=client,
            #     # extras={"BingConnectionId": "your-bing-connection-id"}  # Replace with your actual connection ID
            # )
            # print(f"✅ Initialized Web Search Agent")

            group_chat = AgentGroupChat(
                agents=[financial_data_analyst, financial_data_analysis_reviewer],
                termination_strategy=create_termination_strategy(
                    task_completion_condition="the reviewer has concluded the financial analysis is complete",
                    kernel=kernel,
                    maximum_iterations=15,
                )
            )

            # 1. Create a concurrent orchestration with multiple agents
            concurrent_agents = [
                # financial_data_analyst,
                group_chat
                # web_search_agent,
                # Add more agents as needed
            ]
            concurrent_orchestration = ConcurrentOrchestration(
                members=concurrent_agents,
                streaming_agent_response_callback=streaming_agent_response_callback
            )

            # 2. Create a runtime and start it
            runtime.start()

            # 3. Invoke the orchestration with a task and the runtime
            orchestration_result = await concurrent_orchestration.invoke(
                task="Perform financial analysis of the company 'Tesco'",
                runtime=runtime,
            )
            
            # 4. Wait for the results
            # Note: the order of the results is not guaranteed to be the same
            # as the order of the agents in the orchestration.
            value = await orchestration_result.get()
            for item in value:
                print(f"# {item.name}: {item.content}")
        
        finally:
            # Cleanup: Delete the thread and agent
            for agent in concurrent_agents:
                await client.agents.delete_agent(agent.id)
            for file in [fin_statement_file]:
                await client.agents.files.delete(file.id)

            # 5. Stop the runtime after the invocation is complete
            await runtime.stop_when_idle()
        

if __name__ == "__main__":
    asyncio.run(main())
