"""
Multi-Agent Financial Analysis Workflow

Real-time orchestration of Azure AI agents for comprehensive financial analysis.
"""

import asyncio
from pathlib import Path
from typing import Any

from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AgentRegistry, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.kernel import Kernel

from src.common.data_manager import FinancialDataManager, create_financial_data_summary


class FinancialAnalysisWorkflow:
    """Real-time multi-agent financial analysis orchestrator."""
    
    def __init__(self, data_root: str = "data"):
        self.data_manager = FinancialDataManager(data_root)
        self.agents: dict[str, AzureAIAgent] = {}
        self.client = None
        
    async def __aenter__(self):
        """Initialize agents and resources."""
        await self._initialize_agents()
        return self
        
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Cleanup resources."""
        if self.client:
            await self.client.__aexit__(None, None, None)
    
    async def _initialize_agents(self) -> None:
        """Initialize all predefined agents with Azure AI Foundry."""
        try:
            settings = AzureAIAgentSettings(model_deployment_name="gpt-4o")
            credential = DefaultAzureCredential()
            self.client = await AzureAIAgent.create_client(credential=credential).__aenter__()
            kernel = Kernel()
            
            # Load all predefined agents
            agent_files = [
                "financial_orchestrator.yaml",
                "financial_data_analyst.yaml", 
                "market_intelligence.yaml",
                "research_analyst.yaml"
            ]
            
            for agent_file in agent_files:
                agent_name = agent_file.replace(".yaml", "")
                self.agents[agent_name] = await AgentRegistry.create_from_file(
                    f"src/agents/declarative/{agent_file}",
                    kernel=kernel,
                    settings=settings,
                    client=self.client
                )
            
            print(f"✅ Initialized {len(self.agents)} Azure AI agents")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize agents: {e}")
    
    async def analyze_company(self, company_name: str, ticker: str | None = None) -> dict[str, Any]:
        """
        Perform comprehensive financial analysis using Azure AI agents.
        
        Args:
            company_name: Company to analyze
            ticker: Optional ticker symbol
            
        Returns:
            Analysis results from agent orchestration
        """
        print(f"🚀 Starting multi-agent analysis for {company_name}")
        
        # Discover available financial data
        dataset = self.data_manager.get_dataset(company_name)
        data_context = ""
        
        if dataset:
            data_summary = create_financial_data_summary(dataset)
            print(f"📁 Found local data: {len(dataset.pdf_files)} PDFs, {len(dataset.excel_files)} Excel files")
            
            data_context = f"""
            Available Financial Data:
            - Company: {dataset.company_name}
            - PDF Reports: {[Path(p).name for p in data_summary['files']['pdfs']]}
            - Excel Files: {[Path(p).name for p in data_summary['files']['excel']]}
            - Years Covered: {data_summary['available_years']}
            - Data Directory: {data_summary['data_directory']}
            """
        else:
            print(f"⚠️ No local data found for {company_name} - using public information")
            data_context = f"No local financial data available for {company_name}. Analyze using public information and web search."
        
        # Execute agent-based analysis
        return await self._orchestrate_analysis(company_name, ticker, data_context)
    
    async def _orchestrate_analysis(self, company_name: str, ticker: str | None, data_context: str) -> dict[str, Any]:
        """Orchestrate the analysis using Azure AI agents."""
        try:
            # Use financial orchestrator as the main coordinator
            orchestrator = self.agents["financial_orchestrator"]
            
            query = f"""
            Please coordinate a comprehensive financial analysis for {company_name} {f"(ticker: {ticker})" if ticker else ""}.
            
            {data_context}
            
            Please orchestrate the following analysis:
            1. Financial data analysis (use available documents if provided)
            2. Market intelligence gathering using web search
            3. Research insights and investment recommendations
            4. Risk assessment and ESG evaluation
            
            Coordinate with other specialized agents as needed and provide a comprehensive investment report.
            """
            
            print(f"🤖 Orchestrating analysis with Azure AI agents...")
            
            response_text = ""
            thread = None
            
            async for response in orchestrator.invoke(messages=query, thread=thread):
                response_text += str(response) + "\n"
                thread = response.thread
            
            print(f"✅ Agent orchestration completed")
            
            return {
                "company_name": company_name,
                "ticker": ticker,
                "analysis_date": "2025-06-30",
                "orchestrator_report": response_text,
                "analysis_method": "Azure AI Agent Orchestration",
                "agents_used": list(self.agents.keys()),
                "data_sources_available": "local data" in data_context.lower()
            }
            
        except Exception as e:
            print(f"❌ Agent orchestration failed: {e}")
            raise RuntimeError(f"Financial analysis failed: {e}")


async def analyze_company_financial_data(company_name: str, ticker: str | None = None, data_root: str = "data") -> dict[str, Any]:
    """
    Entry point for multi-agent financial analysis.
    
    Args:
        company_name: Company to analyze
        ticker: Optional ticker symbol
        data_root: Root directory for financial data
        
    Returns:
        Comprehensive financial analysis results
    """
    async with FinancialAnalysisWorkflow(data_root) as workflow:
        return await workflow.analyze_company(company_name, ticker)


async def main():
    """Main execution for direct script usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python financial_analysis.py <company_name> [ticker]")
        print("Example: python financial_analysis.py 'Microsoft Corporation' MSFT")
        return
    
    company_name = sys.argv[1]
    ticker = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = await analyze_company_financial_data(company_name, ticker)
        print(f"\n✅ Analysis completed for {result['company_name']}")
        print(f"🤖 Agents used: {result['agents_used']}")
        print(f"� Analysis method: {result['analysis_method']}")
        print(f"📁 Local data available: {result['data_sources_available']}")
        print(f"\n📋 Orchestrator Report:")
        print("-" * 60)
        print(result['orchestrator_report'])
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        print("💡 Ensure Azure AI Foundry is properly configured with:")
        print("   - Azure OpenAI deployment (gpt-4o)")
        print("   - Proper authentication (Azure CLI or environment variables)")
        print("   - Web search enabled in Azure AI Foundry")


if __name__ == "__main__":
    asyncio.run(main())
