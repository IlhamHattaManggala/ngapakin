import unittest
from framework.csrf import CSRF, CSRFException
from framework.session import Session
from framework.request import Request

class TestCSRFProtection(unittest.TestCase):
    def setUp(self):
        CSRF.clear_exemptions()
        self.session = Session("test_csrf_session")
        self.token = CSRF.token(self.session)

    def test_safe_methods_bypass_csrf(self):
        # GET, HEAD, OPTIONS should not require CSRF token
        for method in ("GET", "HEAD", "OPTIONS"):
            req = Request(method=method, path="/dashboard")
            self.assertTrue(CSRF.verify(req, self.session))

    def test_valid_csrf_token_in_body(self):
        req = Request(
            method="POST",
            path="/submit",
            body={"_token": self.token, "username": "ilham"}
        )
        self.assertTrue(CSRF.verify(req, self.session))

    def test_valid_csrf_token_in_headers(self):
        req = Request(
            method="POST",
            path="/api/data",
            headers={"X-CSRF-TOKEN": self.token},
            body={"key": "val"}
        )
        self.assertTrue(CSRF.verify(req, self.session))

    def test_missing_csrf_token_raises_exception(self):
        req = Request(
            method="POST",
            path="/transfer",
            body={"amount": 1000}
        )
        with self.assertRaises(CSRFException):
            CSRF.verify(req, self.session)

    def test_invalid_csrf_token_raises_exception(self):
        req = Request(
            method="POST",
            path="/transfer",
            body={"_token": "tampered_invalid_token", "amount": 1000}
        )
        with self.assertRaises(CSRFException):
            CSRF.verify(req, self.session)

    def test_csrf_token_from_different_session_rejected(self):
        other_session = Session("other_session_456")
        other_token = CSRF.token(other_session)
        
        req = Request(
            method="POST",
            path="/action",
            body={"_token": other_token}
        )
        # Attempting to use other_session's token with self.session must be rejected
        with self.assertRaises(CSRFException):
            CSRF.verify(req, self.session)

    def test_explicit_route_exemption(self):
        CSRF.exempt("/webhook/stripe")
        CSRF.exempt("/api/public/*")
        
        req1 = Request(method="POST", path="/webhook/stripe", body={"event": "charge"})
        self.assertTrue(CSRF.verify(req1, self.session))
        
        req2 = Request(method="POST", path="/api/public/contact", body={"msg": "hello"})
        self.assertTrue(CSRF.verify(req2, self.session))
        
        # Non-exempt routes still protected
        req3 = Request(method="POST", path="/api/private/data", body={"msg": "secret"})
        with self.assertRaises(CSRFException):
            CSRF.verify(req3, self.session)

    def test_csrf_applies_to_spoofed_methods(self):
        # A form POST spoofed to DELETE or PUT still requires CSRF
        for spoofed_method in ("PUT", "PATCH", "DELETE"):
            req = Request(
                method="POST",
                path="/resource/1",
                body={"_method": spoofed_method} # missing _token
            )
            self.assertEqual(req.method, spoofed_method)
            with self.assertRaises(CSRFException):
                CSRF.verify(req, self.session)

            # With valid token, it succeeds
            req_valid = Request(
                method="POST",
                path="/resource/1",
                body={"_method": spoofed_method, "_token": self.token}
            )
            self.assertTrue(CSRF.verify(req_valid, self.session))


if __name__ == "__main__":
    unittest.main()
