# Unit & Integration tests for Multi-Language Project Scaffolding & Dynamic Path Resolution

import unittest
import os
import shutil
import tempfile
import sys
from framework.paths import (
    normalize_language,
    detect_project_language,
    get_path,
    get_controllers_path,
    get_models_path,
    get_views_path,
    get_routes_path,
    get_public_path,
    get_migrations_path,
    get_jobs_path,
    get_seeders_path,
    get_route_files,
    get_seeder_file,
    PATHS_CONFIG
)
import ngapakin

class TestMultilingualStructure(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="ngpk_test_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_normalize_language(self):
        # Ngapak aliases
        self.assertEqual(normalize_language("ngapak"), "ngapak")
        self.assertEqual(normalize_language("Ngapak"), "ngapak")
        self.assertEqual(normalize_language("ngpk"), "ngapak")
        self.assertEqual(normalize_language("NGPK"), "ngapak")

        # Indonesia aliases
        self.assertEqual(normalize_language("indonesia"), "indonesia")
        self.assertEqual(normalize_language("Indonesia"), "indonesia")
        self.assertEqual(normalize_language("IDN"), "indonesia")
        self.assertEqual(normalize_language("idn"), "indonesia")
        self.assertEqual(normalize_language("id"), "indonesia")

        # English aliases
        self.assertEqual(normalize_language("english"), "english")
        self.assertEqual(normalize_language("English"), "english")
        self.assertEqual(normalize_language("EN"), "english")
        self.assertEqual(normalize_language("en"), "english")
        self.assertEqual(normalize_language("inggris"), "english")
        self.assertEqual(normalize_language("Inggris"), "english")
        self.assertEqual(normalize_language(""), "english")
        self.assertEqual(normalize_language(None), "english")

    def test_scaffold_ngapak_project(self):
        project_path = os.path.join(self.test_dir, "toko_ngapak")
        ngapakin.create_new_project(project_path, language="ngapak")

        # Verify folders exist
        self.assertTrue(os.path.isdir(os.path.join(project_path, "jeroan/Pangatur")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "jeroan/Wujud")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "jeroan/Pencegat")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "jeroan/Gawean")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "lumbung/owahan")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "lumbung/bibit")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "dalan")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "sawangan")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "njobo/css")))

        # Verify key files
        self.assertTrue(os.path.isfile(os.path.join(project_path, "dalan/web.ngpk")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, "dalan/api.ngpk")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, "jeroan/Pangatur/HomeController.ngpk")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, "sawangan/layout.nview")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, "sawangan/index.nview")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, ".env")))

        # Verify dynamic detection
        detected = detect_project_language(project_path)
        self.assertEqual(detected, "ngapak")

        ctrl_path = get_controllers_path(project_path)
        self.assertEqual(os.path.normpath(ctrl_path), os.path.normpath(os.path.join(project_path, "jeroan/Pangatur")))

        view_path = get_views_path(project_path)
        self.assertEqual(os.path.normpath(view_path), os.path.normpath(os.path.join(project_path, "sawangan")))

        pub_path = get_public_path(project_path)
        self.assertEqual(os.path.normpath(pub_path), os.path.normpath(os.path.join(project_path, "njobo")))

        r_files = get_route_files(project_path)
        self.assertEqual(len(r_files), 2)
        self.assertTrue(any("dalan" in f for f in r_files))

    def test_scaffold_indonesia_project(self):
        project_path = os.path.join(self.test_dir, "toko_indonesia")
        ngapakin.create_new_project(project_path, language="indonesia")

        # Verify folders exist
        self.assertTrue(os.path.isdir(os.path.join(project_path, "aplikasi/Pengendali")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "aplikasi/Model")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "aplikasi/Penyaring")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "aplikasi/Tugas")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "basisdata/migrasi")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "basisdata/seeder")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "rute")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "tampilan")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "publik/css")))

        # Verify key files
        self.assertTrue(os.path.isfile(os.path.join(project_path, "rute/web.ngpk")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, "rute/api.ngpk")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, "aplikasi/Pengendali/HomeController.ngpk")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, "tampilan/layout.nview")))
        self.assertTrue(os.path.isfile(os.path.join(project_path, "tampilan/index.nview")))

        # Verify dynamic detection
        detected = detect_project_language(project_path)
        self.assertEqual(detected, "indonesia")

        ctrl_path = get_controllers_path(project_path)
        self.assertEqual(os.path.normpath(ctrl_path), os.path.normpath(os.path.join(project_path, "aplikasi/Pengendali")))

        view_path = get_views_path(project_path)
        self.assertEqual(os.path.normpath(view_path), os.path.normpath(os.path.join(project_path, "tampilan")))

        pub_path = get_public_path(project_path)
        self.assertEqual(os.path.normpath(pub_path), os.path.normpath(os.path.join(project_path, "publik")))

    def test_scaffold_english_default_project(self):
        project_path = os.path.join(self.test_dir, "toko_english")
        ngapakin.create_new_project(project_path, language="english")

        # Verify folders exist
        self.assertTrue(os.path.isdir(os.path.join(project_path, "app/Controllers")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "app/Models")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "database/migrations")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "routes")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "resources/views")))
        self.assertTrue(os.path.isdir(os.path.join(project_path, "public")))

        # Verify dynamic detection
        detected = detect_project_language(project_path)
        self.assertEqual(detected, "english")

        ctrl_path = get_controllers_path(project_path)
        self.assertEqual(os.path.normpath(ctrl_path), os.path.normpath(os.path.join(project_path, "app/Controllers")))

if __name__ == "__main__":
    unittest.main()
