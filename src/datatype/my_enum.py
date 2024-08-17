from enum import Enum


class PFC(Enum):
    Protein = 1
    Fat = 2
    Carbo = 3


class TableName(Enum):
    FOODDATA = "FoodData"
    COOKING_FOOD_DATA = "CookingFoodData"
    COOKING = "Cooking"
    COOKING_HISTORY = "CookingHistory"
    REFRIGERATOR = "Refrigerator"
    SHOPPING_FOOD_DATA = "ShoppingFoodData"
    SHOPPING_HISTORY = "ShoppingHistory"
