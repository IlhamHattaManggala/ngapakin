# Unit tests for Rate Limiting / Throttle Middleware

import unittest
import os
import json
from framework.middleware import MiddlewarePipeline
from framework.request import Request
from framework.response import Response
from framework.cache import Cache
from ngapak.vm import VM

class TestThrottleMiddleware(unittest.TestCase):
    def setUp(self):
        self.cache = Cache()
        self.cache.clear()
        self.pipeline = MiddlewarePipeline("app/Middleware", VM())

    def tearDown(self):
        self.cache.clear()

    def test_throttle_allows_requests_under_limit(self):
        req = Request(method="GET", path="/api/data", headers={"X-Forwarded-For": "192.168.1.50"})
        res = Response()

        def controller_destination(r, s):
            return s.json({"message": "sukses"})

        # Run 3 requests with limit 5
        for i in range(3):
            final_res = self.pipeline.execute_chain(["throttle:5,1"], req, res, controller_destination)
            self.assertEqual(final_res.status, 200)
            self.assertEqual(final_res.headers.get("X-RateLimit-Limit"), "5")
            self.assertEqual(final_res.headers.get("X-RateLimit-Remaining"), str(5 - (i + 1)))

    def test_throttle_blocks_requests_over_limit_with_429(self):
        req = Request(
            method="GET",
            path="/api/pesan",
            headers={"X-Forwarded-For": "10.0.0.1", "Accept": "application/json"}
        )
        res = Response()

        def destination(r, s):
            return s.json({"ok": True})

        # Hit 2 allowed requests
        self.pipeline.execute_chain(["throttle:2,1"], req, res, destination)
        self.pipeline.execute_chain(["throttle:2,1"], req, res, destination)

        # 3rd request must be blocked
        blocked_res = self.pipeline.execute_chain(["throttle:2,1"], req, res, destination)
        self.assertEqual(blocked_res.status, 429)
        self.assertIn("Retry-After", blocked_res.headers)
        self.assertEqual(blocked_res.headers.get("X-RateLimit-Remaining"), "0")

        data = json.loads(blocked_res.content)
        self.assertEqual(data["status"], "salah")
        self.assertEqual(data["code"], 429)

if __name__ == "__main__":
    unittest.main()
