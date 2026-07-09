import os
import tempfile
import unittest

import numpy as np
import soundfile as sf

from backend.audio_service import AudioService


class TestAudioService(unittest.TestCase):
    def test_analyze_file_and_spectrum(self):
        tmp_dir = tempfile.mkdtemp(prefix="audio-service-", dir="/tmp")
        try:
            wav_path = os.path.join(tmp_dir, "tone.wav")
            sr = 16000
            t = np.linspace(0, 0.25, int(0.25 * sr), endpoint=False)
            audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
            sf.write(wav_path, audio, sr)

            service = AudioService(upload_dir=tmp_dir)
            analysis = service.analyze_file(wav_path)
            spectrum = service.spectrum_file(wav_path, n_fft=256, n_bins=16)

            self.assertIn("lufs", analysis)
            self.assertIn("peak_db", analysis)
            self.assertIn("frequencies_hz", spectrum)
            self.assertIn("magnitudes_db", spectrum)
        finally:
            for item in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, item))
            os.rmdir(tmp_dir)


if __name__ == "__main__":
    unittest.main()
