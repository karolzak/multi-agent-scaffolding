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
from semantic_kernel.contents import StreamingChatMessageContent, ChatMessageContent
from typing import List
# from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

# load .env variables
from dotenv import load_dotenv
load_dotenv()

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

def agent_response_callback(message: ChatMessageContent) -> None:
    print(f"**{message.name}**\n{message.content}")

async def main():
    """Main function to run the agents."""
    # 0. Initialize Agents
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        try:
            concurrent_agents = []
            kernel = Kernel()

            settings = AzureAIAgentSettings(model_deployment_name="gpt-4o")
            # Load all predefined agents
            
            orchestrator = await AgentRegistry.create_from_file(
                f"src/agents/declarative/financial_orchestrator.yaml",
                kernel=kernel,
                settings=settings,
                client=client,
            )
            print(f"✅ Initialized Orchestrator agent")    

            # Create the CSV file path for the sample
            pdf_file_path = os.path.join("data", "tesco", "tesco_ar25_interactive.pdf")
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
            
            market_intelligence = await AgentRegistry.create_from_file(
                f"src/agents/declarative/market_intelligence.yaml",
                kernel=kernel,
                settings=settings,
                client=client,
                extras={
                    "BingGroundingConnectionName": os.environ.get("BING_GROUNDING_CONNECTION_ID")  # Replace with your actual connection ID
                }
            )
            print(f"✅ Initialized Market Intelligence agent")
            
            market_intelligence_reviewer = await AgentRegistry.create_from_file(
                f"src/agents/declarative/market_intelligence_reviewer.yaml",
                kernel=kernel,
                settings=settings,
                client=client,
                # extras={
                #     "BingConnectionId": os.environ.get("BING_GROUNDING_CONNECTION_NAME")  # Replace with your actual connection ID
                # }
            )
            print(f"✅ Initialized Market Intelligence Reviewer agent")

            # Create group chat with built-in orchestration
            agents = [
                # orchestrator,
                financial_data_analyst,
                financial_data_analysis_reviewer,
                market_intelligence,
                market_intelligence_reviewer
            ]

            from semantic_kernel.agents import StandardMagenticManager
            from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

            chat_completion_service = AzureChatCompletion(
                deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"), 
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
            )
            manager = StandardMagenticManager(chat_completion_service=chat_completion_service)
            from semantic_kernel.agents import MagenticOrchestration

            magentic_orchestration = MagenticOrchestration(
                members=agents,
                manager=manager,
                agent_response_callback=agent_response_callback,
                streaming_agent_response_callback=streaming_agent_response_callback
            )

            # from semantic_kernel.agents import GroupChatOrchestration, RoundRobinGroupChatManager

            # group_chat_orchestration = GroupChatOrchestration(
            #     members=agents,
            #     manager=RoundRobinGroupChatManager(max_rounds=10),  # Odd number so writer gets the last word
            #     agent_response_callback=agent_response_callback,
            # )
            from semantic_kernel.agents.runtime import InProcessRuntime

            runtime = InProcessRuntime()
            runtime.start()

            # orchestration_result = await group_chat_orchestration.invoke(
            #     task="Start a workflow to create a financial analysis report for company: Tesco",
            #     runtime=runtime,
            # )

            orchestration_result = await magentic_orchestration.invoke(
                task=(
                    """
                    Help me to create financial analysis report for Tesco for year 2025.
                    Your responsibilities:
                    1. Coordinate data collection from various specialized agents:
                    2. Synthesize results from Financial Data Analyst, Financial Data Analysis Reviewer, Market Intelligence Agent, Market Intelligence Reviewer
                    3. Ensure all agents complete their tasks and integrate results effectively
                    4. Generate final comprehensive financial analysis reports
                    
                    When coordinating the workflow:
                    - Start with company information gathering
                    - Coordinate parallel execution of financial analysis and market intelligence gathering
                    - Ensure all agent results are properly integrated
                    - Generate clear, actionable credit application recommendations for the company you are analyzing
                    - Provide confidence levels for all assessments
                    - Handle any errors or exceptions gracefully, ensuring the workflow can recover and continue          
                    """
                ),
                runtime=runtime,
            )

            value = await orchestration_result.get()
            print(f"***** Final Result *****\n{value}")

            await runtime.stop_when_idle()

            # group_chat = AgentGroupChat(
            #     agents=agents,
            #     # selection_strategy=create_selection_strategy(),
            #     termination_strategy=TerminationStrategy(
            #         task_completion_condition="the coordinator has confirmed the workflow is complete",
            #         kernel=kernel,
            #         maximum_iterations=15,
            #     )
            #     # streaming_callback=streaming_agent_response_callback,
            #     # max_rounds=20
            # )
            
            # # Initial message to start the workflow
            # initial_message = f"""
            # FINANCIAL ANALYSIS REQUEST:
            # Company: Tesco

            # WORKFLOW PHASES:
            # 1. Data Analysis Team: Process and analyze financial data based on the financial statement document and review findings
            # 2. Market Intelligene Team: Gather market intelligence using web search, generate insights and validate sources  
            # 3. Coordination: Synthesize results and ensure completeness

            # Each team should work on their phase, with reviewers providing guidance.
            # Coordinator will manage transitions and final compilation.
            # """
            
            # # Execute the group chat workflow
            # messages = []
            # chat_history = kernel.create_chat_history()
            # # chat_history = group_chat.create_chat_history()
            # chat_history.add_user_message(initial_message)
            
            # async for message in group_chat.invoke_stream(chat_history,):
            #     messages.append(message)
            #     # self.logger.info(f"[{message.name}]: {message.content}")
            #     print(f"[{message.name}]: {message.content}")
                
            #     # Check if workflow is complete
            #     if self._is_workflow_complete(message):
            #         break
            # print("✅ Workflow completed successfully")
            # # return compile_results(messages, request.company_symbol)
        finally:
            await client.agents.files.delete(fin_statement_file.id)
            for agent in agents:
                await client.agents.delete_agent(agent.id)

if __name__ == "__main__":
    asyncio.run(main())