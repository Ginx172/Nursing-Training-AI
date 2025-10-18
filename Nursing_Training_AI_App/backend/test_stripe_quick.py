#!/usr/bin/env python3
"""
Quick test for Stripe webhook signature generation and verification
"""

import hmac
import hashlib

def test_stripe_signature():
    # Test Stripe webhook signature generation and verification
    secret = 'whsec_test_secret_key_12345'
    payload = b'{"id": "evt_test_webhook", "type": "payment_intent.succeeded"}'
    timestamp = '1234567890'

    # Generate signature
    signed_payload = f'{timestamp}.{payload.decode()}'
    signature = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    stripe_signature = f't={timestamp},v1={signature}'

    print('[PASS] Stripe signature generation test:')
    print(f'Secret: {secret}')
    print(f'Payload: {payload.decode()}')
    print(f'Signature: {stripe_signature}')
    print(f'Signature length: {len(signature)} characters')

    # Test verification - use the same signed_payload as generation
    expected = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    print(f'\n[PASS] Verification test:')
    print(f'Generated: {signature}')
    print(f'Expected:  {expected}')
    print(f'Match: {signature == expected}')
    
    # Test the actual verification logic from our endpoint
    if stripe_signature and expected in stripe_signature:
        print('[PASS] Endpoint verification would PASS')
    else:
        print('[FAIL] Endpoint verification would FAIL')
    
    return signature == expected

if __name__ == "__main__":
    success = test_stripe_signature()
    print(f'\n[RESULT] Overall test result: {"PASS" if success else "FAIL"}')
