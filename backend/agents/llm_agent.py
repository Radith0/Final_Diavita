"""LLM-based advice generation agent using Groq AI."""
import time
from typing import Dict, Any
from agents.base_agent import BaseAgent
from models.llm.llm_interface import GroqLLMInterface
from models.llm.prompt_templates import PromptTemplates
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMAgent(BaseAgent):
    """Agent responsible for generating personalized advice using LLM."""

    def __init__(self):
        """Initialize LLM agent with Groq interface."""
        super().__init__(agent_id="llm_agent")
        self.llm = GroqLLMInterface()
        self.prompts = PromptTemplates()
        logger.info("LLMAgent initialized with Groq AI")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized diabetes prevention advice.

        Args:
            task: Dict containing:
                - risk_score: Overall risk score
                - risk_factors: List of identified risk factors
                - lifestyle_data: User's lifestyle information
                - retinal_findings: Retinal analysis results

        Returns:
            Personalized recommendations and advice
        """
        try:
            start_time = time.time()

            risk_score = task.get('risk_score', 0.0)
            risk_factors = task.get('risk_factors', [])
            lifestyle_data = task.get('lifestyle_data') or {}
            retinal_findings = task.get('retinal_findings') or {}

            logger.info(f"Generating advice for risk score: {risk_score}")
            self.log_action("advice_generation_started", {"risk_score": risk_score})

            # Build context-aware prompt
            prompt = self.prompts.build_advice_prompt(
                risk_score=risk_score,
                risk_factors=risk_factors,
                lifestyle_data=lifestyle_data,
                retinal_findings=retinal_findings
            )

            # Generate advice using LLM
            logger.debug("Calling Groq LLM for advice generation")
            try:
                llm_response = await self.llm.generate(prompt)
                self.log_action("llm_response_received", len(llm_response) if llm_response else 0)
            except Exception as e:
                logger.warning(f"LLM generation failed, using defaults: {e}")
                llm_response = ""  # Use empty string to trigger default recommendations

            # Parse and structure the response
            structured_advice = self._parse_advice(llm_response, risk_factors)

            processing_time = time.time() - start_time

            result = {
                'status': 'success',
                'recommendations': structured_advice['recommendations'],
                'priority_actions': structured_advice['priority_actions'],
                'explanation': structured_advice['explanation'],
                'preventive_tips': structured_advice['preventive_tips'],
                'processing_time': processing_time
            }

            logger.info(f"Advice generation complete in {processing_time:.2f}s")
            self.log_action("advice_generation_complete", result)

            return result

        except Exception as e:
            logger.error(f"Advice generation failed: {str(e)}")
            self.log_action("advice_generation_failed", str(e))
            return {
                'status': 'error',
                'error': str(e),
                'recommendations': [],
                'priority_actions': []
            }

    def _parse_advice(self, llm_response: str, risk_factors: list) -> Dict[str, Any]:
        """
        Parse and structure LLM response into actionable advice.

        Args:
            llm_response: Raw LLM output
            risk_factors: Identified risk factors

        Returns:
            Structured advice dictionary
        """
        lines = llm_response.split('\n')

        recommendations = []
        priority_actions = []
        explanation = ""
        preventive_tips = []

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip markdown headers and table rows
            if line.startswith('#') or line.startswith('|') or line.startswith('**'):
                # Check if this is a section header
                lower_line = line.lower()
                if 'priority' in lower_line or 'action' in lower_line:
                    current_section = 'priority'
                elif 'recommendation' in lower_line:
                    current_section = 'recommendations'
                elif 'explanation' in lower_line:
                    current_section = 'explanation'
                elif 'tip' in lower_line or 'prevent' in lower_line:
                    current_section = 'tips'
                continue

            # Parse based on current section
            if current_section == 'recommendations':
                # Look for list items or numbered items
                if line.startswith(('-', '•', '*')) or (len(line) > 10 and line[0].isdigit()):
                    clean_line = line.lstrip('-•*0123456789. ').strip()
                    if len(clean_line) > 20:  # Only real recommendations
                        recommendations.append(clean_line)
            elif current_section == 'priority':
                if line.startswith(('-', '•', '*')) or (len(line) > 10 and line[0].isdigit()):
                    clean_line = line.lstrip('-•*0123456789. ').strip()
                    if len(clean_line) > 20:
                        priority_actions.append(clean_line)
            elif current_section == 'explanation':
                if not line.startswith(('-', '•', '*', '#')):
                    explanation += line + " "
            elif current_section == 'tips':
                if line.startswith(('-', '•', '*')) or (len(line) > 10 and line[0].isdigit()):
                    clean_line = line.lstrip('-•*0123456789. ').strip()
                    if len(clean_line) > 20:
                        preventive_tips.append(clean_line)

        # Ensure we have at least some default recommendations
        if not recommendations:
            recommendations = self._get_default_recommendations(risk_factors)

        return {
            'recommendations': recommendations[:5],  # Top 5 recommendations
            'priority_actions': priority_actions[:3],  # Top 3 priority actions
            'explanation': explanation.strip() or "Based on your risk assessment, here are personalized recommendations.",
            'preventive_tips': preventive_tips[:3]
        }

    def _get_default_recommendations(self, risk_factors: list) -> list:
        """
        Generate default recommendations based on risk factors.

        Args:
            risk_factors: List of identified risk factors

        Returns:
            List of default recommendations
        """
        recommendations = [
            "Maintain a healthy diet rich in vegetables, whole grains, and lean proteins",
            "Engage in at least 150 minutes of moderate physical activity per week",
            "Monitor your blood glucose levels regularly",
            "Get adequate sleep (7-9 hours per night)",
            "Schedule regular check-ups with your healthcare provider"
        ]

        # Customize based on specific risk factors
        for factor in risk_factors:
            if 'BMI' in factor.get('factor', ''):
                recommendations.insert(0, "Work towards achieving a healthy BMI through balanced diet and exercise")
            elif 'sleep' in factor.get('factor', '').lower():
                recommendations.insert(0, "Improve sleep quality by maintaining a consistent sleep schedule")
            elif 'physical activity' in factor.get('factor', '').lower():
                recommendations.insert(0, "Gradually increase daily physical activity, starting with walking")

        return recommendations[:5]
