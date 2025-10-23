import random

class RegionGenerator:
    REGIONS = ["kerala", "Barcelona", "Madrid", "Valencia", "Delhi", "New York", "Los Angeles" ]
    @staticmethod

    def assign_random_region() -> str:
        return random.choice(RegionGenerator.REGIONS)