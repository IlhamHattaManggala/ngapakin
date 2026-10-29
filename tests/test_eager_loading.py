import os
import unittest
from framework.database import db_manager
from framework.model import Model
from framework.schema import schema
from ngapak import VM

class TestEagerLoading(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_eager_loading.sqlite"
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        db_manager.db_path = self.db_path
        db_manager.close()

        self.vm = VM()
        Model.active_vm = self.vm
        self.vm.globals["Model"] = Model
        self.vm.globals["schema"] = schema

        # Setup schema: users and posts
        schema.gawe("users", lambda t: (t.id(), t.string("name"), t.timestamps()))
        schema.gawe("posts", lambda t: (t.id(), t.integer("user_id"), t.string("title"), t.timestamps()))

        class User(Model):
            tabel = "users"
            fillable = ["name"]

            def posts(self):
                return self.hasMany("Post")

        class Post(Model):
            tabel = "posts"
            fillable = ["user_id", "title"]

            def author(self):
                return self.belongsTo("User")

        self.User = User
        self.Post = Post
        self.vm.globals["User"] = User
        self.vm.globals["Post"] = Post

        # Seed data: 5 users, each with 2 posts
        for i in range(1, 6):
            User.gawe({"name": f"User_{i}"})
            Post.gawe({"user_id": i, "title": f"Post_{i}_A"})
            Post.gawe({"user_id": i, "title": f"Post_{i}_B"})

    def tearDown(self):
        db_manager.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def test_lazy_loading_produces_n_plus_one_queries(self):
        db_manager.reset_query_log()
        users = self.User.kabeh()
        self.assertEqual(len(users), 5)
        # 1 query for users
        self.assertEqual(db_manager.query_count, 1)

        # Calling relation on each user triggers 1 query per user (N+1 queries!)
        all_post_titles = []
        for u in users:
            posts = u.posts()
            all_post_titles.extend([p.title for p in posts])

        self.assertEqual(len(all_post_titles), 10)
        # 1 initial query + 5 relation queries = 6 queries
        self.assertEqual(db_manager.query_count, 6)

    def test_eager_loading_has_many_eliminates_n_plus_one(self):
        db_manager.reset_query_log()

        # Eager load 'posts'
        users = self.User.with_("posts").kabeh()
        self.assertEqual(len(users), 5)

        # EXACTLY 2 queries: 1 for users, 1 batch query for all posts!
        self.assertEqual(db_manager.query_count, 2)

        # Accessing posts on each user executes ZERO additional queries!
        all_post_titles = []
        for u in users:
            posts = u.posts()
            all_post_titles.extend([p.title for p in posts])

        self.assertEqual(len(all_post_titles), 10)
        # Query count remains 2!
        self.assertEqual(db_manager.query_count, 2)

    def test_eager_loading_belongs_to(self):
        db_manager.reset_query_log()

        # Eager load 'author'
        posts = self.Post.with_("author").kabeh()
        self.assertEqual(len(posts), 10)

        # EXACTLY 2 queries: 1 for posts, 1 batch query for users
        self.assertEqual(db_manager.query_count, 2)

        # Accessing author on all 10 posts executes ZERO additional queries!
        author_names = []
        for p in posts:
            author = p.author()
            self.assertIsNotNone(author)
            author_names.append(author.name)

        self.assertEqual(len(author_names), 10)
        self.assertEqual(db_manager.query_count, 2)

    def test_eager_loading_empty_records(self):
        db_manager.reset_query_log()
        # Query matching no records
        users = self.User.with_("posts").nek("name", "=", "NonExistent").kabeh()
        self.assertEqual(len(users), 0)
        # Only 1 query executed, no useless child query
        self.assertEqual(db_manager.query_count, 1)


if __name__ == "__main__":
    unittest.main()
