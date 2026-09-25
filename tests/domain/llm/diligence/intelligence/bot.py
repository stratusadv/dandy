from dandy import Bot


class CelestialObserverBot(Bot):
    role = 'Celestial Observer'
    task = 'You will be given a description of a celestial object and your task is to identify it.'
    guidelines = 'Provide only the name of the object as a single word.'
