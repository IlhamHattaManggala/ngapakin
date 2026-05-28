import os
import unittest
from framework.database import db_manager
from framework.model import Model
from framework.schema import schema
from ngapak import Lexer, Parser, Compiler, VM

class TestORM(unittest.TestCase):
    def setUp(self):
        # Use a temporary SQLite database for testing
        self.db_path = "test_database.sqlite"
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        db_manager.db_path = self.db_path
        db_manager.close() # reset connection
        
        self.vm = VM()
        Model.active_vm = self.vm
        self.vm.globals["Model"] = Model
        self.vm.globals["schema"] = schema

    def tearDown(self):
        db_manager.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def run_source(self, source):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        compiler = Compiler()
        main_fn = compiler.compile(ast)
        self.vm.run(main_fn)

    def test_schema_and_model_crud(self):
        source = """
        # Create table
        schema.gawe("users", gawe(tabel)
            tabel.id()
            tabel.string("name")
            tabel.string("email")
            tabel.timestamps()
        rampung)
        
        # Define model class
        kelas User extends Model
            tabel = "users"
            fillable = ["name", "email"]
        rampung
        
        # Create records
        u1 = User.gawe(["name": "Ilham", "email": "ilham@example.com"])
        u2 = User.gawe(["name": "Hatta", "email": "hatta@example.com"])
        
        # Query all
        all_users = User.kabeh()
        
        # Query individual
        u = User.golek(1)
        res_name = u.name
        
        # Update record
        u.name = "Manggala"
        u.simpen()
        
        # Fetch again to verify
        u_updated = User.golek(1)
        res_updated_name = u_updated.name
        
        # Delete
        u2_fetched = User.golek(2)
        u2_fetched.busak()
        res_u2_deleted = User.golek(2)
        """
        self.run_source(source)
        
        all_users = self.vm.globals.get("all_users")
        self.assertEqual(len(all_users), 2)
        self.assertEqual(self.vm.globals.get("res_name"), "Ilham")
        self.assertEqual(self.vm.globals.get("res_updated_name"), "Manggala")
        self.assertIsNone(self.vm.globals.get("res_u2_deleted"))

    def test_orm_relationships(self):
        source = """
        # Create tables
        schema.gawe("pengguna", gawe(tabel)
            tabel.id()
            tabel.string("username")
        rampung)
        
        schema.gawe("postingan", gawe(tabel)
            tabel.id()
            tabel.integer("pengguna_id")
            tabel.string("judul")
        rampung)
        
        # Define models
        kelas Pengguna extends Model
            tabel = "pengguna"
            
            gawe postingan(isi)
                balekna isi.hasMany("Postingan")
            rampung
        rampung
        
        kelas Postingan extends Model
            tabel = "postingan"
            
            gawe penulis(isi)
                balekna isi.belongsTo("Pengguna")
            rampung
        rampung
        
        # Insert test data
        p = Pengguna.gawe(["username": "ilham"])
        p_id = p.id
        
        post1 = Postingan.gawe(["pengguna_id": p_id, "judul": "Belajar NgapakIn"])
        post2 = Postingan.gawe(["pengguna_id": p_id, "judul": "MVC Web Framework"])
        
        # Get relation
        posts = p.postingan()
        
        # Inverse relation
        writer = post1.penulis()
        res_writer_name = writer.username
        """
        self.run_source(source)
        
        posts = self.vm.globals.get("posts")
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].fields["judul"], "Belajar NgapakIn")
        self.assertEqual(posts[1].fields["judul"], "MVC Web Framework")
        self.assertEqual(self.vm.globals.get("res_writer_name"), "ilham")

if __name__ == '__main__':
    unittest.main()
