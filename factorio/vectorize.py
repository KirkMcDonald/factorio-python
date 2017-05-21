import itertools

import sympy

# XXX: Do this better; fine for now.
PRIORITY = ["steam", "crude-oil", "coal", "water"]

class Solver:
    def __init__(self, recipes):
        recipes = list(recipes)
        products = {ing.item for recipe in recipes for ing in recipe.products}
        self.outputs = {item for item in products if len(item.recipes) > 1}
        ingredients = {ing.item for recipe in recipes for ing in recipe.ingredients}
        inputs = ingredients - products
        self.input_recipes = []
        for item in inputs:
            assert len(item.recipes) == 1
            recipe = item.recipes[0]
            self.input_recipes.append(recipe)
        all_recipes = recipes + self.input_recipes
        items = list(products | ingredients)
        recipe_map = {recipe.name: recipe for recipe in self.input_recipes}
        self.priority = [recipe_map[name] for name in PRIORITY if name in recipe_map]
        assert len(all_recipes) >= len(items)

        item_indexes = {item: index for index, item in enumerate(items)}
        recipe_indexes = {recipe: index for index, recipe in enumerate(all_recipes)}
        recipe_matrix = sympy.zeros(len(items), len(all_recipes))
        for i, recipe in enumerate(recipes):
            for ingredient in recipe.ingredients:
                j = item_indexes[ingredient.item]
                recipe_matrix[j, i] -= ingredient.amount
            for ingredient in recipe.products:
                j = item_indexes[ingredient.item]
                recipe_matrix[j, i] += ingredient.amount
        for i, recipe in enumerate(self.input_recipes, start=len(recipes)):
            for ingredient in recipe.products:
                j = item_indexes[ingredient.item]
                recipe_matrix[j, i] += ingredient.amount
        self.matrix = recipe_matrix
        self.items = item_indexes
        self.recipes = recipe_indexes

    def match(self, products):
        result = {}
        for item, rate in products.items():
            if item in self.outputs:
                result[item] = rate
        return result

    def solve_for(self, products):
        want = sympy.zeros(len(self.items), 1)
        for item, amount in products.items():
            if item in self.items:
                want[self.items[item]] = amount
        A = self.matrix.row_join(want)
        product_recipes = len(self.recipes) - len(self.input_recipes)
        zero_count = len(self.recipes) - len(self.items)
        zeros = sympy.zeros(len(self.items), 1)
        solutions = []
        recipes = sorted(self.recipes, key=self.recipes.get)
        # XXX: More aggressive strategies for excluding possible combinations
        # are possible. This fairly naive solution will yield a correct result,
        # but will waste a lot of effort in the process.
        for indexes in itertools.combinations(range(product_recipes), zero_count):
            A_prime = A[:, :]
            for index in indexes:
                A_prime[:, index] = zeros
            result, pivots = A_prime.rref()
            rates = [0] * len(self.recipes)
            for row, col in enumerate(pivots):
                rates[col] = result[row, -1]
            if any(x < 0 for x in rates):
                continue
            solution = {}
            for recipe, rate in zip(recipes, rates):
                if rate:
                    solution[recipe] = rate
            solutions.append(solution)
        solutions.sort(key=lambda s: [float(s.get(item, 0)) for item in self.priority])
        # Not all solutions are possible.
        if len(solutions) == 0:
            return None
        return solutions[0]
