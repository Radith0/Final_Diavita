"""Prompt templates for LLM advice generation."""
from typing import Dict, Any, List


class PromptTemplates:
    """Collection of prompt templates for diabetes advice generation."""

    @staticmethod
    def build_advice_prompt(
        risk_score: float,
        risk_factors: List[Dict[str, Any]],
        lifestyle_data: Dict[str, Any],
        retinal_findings: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive advice prompt.

        Args:
            risk_score: Overall diabetes risk score (0-1)
            risk_factors: List of identified risk factors
            lifestyle_data: User's lifestyle information
            retinal_findings: Retinal analysis results

        Returns:
            Formatted prompt string
        """
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "moderate"
        else:
            risk_level = "high"

        # Extract key modifiable factors
        modifiable_factors = [
            f for f in risk_factors
            if f.get('source') == 'lifestyle' and f.get('modifiable', False)
        ]

        # Build prompt
        prompt = f"""You are a diabetes prevention expert. Based on the following assessment, provide personalized, actionable advice.

**Risk Assessment:**
- Overall Risk Score: {risk_score:.2f} ({risk_level} risk)
- Risk Level: {risk_level.upper()}

**Identified Risk Factors:**
"""

        # Add risk factors
        for idx, factor in enumerate(risk_factors[:5], 1):
            source = factor.get('source', 'unknown')
            factor_name = factor.get('factor', 'Unknown factor')
            prompt += f"{idx}. [{source.upper()}] {factor_name}\n"

        # Add lifestyle context
        prompt += f"\n**Current Lifestyle:**\n"
        if lifestyle_data.get('bmi'):
            prompt += f"- BMI: {lifestyle_data['bmi']}\n"
        if lifestyle_data.get('physical_activity') is not None:
            prompt += f"- Physical Activity: {lifestyle_data['physical_activity']} min/week\n"
        if lifestyle_data.get('sleep_hours'):
            prompt += f"- Sleep: {lifestyle_data['sleep_hours']} hours/night\n"
        if lifestyle_data.get('age'):
            prompt += f"- Age: {lifestyle_data['age']} years\n"

        # Add retinal findings if significant
        if retinal_findings.get('total_features_detected', 0) > 0:
            prompt += f"\n**Retinal Findings:** Diabetic retinopathy signs detected\n"

        # Request structured advice
        prompt += f"""
**Please provide personalized recommendations in this EXACT format:**

## Personalized Recommendations

List 5-7 complete, actionable recommendations. Each recommendation should be ONE complete statement including the action AND why it matters. Format as a simple numbered list:

1. [Complete recommendation with action and brief reason in one sentence]
2. [Complete recommendation with action and brief reason in one sentence]
...

**Important formatting rules:**
- Each recommendation must be ONE complete sentence
- Do NOT split "what" and "why" into separate lines
- Do NOT use sub-bullets or nested formatting
- Do NOT use ** for bold inside recommendations
- Just clean, complete sentences

Focus on modifiable factors: {', '.join([f.get('factor', '') for f in modifiable_factors[:3]])}

Make it evidence-based, practical, and encouraging.
"""

        return prompt

    @staticmethod
    def build_simulation_explanation_prompt(
        intervention: str,
        current_risk: float,
        projected_risk: float
    ) -> str:
        """
        Build prompt for explaining simulation results.

        Args:
            intervention: Name of the intervention
            current_risk: Current risk score
            projected_risk: Projected risk after intervention

        Returns:
            Formatted prompt
        """
        risk_reduction = current_risk - projected_risk
        percent_reduction = (risk_reduction / current_risk) * 100

        prompt = f"""Explain in 2-3 sentences why {intervention} can reduce diabetes risk from {current_risk:.2f} to {projected_risk:.2f} (a {percent_reduction:.1f}% reduction).

Focus on:
- The biological/physiological mechanism
- Realistic timeline for seeing benefits
- Additional health benefits beyond diabetes prevention

Keep the explanation simple and motivating."""

        return prompt

    @staticmethod
    def build_goal_setting_prompt(
        risk_factors: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> str:
        """
        Build prompt for personalized goal setting.

        Args:
            risk_factors: Identified modifiable risk factors
            user_preferences: User's preferences and constraints

        Returns:
            Formatted prompt
        """
        prompt = f"""Based on these modifiable risk factors, help create SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound):

**Risk Factors to Address:**
"""

        for idx, factor in enumerate(risk_factors[:3], 1):
            prompt += f"{idx}. {factor.get('factor', 'Unknown')}\n"

        prompt += f"""
**User Context:**
- Available time: {user_preferences.get('time_availability', 'not specified')}
- Budget constraints: {user_preferences.get('budget', 'not specified')}
- Support system: {user_preferences.get('support', 'not specified')}

Provide 3 SMART goals that:
1. Target the highest-impact risk factors
2. Are realistic given user context
3. Build on each other progressively
4. Can be started immediately

Format each goal clearly with specific metrics and timelines.
"""

        return prompt
