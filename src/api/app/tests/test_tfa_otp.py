"""
    2-FA OTP unit.
"""

import unittest
import time

from pyotp import TOTP


class TestOtpUnit(unittest.TestCase):
    """Check OTP unit."""

    def test_otp(self):
        """Check that OTP works correctly."""
        test_secret = "mykey"

        totp = TOTP(s=test_secret, interval=1)
        tfa_otp = totp.now()

        self.assertTrue(totp.verify(tfa_otp))
        time.sleep(2)
        self.assertFalse(totp.verify(tfa_otp))
