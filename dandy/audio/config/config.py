# from dandy.core.config.config import BaseConfig
# from dandy.http.intelligence.intel import HttpResponseIntel
#
#
# class AudioConfig(BaseConfig):
#     type_: str = 'AUDIO'
#
#     def __post_init__(self):
#         self.http_request_intel.url.path_parameters = [
#             'v1',
#             'audio',
#             'transcriptions'
#         ]
#
#     @staticmethod
#     def get_response_content(response_intel: HttpResponseIntel) -> str:
#         return response_intel.json_data['choices'][0]['message']['content']
