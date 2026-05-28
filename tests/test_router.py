import unittest
from framework.router import Router

class TestRouter(unittest.TestCase):
    def test_route_registration(self):
        router = Router()
        router.get("/home", "HomeController@index")
        router.post("/submit", "HomeController@submit")
        
        self.assertEqual(len(router.routes), 2)
        self.assertEqual(router.routes[0]["method"], "GET")
        self.assertEqual(router.routes[0]["path"], "/home")
        self.assertEqual(router.routes[1]["method"], "POST")

    def test_route_groups_and_middlewares(self):
        router = Router()
        # Group with prefix and middleware
        router.group({"prefix": "/admin", "middleware": ["auth", "log"]}, lambda: (
            router.get("/dashboard", "AdminController@dashboard"),
            router.post("/settings", "AdminController@settings")
        ))
        
        self.assertEqual(len(router.routes), 2)
        self.assertEqual(router.routes[0]["path"], "/admin/dashboard")
        self.assertEqual(router.routes[0]["middleware"], ["auth", "log"])
        self.assertEqual(router.routes[1]["path"], "/admin/settings")

    def test_route_matching_and_parameters(self):
        router = Router()
        router.get("/user/{id}", "UserController@show")
        router.get("/post/{post_id}/comment/{comment_id}", "CommentController@show")
        
        # Match user route
        route, params = router.match("GET", "/user/42")
        self.assertIsNotNone(route)
        self.assertEqual(route["action"], "UserController@show")
        self.assertEqual(params, {"id": "42"})
        
        # Match comment route
        route, params = router.match("GET", "/post/10/comment/abc")
        self.assertIsNotNone(route)
        self.assertEqual(params, {"post_id": "10", "comment_id": "abc"})
        
        # Non-matching path
        route, params = router.match("GET", "/user/42/details")
        self.assertIsNone(route)

if __name__ == '__main__':
    unittest.main()
