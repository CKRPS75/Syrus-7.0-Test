import unittest
from unittest.mock import patch

from fastapi import HTTPException

from backend.api import auth


class AuthenticationHelpersTests(unittest.TestCase):
    def test_password_hash_verifies_without_storing_plaintext(self):
        with patch.object(auth, "PASSWORD_ITERATIONS", 100_000):
            encoded = auth.hash_password("TrustRoute123")

        self.assertNotIn("TrustRoute123", encoded)
        self.assertTrue(auth.verify_password("TrustRoute123", encoded))
        self.assertFalse(auth.verify_password("wrong-password", encoded))

    def test_invalid_password_hash_is_rejected(self):
        self.assertFalse(auth.verify_password("password", "not-a-valid-hash"))

    def test_email_is_normalized_and_validated(self):
        email = auth.normalized_email("  Route.Planner@example.com ")
        self.assertEqual(email, "route.planner@example.com")
        auth.validate_email(email)

    def test_invalid_email_is_rejected(self):
        with self.assertRaises(HTTPException):
            auth.validate_email("route.planner.example.com")

    def test_password_policy_requires_letter_number_and_minimum_length(self):
        auth.validate_password("TrustRoute123")
        with self.assertRaises(HTTPException):
            auth.validate_password("letters-only")
        with self.assertRaises(HTTPException):
            auth.validate_password("short1")

    def test_missing_database_configuration_is_reported_without_success(self):
        with patch.dict("os.environ", {"DATABASE_URL": ""}):
            with self.assertRaises(HTTPException) as raised:
                with auth.get_connection():
                    self.fail("A missing database configuration must not open a connection.")
        self.assertEqual(raised.exception.status_code, 503)

    def test_password_reset_is_explicitly_unavailable_without_email_delivery(self):
        with self.assertRaises(HTTPException) as raised:
            auth.reset_password(auth.PasswordResetRequest(email="person@example.com"))
        self.assertEqual(raised.exception.status_code, 501)


if __name__ == "__main__":
    unittest.main()
