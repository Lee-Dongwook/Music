import os
import torch
import scipy.io.wavfile
from abc import ABC, abstractmethod
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import replicate

class BaseAudioEngine(ABC):
    @abstractmethod
    def generate(self, prompt: str, output_path: str) -> str:
        """프롬프트를 입력받아 지정된 경로에 오디오 파일(.wav) 저장 후 파일 경로 반환"""
        pass

class LocalMusicGenEngine(BaseAudioEngine):
    def __init__(self):
        print("[AudioEngine] Loading Local MusicGen model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        self.model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(self.device)
        print(f"[AudioEngine] Local Model loaded on {self.device}")
    
    def generate(self, prompt: str, output_path: str) -> str:
        inputs = self.processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        audio_values = self.model.generate(**inputs, max_new_tokens=256)
        sampling_rate = self.model.config.audio_encoder.sampling_rate
        audio_data = audio_values[0, 0].cpu().numpy()

        scipy.io.wavfile.write(output_path, rate=sampling_rate, data=audio_data)
        return output_path

class ReplicateAudioEngine(BaseAudioEngine):
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN 환경 변수가 설정되지 않았습니다.")
    
    def generate(self, prompt: str, output_path: str) -> str:
        output = replicate.run(
            "meta/musicgen:b05b1d413d0a133145060b0d952a2223838038b556b6a67f0f62b2bc8e2025d5",
            input={"prompt": prompt, "duration": 10}
        )

        import requests
        response = requests.get(str(output))
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path

def get_audio_engine() -> BaseAudioEngine:
    engine_type = os.getenv("AUDIO_ENGINE_TYPE", "local").lower()

    if engine_type == "replicate":
        return ReplicateAudioEngine()
    return LocalMusicGenEngine()
