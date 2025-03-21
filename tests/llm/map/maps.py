from dandy.llm.map.llm_map import BaseLlmMap


class FunLlmMap(BaseLlmMap):
    config = 'PHI_4_14B'
    map = {
        'someone that needs a laugh and needs clowns': 113,
        'someone is interested in seeing animals': 782,
        'someone looking for something more technical': 927,
        'someone who would be glad to get a free puppies': 391,
    }
