import unittest
from framework.request import Request
from framework.router import Router

class TestMethodSpoofing(unittest.TestCase):
    def test_post_spoofed_to_put(self):
        req = Request(method="POST", path="/users/1", body={"_method": "PUT", "name": "Ilham"})
        self.assertEqual(req.original_method, "POST")
        self.assertEqual(req.method, "PUT")
        self.assertEqual(req.get("name"), "Ilham")

    def test_post_spoofed_to_patch(self):
        req = Request(method="POST", path="/users/1", body={"_method": "PATCH", "status": "active"})
        self.assertEqual(req.original_method, "POST")
        self.assertEqual(req.method, "PATCH")

    def test_post_spoofed_to_delete(self):
        req = Request(method="POST", path="/users/1", body={"_method": "DELETE"})
        self.assertEqual(req.original_method, "POST")
        self.assertEqual(req.method, "DELETE")

    def test_method_override_header(self):
        req = Request(
            method="POST",
            path="/users/1",
            headers={"X-HTTP-Method-Override": "DELETE"},
            body={"id": 1}
        )
        self.assertEqual(req.method, "DELETE")

    def test_disallowed_spoofing_targets(self):
        # Disallow spoofing to GET, HEAD, or arbitrary methods
        for invalid in ("GET", "HEAD", "OPTIONS", "CUSTOM", ""):
            req = Request(method="POST", path="/test", body={"_method": invalid})
            self.assertEqual(req.method, "POST")

    def test_cannot_spoof_from_get(self):
        # A GET request must NOT be allowed to spoof method
        req = Request(method="GET", path="/users/1", query={"_method": "DELETE"}, body={"_method": "DELETE"})
        self.assertEqual(req.method, "GET")

    def test_routing_with_spoofed_request(self):
        router = Router()
        router.put("/articles/{id}", "ArticleController@update")
        router.delete("/articles/{id}", "ArticleController@destroy")
        
        # Spoofed PUT
        put_req = Request(method="POST", path="/articles/42", body={"_method": "PUT", "title": "New"})
        route, params = router.match(put_req.method, put_req.path)
        self.assertIsNotNone(route)
        self.assertEqual(route["action"], "ArticleController@update")
        self.assertEqual(params.get("id"), "42")
        
        # Spoofed DELETE
        del_req = Request(method="POST", path="/articles/42", body={"_method": "DELETE"})
        route, params = router.match(del_req.method, del_req.path)
        self.assertIsNotNone(route)
        self.assertEqual(route["action"], "ArticleController@destroy")


if __name__ == "__main__":
    unittest.main()
