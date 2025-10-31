"""
LangGraph Multi-Agent Portfolio Optimizer for Target Capital
Coordinates 4 specialized agents for comprehensive portfolio analysis
"""

import os
import logging
from typing import Dict, List, TypedDict, Annotated
from datetime import datetime
import operator
import json

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from services.comprehensive_portfolio_service import ComprehensivePortfolioService

logger = logging.getLogger(__name__)


class PortfolioState(TypedDict):
    """State for the portfolio optimizer graph"""
    messages: Annotated[List, operator.add]
    user_id: int
    portfolio_data: Dict
    risk_analysis: Dict
    sector_analysis: Dict
    allocation_recommendations: Dict
    opportunities: List[Dict]
    final_report: str
    agent_outputs: Dict


class LangGraphPortfolioOptimizer:
    """
    Multi-agent portfolio optimizer with 4 specialized agents:
    
    1. Risk Analyzer Agent - Analyzes portfolio risk, volatility, diversification
    2. Sector Analyzer Agent - Evaluates sector allocation and concentration
    3. Asset Allocator Agent - Recommends optimal asset allocation
    4. Opportunity Finder Agent - Identifies investment opportunities based on preferences
    
    Coordinator orchestrates agents and synthesizes insights
    """
    
    def __init__(self):
        # Different LLM configurations for different agents
        api_key = os.environ.get("OPENAI_API_KEY", "")
        
        self.risk_llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,  # Conservative for risk analysis
            api_key=api_key
        )
        
        self.creative_llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,  # Creative for opportunities
            api_key=api_key
        )
        
        self.balanced_llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.4,  # Balanced for analysis
            api_key=api_key
        )
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the multi-agent coordination graph"""
        workflow = StateGraph(PortfolioState)
        
        # Add agent nodes
        workflow.add_node("fetch_portfolio", self.fetch_portfolio_data)
        workflow.add_node("risk_agent", self.risk_analyzer_agent)
        workflow.add_node("sector_agent", self.sector_analyzer_agent)
        workflow.add_node("allocation_agent", self.asset_allocator_agent)
        workflow.add_node("opportunity_agent", self.opportunity_finder_agent)
        workflow.add_node("coordinator", self.coordinator_agent)
        
        # Define the flow
        workflow.set_entry_point("fetch_portfolio")
        
        # Fetch portfolio first
        workflow.add_edge("fetch_portfolio", "risk_agent")
        
        # Run specialized agents in parallel (conceptually)
        workflow.add_edge("risk_agent", "sector_agent")
        workflow.add_edge("sector_agent", "allocation_agent")
        workflow.add_edge("allocation_agent", "opportunity_agent")
        
        # Coordinator synthesizes all agent outputs
        workflow.add_edge("opportunity_agent", "coordinator")
        workflow.add_edge("coordinator", END)
        
        return workflow.compile()
    
    def fetch_portfolio_data(self, state: PortfolioState) -> Dict:
        """Fetch comprehensive portfolio data"""
        logger.info("Fetching portfolio data")
        
        user_id = state["user_id"]
        
        try:
            # Get portfolio data from service
            portfolio_service = ComprehensivePortfolioService(user_id)
            portfolio_summary = portfolio_service.get_complete_portfolio_summary()
            
            return {
                "portfolio_data": portfolio_summary,
                "messages": [AIMessage(content="Portfolio data fetched successfully")],
                "agent_outputs": {}
            }
        except Exception as e:
            logger.error(f"Failed to fetch portfolio data: {e}")
            return {
                "portfolio_data": {},
                "messages": [AIMessage(content=f"Error fetching portfolio: {e}")],
                "agent_outputs": {}
            }
    
    def risk_analyzer_agent(self, state: PortfolioState) -> Dict:
        """Agent 1: Analyze portfolio risk and volatility"""
        logger.info("Risk Analyzer Agent running")
        
        portfolio = state.get("portfolio_data", {})
        
        system_prompt = """You are a Risk Analysis Specialist at Target Capital.
Analyze the portfolio and provide:
1. Overall risk score (1-10)
2. Volatility assessment
3. Diversification quality
4. Concentration risks
5. Risk-adjusted returns analysis
6. Specific risk mitigation recommendations

Be precise and quantitative. Output as structured JSON."""
        
        portfolio_summary = json.dumps(portfolio, indent=2)
        
        response = self.risk_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analyze this portfolio for risk:\n{portfolio_summary}")
        ])
        
        try:
            content = response.content if isinstance(response.content, str) else str(response.content)
            risk_analysis = json.loads(content)
        except:
            risk_analysis = {"raw_analysis": str(response.content)}
        
        return {
            "risk_analysis": risk_analysis,
            "messages": [AIMessage(content="Risk analysis completed")],
            "agent_outputs": {"risk_agent": risk_analysis}
        }
    
    def sector_analyzer_agent(self, state: PortfolioState) -> Dict:
        """Agent 2: Analyze sector allocation and concentration"""
        logger.info("Sector Analyzer Agent running")
        
        portfolio = state.get("portfolio_data", {})
        
        system_prompt = """You are a Sector Analysis Specialist at Target Capital.
Analyze the portfolio's sector allocation:
1. Current sector breakdown
2. Over/under-exposed sectors
3. Sector correlation analysis
4. Cyclical vs defensive balance
5. Sector-specific opportunities and risks
6. Rebalancing recommendations

Provide specific percentages and actionable insights. Output as JSON."""
        
        portfolio_summary = json.dumps(portfolio, indent=2)
        
        response = self.balanced_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analyze sector allocation:\n{portfolio_summary}")
        ])
        
        try:
            content = response.content if isinstance(response.content, str) else str(response.content)
            sector_analysis = json.loads(content)
        except:
            sector_analysis = {"raw_analysis": str(response.content)}
        
        return {
            "sector_analysis": sector_analysis,
            "messages": [AIMessage(content="Sector analysis completed")],
            "agent_outputs": {**state.get("agent_outputs", {}), "sector_agent": sector_analysis}
        }
    
    def asset_allocator_agent(self, state: PortfolioState) -> Dict:
        """Agent 3: Recommend optimal asset allocation"""
        logger.info("Asset Allocator Agent running")
        
        portfolio = state.get("portfolio_data", {})
        risk_analysis = state.get("risk_analysis", {})
        sector_analysis = state.get("sector_analysis", {})
        
        system_prompt = """You are an Asset Allocation Specialist at Target Capital.
Based on the portfolio and previous analysis, recommend:
1. Optimal asset class allocation (Equity, Debt, Gold, etc.)
2. Rebalancing strategy
3. Specific allocation percentages
4. Timeline for implementation
5. Expected impact on risk/return profile

Consider the user's risk profile. Output as JSON."""
        
        context = f"""Portfolio: {json.dumps(portfolio, indent=2)}
Risk Analysis: {json.dumps(risk_analysis, indent=2)}
Sector Analysis: {json.dumps(sector_analysis, indent=2)}"""
        
        response = self.balanced_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Recommend asset allocation:\n{context}")
        ])
        
        try:
            content = response.content if isinstance(response.content, str) else str(response.content)
            allocation_recs = json.loads(content)
        except:
            allocation_recs = {"raw_recommendations": str(response.content)}
        
        return {
            "allocation_recommendations": allocation_recs,
            "messages": [AIMessage(content="Allocation recommendations generated")],
            "agent_outputs": {**state.get("agent_outputs", {}), "allocation_agent": allocation_recs}
        }
    
    def opportunity_finder_agent(self, state: PortfolioState) -> Dict:
        """Agent 4: Identify investment opportunities"""
        logger.info("Opportunity Finder Agent running")
        
        portfolio = state.get("portfolio_data", {})
        allocation_recs = state.get("allocation_recommendations", {})
        
        system_prompt = """You are an Investment Opportunities Specialist at Target Capital.
Identify 5-10 specific investment opportunities:
1. Underrepresented quality stocks
2. Emerging sector plays
3. Value opportunities
4. Diversification additions
5. Dividend yielders for income

For each opportunity provide:
- Stock name and symbol
- Sector
- Rationale (2-3 sentences)
- Expected allocation (%)
- Risk level

Output as JSON array."""
        
        context = f"""Current Portfolio: {json.dumps(portfolio, indent=2)}
Allocation Gaps: {json.dumps(allocation_recs, indent=2)}"""
        
        response = self.creative_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Find investment opportunities:\n{context}")
        ])
        
        try:
            content = response.content if isinstance(response.content, str) else str(response.content)
            opportunities = json.loads(content)
            if not isinstance(opportunities, list):
                opportunities = [opportunities]
        except:
            opportunities = [{"raw_opportunities": str(response.content)}]
        
        return {
            "opportunities": opportunities,
            "messages": [AIMessage(content=f"Found {len(opportunities)} opportunities")],
            "agent_outputs": {**state.get("agent_outputs", {}), "opportunity_agent": opportunities}
        }
    
    def coordinator_agent(self, state: PortfolioState) -> Dict:
        """Coordinator: Synthesize all agent outputs into final report"""
        logger.info("Coordinator Agent synthesizing insights")
        
        system_prompt = """You are the Chief Portfolio Strategist at Target Capital.
Synthesize the analysis from all specialized agents into a comprehensive portfolio optimization report.

Create a well-structured markdown report with:
1. Executive Summary
2. Risk Assessment (from Risk Agent)
3. Sector Analysis (from Sector Agent)
4. Asset Allocation Strategy (from Allocation Agent)
5. Investment Opportunities (from Opportunity Agent)
6. Action Plan with prioritized steps
7. Expected Outcomes

Make it clear, actionable, and professional."""
        
        agent_outputs = state.get("agent_outputs", {})
        
        context = f"""Agent Outputs:
        
Risk Analysis:
{json.dumps(agent_outputs.get('risk_agent', {}), indent=2)}

Sector Analysis:
{json.dumps(agent_outputs.get('sector_agent', {}), indent=2)}

Allocation Recommendations:
{json.dumps(agent_outputs.get('allocation_agent', {}), indent=2)}

Investment Opportunities:
{json.dumps(agent_outputs.get('opportunity_agent', {}), indent=2)}"""
        
        response = self.balanced_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Create comprehensive report:\n{context}")
        ])
        
        content = response.content if isinstance(response.content, str) else str(response.content)
        return {
            "final_report": content,
            "messages": [AIMessage(content="Portfolio optimization report completed")]
        }
    
    def optimize_portfolio(self, user_id: int) -> Dict:
        """
        Main entry point for portfolio optimization
        
        Args:
            user_id: User ID to optimize portfolio for
        
        Returns:
            Dict with comprehensive optimization report and agent insights
        """
        logger.info(f"Starting multi-agent portfolio optimization for user {user_id}")
        
        # Initialize state
        initial_state = {
            "messages": [],
            "user_id": user_id,
            "portfolio_data": {},
            "risk_analysis": {},
            "sector_analysis": {},
            "allocation_recommendations": {},
            "opportunities": [],
            "final_report": "",
            "agent_outputs": {}
        }
        
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            return {
                "report": final_state.get("final_report", ""),
                "risk_analysis": final_state.get("risk_analysis", {}),
                "sector_analysis": final_state.get("sector_analysis", {}),
                "allocation_recommendations": final_state.get("allocation_recommendations", {}),
                "opportunities": final_state.get("opportunities", []),
                "metadata": {
                    "agents_used": list(final_state.get("agent_outputs", {}).keys()),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            return {
                "report": f"Portfolio optimization encountered an error: {str(e)}",
                "error": str(e)
            }
