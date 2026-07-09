import shutil
import tempfile
import unittest

from fastapi import HTTPException

from backend.job_store import JobStore
from backend.validation_utils import coerce_ws_chain_params, validate_audio_file


class TestBackendImprovements(unittest.TestCase):
    def test_validate_audio_file_accepts_supported_extension(self):
        validate_audio_file("track.wav")

    def test_validate_audio_file_rejects_unsupported_extension(self):
        with self.assertRaises(HTTPException):
            validate_audio_file("track.txt")

    def test_coerce_ws_chain_params_converts_strings(self):
        params = {
            "use_lufs_normalize": "true",
            "comp_threshold": "-1.5",
            "mb_bypass": "false",
        }
        coerced = coerce_ws_chain_params(params)
        self.assertTrue(coerced["use_lufs_normalize"])
        self.assertEqual(coerced["comp_threshold"], -1.5)
        self.assertFalse(coerced["mb_bypass"])

    def test_job_store_persists_to_disk(self):
        tmp_dir = tempfile.mkdtemp(prefix="job-store-", dir="/tmp")
        try:
            store = JobStore(storage_dir=tmp_dir)
            store["job-1"] = {"status": "queued", "filename": "demo.wav"}
            reloaded = JobStore(storage_dir=tmp_dir)
            self.assertEqual(reloaded["job-1"]["status"], "queued")
            self.assertEqual(reloaded["job-1"]["filename"], "demo.wav")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
