"""Financial report plugin for Semantic Kernel with mocked data."""

from semantic_kernel.functions import kernel_function
from typing import Annotated
from datetime import datetime
import json


class FinancialReportPlugin:
    """Plugin for retrieving financial report data (mocked)."""

    @kernel_function(
        name="get_financial_report",
        description="Retrieve financial report data for a company"
    )
    def get_financial_report(
        self,
        symbol: Annotated[str, "Stock symbol (e.g., AAPL, MSFT)"]
    ) -> str:
        """
        Get financial report data for a specified company.
        
        Args:
            symbol: Company stock symbol
            
        Returns:
            JSON string containing financial report data
        """
        # Mock financial data - same for all companies for demonstration
        mock_data = {
            "company": {
                "symbol": symbol.upper(),
                "name": self._get_company_name(symbol),
                "sector": "Technology",
                "market_cap": "2.8T"
            },
            "report_period": "Q4 2023",
            "generated_at": datetime.now().isoformat(),
            "financials": {
                "revenue": {
                    "current_quarter": 119.58,
                    "previous_quarter": 117.15,
                    "currency": "USD",
                    "unit": "billions"
                },
                "net_income": {
                    "current_quarter": 33.92,
                    "previous_quarter": 29.96,
                    "currency": "USD",
                    "unit": "billions"
                },
                "earnings_per_share": {
                    "current_quarter": 2.18,
                    "previous_quarter": 1.88,
                    "currency": "USD"
                },
                "gross_margin": {
                    "current_quarter": 45.96,
                    "previous_quarter": 43.31,
                    "unit": "percentage"
                }
            },
            "key_metrics": {
                "revenue_growth": "2.1%",
                "profit_margin": "28.4%",
                "return_on_equity": "147.25%",
                "debt_to_equity": 1.73
            },
            "summary": f"Strong financial performance with steady revenue growth. {symbol.upper()} continues to demonstrate robust profitability and market leadership."
        }
        
        # Return more detailed quarterly breakdown
        mock_data["quarterly_breakdown"] = {
            "q1_2023": {"revenue": 94.84, "net_income": 24.16},
            "q2_2023": {"revenue": 81.80, "net_income": 19.88},
            "q3_2023": {"revenue": 89.50, "net_income": 22.96},
            "q4_2023": {"revenue": 119.58, "net_income": 33.92}
        }
        
        # Return annual summary
        mock_data["annual_summary"] = {
            "total_revenue": 385.72,
            "total_net_income": 100.92,
            "annual_growth": "2.8%",
            "dividend_yield": "0.88%"
        }
        
        return json.dumps(mock_data, indent=2)
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name for given symbol (mocked)."""
        company_names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla, Inc.",
            "META": "Meta Platforms, Inc.",
            "NVDA": "NVIDIA Corporation"
        }
        return company_names.get(symbol.upper(), f"{symbol.upper()} Corporation")