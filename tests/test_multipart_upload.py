import os
import shutil
import unittest
from framework.request import Request
from framework.upload import UploadedFile, PayloadTooLargeError

class TestMultipartUpload(unittest.TestCase):
    def setUp(self):
        self.upload_dir = os.path.abspath("test_uploads")
        if os.path.exists(self.upload_dir):
            shutil.rmtree(self.upload_dir, ignore_errors=True)
        os.makedirs(self.upload_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.upload_dir):
            shutil.rmtree(self.upload_dir, ignore_errors=True)

    def test_multipart_parsing_text_and_files(self):
        boundary = "---------------------------974767299852498929531610575"
        body_parts = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="username"\r\n\r\n'
            f"ilham_hatta\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="avatar"; filename="profile.png"\r\n'
            f"Content-Type: image/png\r\n\r\n"
            f"FAKE_IMAGE_BINARY_DATA_12345\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }

        body, files = Request.parse_payload(headers, body_parts)
        
        # Verify text field
        self.assertIn("username", body)
        self.assertEqual(body["username"], "ilham_hatta")
        
        # Verify file field
        self.assertIn("avatar", files)
        file_obj = files["avatar"]
        self.assertIsInstance(file_obj, UploadedFile)
        self.assertEqual(file_obj.client_filename, "profile.png")
        self.assertEqual(file_obj.filename, "profile.png")
        self.assertEqual(file_obj.content, b"FAKE_IMAGE_BINARY_DATA_12345")
        self.assertEqual(file_obj.size, len(b"FAKE_IMAGE_BINARY_DATA_12345"))
        self.assertEqual(file_obj.content_type, "image/png")

    def test_file_save_and_path_traversal_prevention(self):
        file_obj = UploadedFile(
            client_filename="../../evil_exploit.php",
            content=b"<?php echo 'bad'; ?>"
        )
        
        # Verify client filename is kept for reference, but internal filename is sanitized!
        self.assertEqual(file_obj.client_filename, "../../evil_exploit.php")
        self.assertNotIn("..", file_obj.filename)
        self.assertNotIn("/", file_obj.filename)
        self.assertNotIn("\\", file_obj.filename)

        # Save to test directory
        saved_path = file_obj.save(self.upload_dir)
        self.assertTrue(os.path.exists(saved_path))
        # Ensure it is strictly inside upload_dir
        self.assertTrue(os.path.abspath(saved_path).startswith(self.upload_dir))

        # Explicit attempt to pass dangerous custom_filename with traversal
        with self.assertRaises(ValueError):
            file_obj.save(self.upload_dir, custom_filename="../../../outside.txt")

    def test_file_overwrite_protection(self):
        f1 = UploadedFile(client_filename="document.pdf", content=b"first")
        f2 = UploadedFile(client_filename="document.pdf", content=b"second")
        
        path1 = f1.save(self.upload_dir)
        path2 = f2.save(self.upload_dir, overwrite=False)
        
        self.assertNotEqual(path1, path2)
        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))
        
        with open(path1, "rb") as f:
            self.assertEqual(f.read(), b"first")
        with open(path2, "rb") as f:
            self.assertEqual(f.read(), b"second")

    def test_payload_size_limit_rejection(self):
        max_size = 500  # 500 bytes limit
        oversized_data = b"A" * 1000
        headers = {"Content-Type": "application/octet-stream"}

        with self.assertRaises(PayloadTooLargeError):
            Request.parse_payload(headers, oversized_data, max_size=max_size)

    def test_json_and_urlencoded_payload_parsing(self):
        # JSON
        json_headers = {"Content-Type": "application/json"}
        json_data = b'{"name": "Larapak", "version": "1.0.5"}'
        body, files = Request.parse_payload(json_headers, json_data)
        self.assertEqual(body.get("name"), "Larapak")
        self.assertEqual(body.get("version"), "1.0.5")
        self.assertEqual(len(files), 0)

        # Form urlencoded
        form_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        form_data = b"name=Ilham&skills=python&skills=ngapak"
        body, files = Request.parse_payload(form_headers, form_data)
        self.assertEqual(body.get("name"), "Ilham")
        self.assertEqual(body.get("skills"), ["python", "ngapak"])
        self.assertEqual(len(files), 0)

    def test_request_integration(self):
        boundary = "----TestBoundary"
        body_parts = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="title"\r\n\r\n'
            f"My Document\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="attachment"; filename="notes.txt"\r\n'
            f"Content-Type: text/plain\r\n\r\n"
            f"Sample text\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        parsed_body, parsed_files = Request.parse_payload(headers, body_parts)

        req = Request(
            method="POST",
            path="/upload",
            headers=headers,
            body=parsed_body,
            files=parsed_files
        )

        self.assertEqual(req.input("title"), "My Document")
        self.assertTrue(req.has_file("attachment"))
        self.assertFalse(req.has_file("nonexistent"))
        uploaded = req.file("attachment")
        self.assertEqual(uploaded.filename, "notes.txt")
        self.assertEqual(uploaded.content, b"Sample text")


if __name__ == "__main__":
    unittest.main()
