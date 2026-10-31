# Unit tests for Ngapak CLI Aliases and Scaffolding commands

import unittest
import os
import shutil
import tempfile
import sys
from ngapakin import NGAPAK_COMMAND_ALIASES

class TestCLIAliases(unittest.TestCase):
    def test_ngapak_aliases_coverage(self):
        # Generator aliases
        self.assertEqual(NGAPAK_COMMAND_ALIASES["gawe:pangatur"], "make:controller")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["gawe:wujud"], "make:model")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["gawe:migrasi"], "make:migration")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["gawe:pencegat"], "make:middleware")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["gawe:gawean"], "make:job")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["gawe:bibit"], "make:seeder")

        # Proyek & server
        self.assertEqual(NGAPAK_COMMAND_ALIASES["anyar"], "new")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["ladeni"], "serve")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["dalan:daptar"], "route:list")

        # Database & migrasi
        self.assertEqual(NGAPAK_COMMAND_ALIASES["migrasi"], "migrate")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["munggah"], "migrate")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["migrasi:anyar"], "migrate:fresh")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["migrasi:status"], "migrate:status")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["mudhun"], "rollback")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["bibiti"], "db:seed")

        # Frontend & antrean
        self.assertEqual(NGAPAK_COMMAND_ALIASES["rikat:rakit"], "css:build")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["rikat:pantau"], "css:watch")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["coba"], "test")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["gawean:tandang"], "queue:work")
        self.assertEqual(NGAPAK_COMMAND_ALIASES["resik:cache"], "cache:clear")

if __name__ == "__main__":
    unittest.main()

