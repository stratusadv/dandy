from dandy.intel.intel import BaseIntel


class AudioTranscriptionIntel(BaseIntel):
    text: str
    usage: dict


class AudioVerboseTranscriptionIntel(AudioTranscriptionIntel):
    task: str
    language: str
    duration: float


class AudioSegmentIntel(BaseIntel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class AudioSegmentsTranscriptionIntel(AudioVerboseTranscriptionIntel):
    segments: list[AudioSegmentIntel]


class AudioWordIntel(BaseIntel):
    word: str
    start: float
    end: float


class AudioWordsTranscriptionIntel(AudioWordIntel):
    words: list[AudioWordIntel]
