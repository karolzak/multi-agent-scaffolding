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
            
             = await AgentRegistry.create_from_file(
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



        finally:
            # Cleanup: Delete the thread and agent
            for agent in concurrent_agents:
                await client.agents.delete_agent(agent.id)
            for file in [fin_statement_file]:
                await client.agents.files.delete(file.id)
            
            # Create specialized agents
            data_analyst = await self.create_data_analyst_agent()
            data_reviewer = await self.create_data_reviewer_agent()
            web_researcher = await self.create_web_researcher_agent()
            research_reviewer = await self.create_research_reviewer_agent()
            coordinator = await self.create_coordinator_agent()
            
            # Create group chat with built-in orchestration
            agents = [data_analyst, data_reviewer, web_researcher, research_reviewer, coordinator]
            group_chat = AgentGroupChat(
                agents=agents,
                selection_strategy=self._create_selection_strategy(),
                termination_strategy=self._create_termination_strategy(coordinator),
                max_rounds=20
            )
            
            # Initial message to start the workflow
            initial_message = f"""
            FINANCIAL ANALYSIS REQUEST:
            Company: {request.company_symbol}
            Sector: {request.sector}
            Date Range: {request.start_date.strftime('%Y-%m-%d')} to {request.end_date.strftime('%Y-%m-%d')}
            Required Metrics: {', '.join(request.metrics)}

            WORKFLOW PHASES:
            1. Data Analysis Team: Analyze financial data and review findings
            2. Research Team: Gather market intelligence and validate sources  
            3. Coordination: Synthesize results and ensure completeness

            Each team should work on their phase, with reviewers providing guidance.
            Coordinator will manage transitions and final compilation.
            """
            
            # Execute the group chat workflow
            messages = []
            chat_history = group_chat.create_chat_history()
            chat_history.add_user_message(initial_message)
            
            async for message in group_chat.invoke_stream(chat_history):
                messages.append(message)
                self.logger.info(f"[{message.name}]: {message.content}")
                
                # Check if workflow is complete
                if self._is_workflow_complete(message):
                    break
            
            return compile_results(messages, request.company_symbol)
        

if __name__ == "__main__":
    asyncio.run(main())