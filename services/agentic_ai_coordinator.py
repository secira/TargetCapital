"""
Agentic AI Coordinator Service
Orchestrates multiple AI agents for comprehensive investment analysis and decision-making
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
from openai import OpenAI

class AgenticAICoordinator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized AI agents
        self.research_agent = ResearchAgent(self.openai_client)
        self.analysis_agent = AnalysisAgent(self.openai_client)
        self.decision_agent = DecisionAgent(self.openai_client)
        self.learning_agent = LearningAgent(self.openai_client)
        
    def analyze_with_agentic_ai(self, symbol: str, analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Perform comprehensive agentic AI analysis using learn-reason-act-adapt cycle
        """
        try:
            self.logger.info(f"Starting agentic AI analysis for {symbol}")
            
            # Step 1: LEARN - Gather comprehensive data
            learning_result = self._learn_phase(symbol)
            
            # Step 2: REASON - Analyze and synthesize information
            reasoning_result = self._reason_phase(symbol, learning_result)
            
            # Step 3: ACT - Generate actionable recommendations
            action_result = self._act_phase(symbol, learning_result, reasoning_result)
            
            # Step 4: ADAPT - Learn from outcomes and adjust
            adaptation_result = self._adapt_phase(symbol, action_result)
            
            # Compile comprehensive results
            comprehensive_analysis = {
                'symbol': symbol,
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat(),
                'learning_insights': learning_result,
                'reasoning_analysis': reasoning_result,
                'action_recommendations': action_result,
                'adaptation_feedback': adaptation_result,
                'final_recommendation': action_result.get('primary_recommendation', 'HOLD'),
                'confidence': action_result.get('confidence_score', 0.5),
                'reasoning_summary': reasoning_result.get('summary', 'Analysis completed'),
                'research_insights': learning_result.get('key_insights', [])
            }
            
            self.logger.info(f"Completed agentic AI analysis for {symbol}")
            return comprehensive_analysis
            
        except Exception as e:
            self.logger.error(f"Agentic AI analysis error for {symbol}: {str(e)}")
            return {
                'error': f'Agentic AI analysis failed: {str(e)}',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
    
    def optimize_portfolio_comprehensive(self, portfolio: Dict) -> Dict[str, Any]:
        """
        Comprehensive portfolio optimization using agentic AI approach
        """
        try:
            self.logger.info("Starting agentic AI portfolio optimization")
            
            # Learn current portfolio state and market conditions
            portfolio_learning = self._learn_portfolio_state(portfolio)
            
            # Reason about optimal allocation and risk management
            optimization_reasoning = self._reason_portfolio_optimization(portfolio, portfolio_learning)
            
            # Act with specific rebalancing recommendations
            optimization_actions = self._act_portfolio_optimization(portfolio, optimization_reasoning)
            
            # Adapt based on risk tolerance and constraints
            optimization_adaptation = self._adapt_portfolio_strategy(portfolio, optimization_actions)
            
            return {
                'portfolio_analysis': portfolio_learning,
                'optimization_reasoning': optimization_reasoning,
                'optimization': optimization_actions,
                'adaptation_strategy': optimization_adaptation,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Portfolio optimization error: {str(e)}")
            return {
                'error': f'Portfolio optimization failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _learn_phase(self, symbol: str) -> Dict[str, Any]:
        """LEARN: Gather comprehensive data and insights"""
        return self.research_agent.gather_comprehensive_data(symbol)
    
    def _reason_phase(self, symbol: str, learning_data: Dict) -> Dict[str, Any]:
        """REASON: Analyze and synthesize information"""
        return self.analysis_agent.synthesize_analysis(symbol, learning_data)
    
    def _act_phase(self, symbol: str, learning_data: Dict, reasoning_data: Dict) -> Dict[str, Any]:
        """ACT: Generate actionable recommendations"""
        return self.decision_agent.generate_recommendations(symbol, learning_data, reasoning_data)
    
    def _adapt_phase(self, symbol: str, action_data: Dict) -> Dict[str, Any]:
        """ADAPT: Learn from outcomes and adjust strategy"""
        return self.learning_agent.adapt_strategy(symbol, action_data)
    
    def _learn_portfolio_state(self, portfolio: Dict) -> Dict[str, Any]:
        """Learn current portfolio state and market conditions"""
        return self.research_agent.analyze_portfolio_state(portfolio)
    
    def _reason_portfolio_optimization(self, portfolio: Dict, learning_data: Dict) -> Dict[str, Any]:
        """Reason about portfolio optimization strategies"""
        return self.analysis_agent.reason_portfolio_optimization(portfolio, learning_data)
    
    def _act_portfolio_optimization(self, portfolio: Dict, reasoning_data: Dict) -> Dict[str, Any]:
        """Generate specific portfolio optimization actions"""
        return self.decision_agent.generate_portfolio_actions(portfolio, reasoning_data)
    
    def _adapt_portfolio_strategy(self, portfolio: Dict, action_data: Dict) -> Dict[str, Any]:
        """Adapt portfolio strategy based on constraints and feedback"""
        return self.learning_agent.adapt_portfolio_strategy(portfolio, action_data)


class ResearchAgent:
    """Specialized agent for comprehensive data gathering and research"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.logger = logging.getLogger(__name__)
    
    def gather_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """Gather comprehensive research data"""
        try:
            research_prompt = f"""
            As a senior financial research analyst, conduct comprehensive research on {symbol}:
            
            Research Areas:
            1. Company fundamentals (revenue, profitability, growth rates)
            2. Industry analysis and competitive positioning
            3. Recent news and market sentiment
            4. Technical indicators and price trends
            5. Risk factors and opportunities
            6. Analyst consensus and price targets
            7. ESG factors and sustainability metrics
            8. Management quality and corporate governance
            
            Provide detailed insights in JSON format with clear structure.
            Focus on actionable intelligence that can inform investment decisions.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior financial research analyst with 15 years of experience in equity research. Provide comprehensive, data-driven analysis."},
                    {"role": "user", "content": research_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.1
            )
            
            research_data = json.loads(response.choices[0].message.content)
            
            return {
                'research_completed': True,
                'data_sources': ['Fundamental Analysis', 'Technical Analysis', 'Sentiment Analysis', 'Industry Analysis'],
                'key_insights': research_data.get('key_insights', []),
                'research_summary': research_data.get('summary', 'Research completed'),
                'detailed_findings': research_data,
                'confidence_level': research_data.get('data_confidence', 0.8),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Research gathering error for {symbol}: {str(e)}")
            return {
                'research_completed': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_portfolio_state(self, portfolio: Dict) -> Dict[str, Any]:
        """Analyze current portfolio state comprehensively"""
        try:
            portfolio_prompt = f"""
            Analyze the current portfolio state:
            
            Portfolio Data: {json.dumps(portfolio, indent=2)}
            
            Analysis Areas:
            1. Asset allocation and diversification
            2. Risk concentration and correlation analysis
            3. Sector and geographic exposure
            4. Performance attribution
            5. Cash flow and liquidity analysis
            6. Tax efficiency considerations
            7. ESG alignment assessment
            8. Cost analysis (fees, expenses)
            
            Provide comprehensive portfolio state analysis in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a portfolio analyst specializing in comprehensive portfolio assessment and optimization."},
                    {"role": "user", "content": portfolio_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1800,
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Portfolio state analysis error: {str(e)}")
            return {'error': str(e)}


class AnalysisAgent:
    """Specialized agent for deep analysis and reasoning"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.logger = logging.getLogger(__name__)
    
    def synthesize_analysis(self, symbol: str, research_data: Dict) -> Dict[str, Any]:
        """Synthesize research data into comprehensive analysis"""
        try:
            analysis_prompt = f"""
            Synthesize the following research data for {symbol} into comprehensive investment analysis:
            
            Research Data: {json.dumps(research_data, indent=2)}
            
            Analysis Framework:
            1. Valuation analysis (multiple approaches)
            2. Growth prospects and sustainability
            3. Competitive advantage assessment
            4. Risk-return profile evaluation
            5. Market timing considerations
            6. Scenario analysis (bull/base/bear cases)
            7. Catalyst identification
            8. Investment thesis development
            
            Provide structured analysis with clear reasoning in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a CFA charterholder and senior equity analyst with expertise in valuation, risk assessment, and investment strategy."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.1
            )
            
            analysis_result = json.loads(response.choices[0].message.content)
            
            return {
                'analysis_completed': True,
                'valuation_analysis': analysis_result.get('valuation_analysis', {}),
                'growth_analysis': analysis_result.get('growth_analysis', {}),
                'risk_analysis': analysis_result.get('risk_analysis', {}),
                'competitive_analysis': analysis_result.get('competitive_analysis', {}),
                'scenario_analysis': analysis_result.get('scenario_analysis', {}),
                'investment_thesis': analysis_result.get('investment_thesis', 'Analysis completed'),
                'summary': analysis_result.get('summary', 'Comprehensive analysis completed'),
                'confidence_score': analysis_result.get('confidence_score', 0.7),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Analysis synthesis error for {symbol}: {str(e)}")
            return {
                'analysis_completed': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def reason_portfolio_optimization(self, portfolio: Dict, learning_data: Dict) -> Dict[str, Any]:
        """Reason about optimal portfolio structure and allocation"""
        try:
            reasoning_prompt = f"""
            Reason about portfolio optimization based on current state and analysis:
            
            Portfolio: {json.dumps(portfolio, indent=2)}
            Analysis: {json.dumps(learning_data, indent=2)}
            
            Reasoning Framework:
            1. Risk-return optimization
            2. Correlation and diversification analysis
            3. Asset allocation efficiency
            4. Rebalancing opportunities
            5. Tax optimization strategies
            6. Cost minimization approaches
            7. Liquidity management
            8. Strategic vs tactical allocation
            
            Provide detailed reasoning for optimization decisions in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior portfolio manager with expertise in modern portfolio theory, risk management, and quantitative optimization."},
                    {"role": "user", "content": reasoning_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1800,
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Portfolio optimization reasoning error: {str(e)}")
            return {'error': str(e)}


class DecisionAgent:
    """Specialized agent for generating actionable recommendations and decisions"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.logger = logging.getLogger(__name__)
    
    def generate_recommendations(self, symbol: str, research_data: Dict, analysis_data: Dict) -> Dict[str, Any]:
        """Generate specific, actionable investment recommendations"""
        try:
            decision_prompt = f"""
            Generate specific investment recommendations for {symbol} based on comprehensive analysis:
            
            Research: {json.dumps(research_data, indent=2)}
            Analysis: {json.dumps(analysis_data, indent=2)}
            
            Decision Framework:
            1. Primary investment recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
            2. Position sizing recommendation
            3. Entry strategy and timing
            4. Risk management parameters
            5. Profit-taking strategy
            6. Stop-loss levels
            7. Time horizon recommendations
            8. Alternative scenarios and contingencies
            
            Provide clear, actionable recommendations with confidence levels in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior portfolio manager and investment committee member with authority to make investment decisions. Provide clear, actionable recommendations."},
                    {"role": "user", "content": decision_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.1
            )
            
            decision_result = json.loads(response.choices[0].message.content)
            
            return {
                'primary_recommendation': decision_result.get('primary_recommendation', 'HOLD'),
                'confidence_score': decision_result.get('confidence_score', 0.6),
                'position_sizing': decision_result.get('position_sizing', 'Standard'),
                'entry_strategy': decision_result.get('entry_strategy', {}),
                'risk_management': decision_result.get('risk_management', {}),
                'profit_strategy': decision_result.get('profit_strategy', {}),
                'time_horizon': decision_result.get('time_horizon', '6-12 months'),
                'contingency_plans': decision_result.get('contingency_plans', []),
                'decision_rationale': decision_result.get('decision_rationale', 'Based on comprehensive analysis'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Decision generation error for {symbol}: {str(e)}")
            return {
                'primary_recommendation': 'HOLD',
                'confidence_score': 0.5,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_portfolio_actions(self, portfolio: Dict, reasoning_data: Dict) -> Dict[str, Any]:
        """Generate specific portfolio optimization actions"""
        try:
            action_prompt = f"""
            Generate specific portfolio optimization actions based on reasoning:
            
            Portfolio: {json.dumps(portfolio, indent=2)}
            Reasoning: {json.dumps(reasoning_data, indent=2)}
            
            Action Categories:
            1. Rebalancing actions (specific trades)
            2. Risk management adjustments
            3. Asset allocation changes
            4. Position sizing modifications
            5. Cash management decisions
            6. Tax optimization moves
            7. Cost reduction strategies
            8. Timing considerations
            
            Provide specific, executable actions with priorities in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a portfolio manager with execution authority. Provide specific, actionable portfolio management decisions."},
                    {"role": "user", "content": action_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Portfolio action generation error: {str(e)}")
            return {'error': str(e)}


class LearningAgent:
    """Specialized agent for continuous learning and strategy adaptation"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.logger = logging.getLogger(__name__)
    
    def adapt_strategy(self, symbol: str, action_data: Dict) -> Dict[str, Any]:
        """Adapt investment strategy based on outcomes and feedback"""
        try:
            adaptation_prompt = f"""
            Adapt and refine investment strategy for {symbol} based on decision outcomes:
            
            Action Data: {json.dumps(action_data, indent=2)}
            
            Adaptation Areas:
            1. Strategy refinement based on market feedback
            2. Risk parameter adjustments
            3. Decision framework improvements
            4. Confidence calibration
            5. Timing optimization
            6. Position sizing refinement
            7. Exit strategy adjustments
            8. Learning integration
            
            Provide strategy adaptations and improvements in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a quantitative strategist focused on continuous improvement and adaptive learning in investment processes."},
                    {"role": "user", "content": adaptation_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1200,
                temperature=0.2
            )
            
            adaptation_result = json.loads(response.choices[0].message.content)
            
            return {
                'strategy_adaptations': adaptation_result.get('strategy_adaptations', []),
                'risk_adjustments': adaptation_result.get('risk_adjustments', {}),
                'decision_refinements': adaptation_result.get('decision_refinements', []),
                'confidence_calibration': adaptation_result.get('confidence_calibration', {}),
                'learning_insights': adaptation_result.get('learning_insights', []),
                'improvement_recommendations': adaptation_result.get('improvement_recommendations', []),
                'adapted_strategy': adaptation_result.get('adapted_strategy', 'Strategy adapted'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Strategy adaptation error for {symbol}: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def adapt_portfolio_strategy(self, portfolio: Dict, action_data: Dict) -> Dict[str, Any]:
        """Adapt portfolio strategy based on constraints and feedback"""
        try:
            portfolio_adaptation_prompt = f"""
            Adapt portfolio strategy based on action results and constraints:
            
            Portfolio: {json.dumps(portfolio, indent=2)}
            Actions: {json.dumps(action_data, indent=2)}
            
            Adaptation Framework:
            1. Constraint integration and adjustment
            2. Risk tolerance calibration
            3. Performance attribution learning
            4. Cost-benefit optimization
            5. Liquidity management refinement
            6. Tax efficiency improvements
            7. Behavioral bias corrections
            8. Strategic framework evolution
            
            Provide portfolio strategy adaptations in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a portfolio strategist specializing in adaptive portfolio management and continuous strategy refinement."},
                    {"role": "user", "content": portfolio_adaptation_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1200,
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Portfolio strategy adaptation error: {str(e)}")
            return {'error': str(e)}