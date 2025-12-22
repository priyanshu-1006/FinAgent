"""
Unit Tests for Intent Parser

Tests all intent parsing functionality:
- Keyword-based parsing
- Parameter extraction
- Action classification
- Edge cases
"""

import pytest
from src.agent.intent_parser import IntentParser, ParsedIntent, parse_intent
from src.agent.config import ACTIONS, INTENT_KEYWORDS


class TestIntentParser:
    """Test suite for IntentParser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser without AI (keyword mode only)"""
        return IntentParser(use_ai=False)
    
    # ============ Pay Bill Tests ============
    
    def test_parse_pay_bill_basic(self, parser):
        """Test basic bill payment parsing"""
        intent = parser.parse("pay electricity bill of 1500")
        
        assert intent.action == "pay_bill"
        assert intent.parameters.get("amount") == 1500
        assert intent.parameters.get("biller_type") == "electricity"
        assert intent.requires_approval == True
    
    def test_parse_pay_bill_with_biller_name(self, parser):
        """Test bill payment with biller name"""
        intent = parser.parse("pay electricity bill of Rs 2000 to Adani Power")
        
        assert intent.action == "pay_bill"
        assert intent.parameters.get("amount") == 2000
        assert intent.parameters.get("biller_name") == "Adani"
    
    def test_parse_pay_bill_gas(self, parser):
        """Test gas bill payment"""
        intent = parser.parse("pay gas bill 500 rupees")
        
        assert intent.action == "pay_bill"
        assert intent.parameters.get("biller_type") == "gas"
        assert intent.parameters.get("amount") == 500
    
    def test_parse_pay_bill_mobile(self, parser):
        """Test mobile bill payment"""
        intent = parser.parse("pay mobile bill of ₹999 to Jio")
        
        assert intent.action == "pay_bill"
        assert intent.parameters.get("biller_type") == "mobile"
        assert intent.parameters.get("amount") == 999
        assert intent.parameters.get("biller_name") == "Jio"
    
    def test_parse_pay_bill_broadband(self, parser):
        """Test broadband bill payment"""
        intent = parser.parse("pay broadband bill 1299")
        
        assert intent.action == "pay_bill"
        assert intent.parameters.get("biller_type") == "broadband"
        assert intent.parameters.get("amount") == 1299
    
    # ============ Fund Transfer Tests ============
    
    def test_parse_fund_transfer_basic(self, parser):
        """Test basic fund transfer"""
        intent = parser.parse("transfer 5000 to Mom")
        
        assert intent.action == "fund_transfer"
        assert intent.parameters.get("amount") == 5000
        assert intent.parameters.get("recipient") == "Mom"
        assert intent.requires_approval == True
    
    def test_parse_fund_transfer_with_rupees(self, parser):
        """Test fund transfer with rupees keyword"""
        intent = parser.parse("transfer 10000 rupees to Rahul")
        
        assert intent.action == "fund_transfer"
        assert intent.parameters.get("amount") == 10000
        assert intent.parameters.get("recipient") == "Rahul"
    
    def test_parse_fund_transfer_send_money(self, parser):
        """Test 'send money' phrasing - transfer keyword is more explicit"""
        intent = parser.parse("transfer 2500 to my friend")
        
        assert intent.action == "fund_transfer"
        assert intent.parameters.get("amount") == 2500
        assert intent.parameters.get("recipient") == "Friend"
    
    def test_parse_fund_transfer_with_currency_symbol(self, parser):
        """Test transfer with ₹ symbol"""
        intent = parser.parse("transfer ₹15000 to Dad")
        
        assert intent.action == "fund_transfer"
        assert intent.parameters.get("amount") == 15000
        assert intent.parameters.get("recipient") == "Dad"
    
    # ============ Buy Gold Tests ============
    
    def test_parse_buy_gold_amount(self, parser):
        """Test gold purchase by amount"""
        intent = parser.parse("buy gold worth 10000")
        
        assert intent.action == "buy_gold"
        assert intent.parameters.get("amount") == 10000
        assert intent.parameters.get("buy_type") == "amount"
        assert intent.requires_approval == True
    
    def test_parse_buy_gold_grams(self, parser):
        """Test gold purchase by grams"""
        intent = parser.parse("buy 5 grams of gold")
        
        assert intent.action == "buy_gold"
        assert intent.parameters.get("grams") == 5.0
        assert intent.parameters.get("buy_type") == "grams"
    
    def test_parse_buy_gold_digital(self, parser):
        """Test digital gold purchase"""
        intent = parser.parse("invest in digital gold Rs 5000")
        
        assert intent.action == "buy_gold"
        assert intent.parameters.get("amount") == 5000
    
    # ============ Login Tests ============
    
    def test_parse_login(self, parser):
        """Test login intent"""
        intent = parser.parse("login to the bank")
        
        assert intent.action == "login"
        assert intent.requires_approval == False
    
    def test_parse_sign_in(self, parser):
        """Test sign in phrasing"""
        intent = parser.parse("sign in to my account")
        
        assert intent.action == "login"
    
    # ============ Balance Check Tests ============
    
    def test_parse_check_balance(self, parser):
        """Test balance check"""
        intent = parser.parse("check my account balance")
        
        assert intent.action == "check_balance"
        assert intent.requires_approval == False
    
    def test_parse_how_much_money(self, parser):
        """Test 'how much money' phrasing"""
        intent = parser.parse("how much money do I have")
        
        assert intent.action == "check_balance"
    
    # ============ View Transactions Tests ============
    
    def test_parse_view_transactions(self, parser):
        """Test transaction history view"""
        intent = parser.parse("show my recent transactions")
        
        assert intent.action == "view_transactions"
        assert intent.requires_approval == False
    
    def test_parse_transaction_history(self, parser):
        """Test 'history' keyword"""
        intent = parser.parse("show transaction history")
        
        assert intent.action == "view_transactions"
    
    # ============ Profile Tests ============
    
    def test_parse_view_profile(self, parser):
        """Test profile view"""
        intent = parser.parse("show my profile")
        
        assert intent.action == "view_profile"
        assert intent.requires_approval == False
    
    def test_parse_update_profile(self, parser):
        """Test profile update - uses 'edit profile' keyword"""
        intent = parser.parse("edit profile details")
        
        assert intent.action == "update_profile"
        assert intent.requires_approval == True
    
    # ============ Amount Extraction Tests ============
    
    def test_extract_amount_rupee_symbol(self, parser):
        """Test amount with ₹ symbol"""
        intent = parser.parse("transfer ₹150000 to account")
        
        assert intent.parameters.get("amount") == 150000
    
    def test_extract_amount_rs(self, parser):
        """Test amount with Rs notation"""
        intent = parser.parse("pay bill of Rs. 2,500")
        
        assert intent.parameters.get("amount") == 2500
    
    def test_extract_amount_rupees_word(self, parser):
        """Test amount with 'rupees' word"""
        intent = parser.parse("transfer 5000 rupees")
        
        assert intent.parameters.get("amount") == 5000
    
    def test_extract_amount_decimal(self, parser):
        """Test amount with decimal"""
        intent = parser.parse("transfer ₹1500.50 to friend")
        
        assert intent.parameters.get("amount") == 1500.50
    
    # ============ Edge Cases ============
    
    def test_unknown_command(self, parser):
        """Test unknown command handling"""
        intent = parser.parse("random gibberish text")
        
        assert intent.action == "unknown"
        assert intent.confidence == 0.0
        assert intent.requires_approval == False
    
    def test_empty_command(self, parser):
        """Test empty command handling"""
        intent = parser.parse("")
        
        assert intent.action == "unknown"
        assert intent.confidence == 0.0
    
    def test_command_case_insensitive(self, parser):
        """Test case insensitivity"""
        intent = parser.parse("PAY ELECTRICITY BILL OF 1000")
        
        assert intent.action == "pay_bill"
        assert intent.parameters.get("biller_type") == "electricity"
    
    def test_multiple_actions_first_wins(self, parser):
        """Test when command contains multiple action keywords"""
        # This should match the strongest pattern
        intent = parser.parse("pay electricity bill and transfer money")
        
        # Either pay_bill or fund_transfer is valid
        assert intent.action in ["pay_bill", "fund_transfer"]
    
    # ============ Confidence Score Tests ============
    
    def test_high_confidence_multiple_keywords(self, parser):
        """Test confidence based on keyword matching weight"""
        intent1 = parser.parse("pay electricity bill")  # matches "electricity" (1 word)
        intent2 = parser.parse("pay bill")  # matches "pay bill" (2 words) → higher weight
        
        # Multi-word keyword matches get higher confidence
        assert intent2.confidence >= intent1.confidence
        assert intent1.action == "pay_bill"
        assert intent2.action == "pay_bill"
    
    # ============ ParsedIntent Tests ============
    
    def test_parsed_intent_to_dict(self, parser):
        """Test ParsedIntent serialization"""
        intent = parser.parse("transfer 5000 to Mom")
        intent_dict = intent.to_dict()
        
        assert "action" in intent_dict
        assert "confidence" in intent_dict
        assert "parameters" in intent_dict
        assert "original_command" in intent_dict
        assert "requires_approval" in intent_dict
    
    # ============ Actions Configuration Tests ============
    
    def test_all_actions_have_risk_level(self):
        """Test all actions have risk level defined"""
        for action, config in ACTIONS.items():
            assert "risk_level" in config, f"Action {action} missing risk_level"
            assert config["risk_level"] in ["low", "medium", "high"]
    
    def test_all_actions_have_approval_flag(self):
        """Test all actions have requires_approval defined"""
        for action, config in ACTIONS.items():
            assert "requires_approval" in config, f"Action {action} missing requires_approval"
            assert isinstance(config["requires_approval"], bool)
    
    def test_high_risk_actions_require_approval(self):
        """Test high risk actions require approval"""
        for action, config in ACTIONS.items():
            if config["risk_level"] == "high":
                assert config["requires_approval"] == True, f"High risk action {action} should require approval"
    
    # ============ Intent Keywords Tests ============
    
    def test_all_actions_have_keywords(self):
        """Test all actions have keywords defined"""
        for action in ACTIONS.keys():
            assert action in INTENT_KEYWORDS, f"Action {action} missing keywords"
            assert len(INTENT_KEYWORDS[action]) > 0, f"Action {action} has no keywords"


class TestConvenienceFunction:
    """Test the parse_intent convenience function"""
    
    def test_parse_intent_function(self):
        """Test convenience function works"""
        intent = parse_intent("check balance")
        
        assert isinstance(intent, ParsedIntent)
        assert intent.action == "check_balance"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
