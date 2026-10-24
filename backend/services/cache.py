

class PreScoringCache:
    def __init__(self):
        self.cache = {}
    
    def set(self, application_id : int, data : dict):
        self.cache[application_id] = data

    def get(self, application_id : int):
        return self.cache.get(application_id)

    def delete_cache(self, application_id: int):
        self.cache.pop(application_id, None)

pre_scoring_cache = PreScoringCache()
