"""Validates actual Windows CPU model loading/inference; synthetic silence, no teaching claims."""
import numpy as np
from faster_whisper import WhisperModel
model=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=2)
segments,info=model.transcribe(np.zeros(16000,dtype=np.float32),language='en',vad_filter=True)
assert list(segments)==[]
print('PASS: CPU base.en model loaded and silence inference completed. This is not a real-lesson accuracy test.')
