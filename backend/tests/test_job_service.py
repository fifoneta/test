import shutil
import tempfile
import unittest

from backend.job_service import JobService


class TestJobService(unittest.TestCase):
    def test_create_and_update_job(self):
        tmp_dir = tempfile.mkdtemp(prefix="job-service-", dir="/tmp")
        try:
            service = JobService(storage_dir=tmp_dir)
            service.create_job("job-1", {"status": "queued", "filename": "demo.wav"})
            service.update_job("job-1", status="processing", progress=42)

            job = service.get_job("job-1")
            self.assertEqual(job["status"], "processing")
            self.assertEqual(job["progress"], 42)
            self.assertEqual(job["filename"], "demo.wav")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
