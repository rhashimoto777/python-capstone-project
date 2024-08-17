from enum import Enum


class PFC(Enum):
    Protein = 1
    Fat = 2
    Carbo = 3


class TableName(Enum):
    FoodData = "FoodData"
    CookingFoodData = "CookingFoodData"
    Cooking = "Cooking"
    CookingHistory = "CookingHistory"
    Refrigerator = "Refrigerator"
    ShoppingFoodData = "ShoppingFoodData"
    ShoppingHistory = "ShoppingHistory"


class DataBaseFileCommand(Enum):
    DeleteDB_and_CreateBlankDB = 1
    DeleteDB_and_RestoreFromBackup = 2
    OverwriteBackupWithCurrentDB = 3
