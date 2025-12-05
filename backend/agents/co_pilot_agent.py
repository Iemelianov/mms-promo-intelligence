"""
Explainer / Co-Pilot (Chat) Agent

Purpose: Conversational interface for all screens

Responsibilities:
- Answer "why" questions
- Explain complex calculations
- Help brainstorm scenarios
- Provide what-if analysis

Context Awareness:
- Current screen/state
- Active scenarios
- Validation reports
- User's current task
"""

from typing import Optional, Dict, Any
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from ..models.schemas import PromoScenario, ValidationReport


class CoPilotAgent:
    """Agent for conversational interface and explanations."""
    
    def __init__(
        self,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Co-Pilot Agent.
        
        Args:
            context: Optional context dictionary with current state
        """
        self.context = context or {}
        
        # TODO: Initialize LangChain agent executor
        # self.agent_executor: Optional[AgentExecutor] = None
    
    def answer_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Answer user's question with context awareness.
        
        Args:
            question: User's question
            context: Optional additional context
        
        Returns:
            Answer string
        """
        # TODO: Implement question answering logic
        raise NotImplementedError("answer_question not yet implemented")
    
    def explain_calculation(
        self,
        calculation_type: str,
        inputs: Dict[str, Any]
    ) -> str:
        """
        Explain how a calculation was performed.
        
        Args:
            calculation_type: Type of calculation (e.g., "scenario_kpi", "uplift")
            inputs: Dictionary with calculation inputs
        
        Returns:
            Explanation string
        """
        # TODO: Implement calculation explanation logic
        raise NotImplementedError("explain_calculation not yet implemented")
    
    def brainstorm_scenarios(
        self,
        problem: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Help brainstorm promotional scenarios.
        
        Args:
            problem: Problem description
            constraints: Optional constraints dictionary
        
        Returns:
            Brainstorming suggestions string
        """
        # TODO: Implement brainstorming logic
        raise NotImplementedError("brainstorm_scenarios not yet implemented")
    
    def what_if_analysis(
        self,
        scenario: PromoScenario,
        parameter_changes: Dict[str, Any]
    ) -> str:
        """
        Perform what-if analysis on a scenario.
        
        Args:
            scenario: Base PromoScenario
            parameter_changes: Dictionary of parameter changes
        
        Returns:
            Analysis results string
        """
        # TODO: Implement what-if analysis logic
        raise NotImplementedError("what_if_analysis not yet implemented")
    
    def update_context(
        self,
        screen: Optional[str] = None,
        active_scenarios: Optional[list] = None,
        validation_reports: Optional[List[ValidationReport]] = None,
        current_task: Optional[str] = None,
    ):
        """
        Update agent context with current state.
        
        Args:
            screen: Current screen name
            active_scenarios: List of active scenarios
            validation_reports: List of validation reports
            current_task: Current task description
        """
        if screen:
            self.context['screen'] = screen
        if active_scenarios:
            self.context['active_scenarios'] = active_scenarios
        if validation_reports:
            self.context['validation_reports'] = validation_reports
        if current_task:
            self.context['current_task'] = current_task




