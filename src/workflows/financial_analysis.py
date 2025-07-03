# Copyright (c) Microsoft. All rights reserved.

import os
import asyncio
import datetime

from azure.ai.agents.models import FilePurpose
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import (
    AgentRegistry, AzureAIAgent, AzureAIAgentSettings,
    StandardMagenticManager, MagenticOrchestration, Agent
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents import StreamingChatMessageContent, ChatMessageContent

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

async def get_agents(kernel: Kernel, settings: AzureAIAgentSettings, client: object) -> list[Agent]:
    """Create and return all agents for the financial analysis workflow.
    
    Args:
        kernel: The semantic kernel instance
        settings: Azure AI Agent settings
        client: Azure AI Agent client
        fin_statement_file_id: File ID of the uploaded financial statement
        
    Returns:
        list: List of initialized agents
    """

    # Create the CSV file path for the sample
    pdf_file_path = os.path.join("data", "tesco", "tesco_ar25_interactive.pdf")
    fin_statement_file = await client.agents.files.upload_and_poll(
        file_path=pdf_file_path,
        purpose=FilePurpose.AGENTS,
        filename="tesco_ar25_interactive.pdf"
    )
    # Initialize Financial Data Analyst
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
    
    # Initialize Financial Data Analysis Reviewer
    financial_data_analysis_reviewer = await AgentRegistry.create_from_file(
        f"src/agents/declarative/financial_data_analysis_reviewer.yaml",
        kernel=kernel,
        settings=settings,
        client=client,
    )
    print(f"✅ Initialized Financial Data Analysis Reviewer agent")
    
    # Initialize Market Intelligence Agent
    market_intelligence = await AgentRegistry.create_from_file(
        f"src/agents/declarative/market_intelligence.yaml",
        kernel=kernel,
        settings=settings,
        client=client,
        extras={
            "BingGroundingConnectionName": os.environ.get("BING_GROUNDING_CONNECTION_ID")
        }
    )
    print(f"✅ Initialized Market Intelligence agent")
    
    # Initialize Market Intelligence Reviewer
    market_intelligence_reviewer = await AgentRegistry.create_from_file(
        f"src/agents/declarative/market_intelligence_reviewer.yaml",
        kernel=kernel,
        settings=settings,
        client=client,
    )
    print(f"✅ Initialized Market Intelligence Reviewer agent")

    return [
        financial_data_analyst,
        financial_data_analysis_reviewer,
        market_intelligence,
        market_intelligence_reviewer
    ]

async def main():
    """Main function to run the agents."""
    fin_statement_file = None
    agents = []
    
    # 0. Initialize Agents
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        try:
            kernel = Kernel()

            settings = AzureAIAgentSettings(
                model_deployment_name=os.environ.get("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME", ""))
            # Load all predefined agents
            agents = await get_agents(kernel, settings, client)

            # Create group chat with built-in orchestration
            chat_completion_service = AzureChatCompletion(
                deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"), 
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
            )
            manager = StandardMagenticManager(chat_completion_service=chat_completion_service)

            magentic_orchestration = MagenticOrchestration(
                members=agents,
                manager=manager,
                agent_response_callback=agent_response_callback,
                streaming_agent_response_callback=streaming_agent_response_callback
            )

            runtime = InProcessRuntime()
            runtime.start()

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

            print("✅ Workflow completed successfully")

            # dump final results to a file under outputs/datetime/financial_analysis_report.md
            output_dir = os.path.join("outputs", datetime.datetime.now().strftime("%Y%m%d_%H%M"))
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, "financial_analysis_report.md")
            with open(output_file_path, "w") as f:
                f.write(f"Financial Analysis Report for Tesco\n")
                f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("### Analysis Results:\n")
                f.write(str(value))
                print(f"✅ Report saved to {output_file_path}")
            
            # Stop the runtime when done
            await runtime.stop_when_idle()

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            raise

        finally:
            if fin_statement_file is not None:
                await client.agents.files.delete(fin_statement_file.id)
            for agent in agents:
                await client.agents.delete_agent(agent.id)

if __name__ == "__main__":
    asyncio.run(main())