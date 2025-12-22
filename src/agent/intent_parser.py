"""
Intent Parser - Extracts structured intent from natural language commands

Uses GPT-4o or Gemini to parse user commands into actionable intents.
Falls back to keyword matching if AI is unavailable.
"""

import json
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .config import config, INTENT_KEYWORDS, ACTIONS


@dataclass
class ParsedIntent:
    """Structured intent extracted from user command"""
    action: str
    confidence: float
    parameters: Dict[str, Any]
    original_command: str
    requires_approval: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "confidence": self.confidence,
            "parameters": self.parameters,
            "original_command": self.original_command,
            "requires_approval": self.requires_approval
        }


class IntentParser:
    """Parse natural language commands into structured intents"""
    
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
        self.ai_client = None
        self._gemini_model_name = None
        
        if use_ai:
            self._init_ai_client()
    
    def _init_ai_client(self):
        """Initialize AI client based on configuration"""
        try:
            if config.ai_provider == "openai" and config.openai_api_key:
                from openai import OpenAI
                self.ai_client = OpenAI(api_key=config.openai_api_key)
            elif config.ai_provider == "gemini" and config.get_current_api_key():
                from google import genai
                self.ai_client = genai.Client(api_key=config.get_current_api_key())
                self._gemini_model_name = config.gemini_model
        except ImportError as e:
            print(f"AI library not available: {e}")
            self.ai_client = None
    
    def _switch_api_key(self):
        """Switch to next API key on rate limit"""
        new_key = config.get_next_api_key()
        if new_key and config.ai_provider == "gemini":
            from google import genai
            self.ai_client = genai.Client(api_key=new_key)
            return True
        return False
    
    def parse(self, command: str) -> ParsedIntent:
        """Parse a natural language command into a structured intent"""
        
        # Try AI-based parsing first
        if self.use_ai and self.ai_client:
            intent = self._parse_with_ai(command)
            if intent and intent.confidence > 0.7:
                return intent
        
        # Fall back to keyword matching
        return self._parse_with_keywords(command)
    
    def _parse_with_ai(self, command: str) -> Optional[ParsedIntent]:
        """Use AI to parse the command with retry and key rotation"""
        
        prompt = self._build_parsing_prompt(command)
        max_retries = len(config.gemini_api_keys) if config.gemini_api_keys else 1
        
        for attempt in range(max_retries):
            try:
                if config.ai_provider == "openai":
                    response = self.ai_client.chat.completions.create(
                        model=config.openai_model,
                        messages=[
                            {"role": "system", "content": "You are a financial action parser. Extract structured intent from user commands."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    result = json.loads(response.choices[0].message.content)
                
                elif config.ai_provider == "gemini":
                    # Use new google.genai API
                    response = self.ai_client.models.generate_content(
                        model=self._gemini_model_name,
                        contents=prompt
                    )
                    # Extract JSON from response
                    text = response.text
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        return None
                
                # Validate and create intent
                action = result.get("action", "unknown")
                if action in ACTIONS:
                    return ParsedIntent(
                        action=action,
                        confidence=result.get("confidence", 0.9),
                        parameters=result.get("parameters", {}),
                        original_command=command,
                        requires_approval=ACTIONS[action]["requires_approval"]
                    )
            
            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit / quota errors
                if "429" in str(e) or "quota" in error_str or "rate" in error_str or "limit" in error_str:
                    print(f"⚠️ API quota hit, rotating key...")
                    if self._switch_api_key():
                        continue
                print(f"AI parsing error: {e}")
        
        return None
    
    def _parse_with_keywords(self, command: str) -> ParsedIntent:
        """Simple keyword-based intent parsing with weighted scoring"""
        
        command_lower = command.lower()
        best_match = None
        best_score = 0
        
        for action, keywords in INTENT_KEYWORDS.items():
            # Weight longer keywords more heavily to prefer specific matches
            # "edit profile" should score higher than just "profile"
            score = sum(
                len(kw.split())  # Weight by number of words in keyword
                for kw in keywords 
                if kw in command_lower
            )
            if score > best_score:
                best_score = score
                best_match = action
        
        if best_match:
            # Extract parameters based on action type
            params = self._extract_parameters(command, best_match)
            
            return ParsedIntent(
                action=best_match,
                confidence=min(0.5 + (best_score * 0.15), 0.95),
                parameters=params,
                original_command=command,
                requires_approval=ACTIONS[best_match]["requires_approval"]
            )
        
        return ParsedIntent(
            action="unknown",
            confidence=0.0,
            parameters={},
            original_command=command,
            requires_approval=False
        )
    
    def _extract_parameters(self, command: str, action: str) -> Dict[str, Any]:
        """Extract relevant parameters from the command based on action type"""
        
        params = {}
        
        # Extract amount (e.g., "₹500", "500 rupees", "Rs 1000")
        amount_pattern = r'(?:₹|rs\.?|rupees?)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)|(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:₹|rs\.?|rupees?)'
        amount_match = re.search(amount_pattern, command, re.IGNORECASE)
        if amount_match:
            amount_str = amount_match.group(1) or amount_match.group(2)
            params["amount"] = float(amount_str.replace(",", ""))
        
        # Extract plain numbers if no currency symbol
        if "amount" not in params:
            number_pattern = r'\b(\d+(?:,\d{3})*(?:\.\d{2})?)\b'
            numbers = re.findall(number_pattern, command)
            if numbers:
                params["amount"] = float(numbers[0].replace(",", ""))
        
        # Action-specific parameter extraction
        if action == "pay_bill":
            # Extract biller type
            billers = ["electricity", "gas", "water", "mobile", "broadband", "internet", "dth"]
            for biller in billers:
                if biller in command.lower():
                    params["biller_type"] = biller
                    break
            
            # Extract biller name
            biller_names = ["adani", "tata", "reliance", "bses", "jio", "airtel", "mahanagar"]
            for name in biller_names:
                if name in command.lower():
                    params["biller_name"] = name.capitalize()
                    break
        
        elif action == "fund_transfer":
            # Extract recipient name
            to_pattern = r'(?:to|for)\s+(\w+(?:\s+\w+)?)'
            to_match = re.search(to_pattern, command, re.IGNORECASE)
            if to_match:
                params["recipient"] = to_match.group(1).strip()
            
            # Check for known beneficiaries
            beneficiaries = ["mom", "dad", "friend", "rahul", "sneha"]
            for ben in beneficiaries:
                if ben in command.lower():
                    params["recipient"] = ben.capitalize()
                    break
        
        elif action == "buy_gold":
            # Extract grams if specified
            grams_pattern = r'(\d+(?:\.\d+)?)\s*(?:grams?|g\b)'
            grams_match = re.search(grams_pattern, command, re.IGNORECASE)
            if grams_match:
                params["grams"] = float(grams_match.group(1))
                params["buy_type"] = "grams"
            else:
                params["buy_type"] = "amount"
        
        return params
    
    def _build_parsing_prompt(self, command: str) -> str:
        """Build the prompt for AI parsing"""
        
        actions_list = ", ".join(ACTIONS.keys())
        
        return f"""
Parse the following banking command into a structured intent.

User Command: "{command}"

Available Actions: {actions_list}

Extract:
1. action - The primary action to perform (must be one of the available actions)
2. confidence - How confident you are (0.0 to 1.0)
3. parameters - Relevant parameters like:
   - amount (numeric)
   - recipient (for transfers)
   - biller_type (electricity, gas, water, mobile, broadband)
   - biller_name (company name)
   - grams (for gold purchase)
   - buy_type ("amount" or "grams" for gold)

Respond with valid JSON only:
{{
    "action": "action_name",
    "confidence": 0.95,
    "parameters": {{...}}
}}
"""


# Convenience function
def parse_intent(command: str) -> ParsedIntent:
    """Quick intent parsing with default settings"""
    parser = IntentParser(use_ai=True)
    return parser.parse(command)
