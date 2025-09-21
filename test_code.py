#!/usr/bin/env python3
"""
A sample Python file to test the PR Review Agent
This file has some intentional issues for demonstration
"""

import os
import sys
from datetime import datetime

def calculate_tax(amount, rate):
    """Calculate tax for given amount and rate"""
    # TODO: Add validation for negative amounts
    if amount < 0:
        return 0
    
    tax = amount * rate
    return tax

def process_payment(amount, card_number):
    """Process payment with card"""
    try:
        # Hardcoded API key - security issue
        api_key = "sk_test_1234567890abcdef"
        
        # Process payment
        result = payment_gateway.charge(amount, card_number, api_key)
        return result
    except Exception as e:
        print(f"Payment failed: {e}")
        return None

def validate_user_input(user_input):
    """Validate user input"""
    # This line is too long and should be broken into multiple lines for better readability
    if user_input and len(user_input) > 0 and user_input.isalnum() and not user_input.startswith('admin'):
        return True
    return False

def main():
    """Main function"""
    print("Starting payment processing...")
    
    # Test tax calculation
    tax = calculate_tax(100, 0.1)
    print(f"Tax: {tax}")
    
    # Test payment processing
    result = process_payment(50, "4111111111111111")
    if result:
        print("Payment successful")
    else:
        print("Payment failed")

if __name__ == "__main__":
    main()
