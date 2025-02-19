from typing_extensions import List

from dandy.intel import BaseIntel


class CookieRecipeIngredientIntel(BaseIntel):
    name: str
    unit_type: str
    quantity: float


class CookieRecipeIntel(BaseIntel):
    name: str
    description: str
    ingredients: List[CookieRecipeIngredientIntel]
    instructions: str


