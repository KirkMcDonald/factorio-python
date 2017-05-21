from factorio import item as item_module

class Ingredient:
    def __init__(self, amount, item):
        self.amount = amount
        self.item = item

    @classmethod
    def from_dict(cls, i, items):
        if "amount" in i:
            amount = i["amount"]
        else:
            amount = (i["amount_min"] + i["amount_max"]) / 2
        amount *= i.get("probability", 1)
        return cls(amount, item_module.get_item(items, i["name"]))

    def __repr__(self):
        return "%s(%d, %r)" % (type(self).__name__, self.amount, self.item.name)

PRIORITY = ['raw-wood', 'crude-oil', 'stone', 'coal', 'uranium-ore', 'iron-ore', 'copper-ore', 'water']

class RawRequirements:
    def __init__(self):
        self.reqs = {}
    
    def __repr__(self):
        return "Raw({!r})".format(self.reqs)

    def combine(self, other, factor):
        for item, value in other.reqs.items():
            self.add(item, value * factor)

    def add(self, item, value):
        old_value = self.reqs.get(item, 0)
        if old_value is CYCLE:
            return
        self.reqs[item] = old_value + value

    def set_cyclic(self, item):
        self.reqs[item] = CYCLE

    def _make_tuple(self, quantity):
        items = {i.name: i for i in self.reqs}
        return tuple(self.reqs[items[name]] / quantity if name in items else 0 for name in PRIORITY) + (sorted((i.name, value) for i, value in self.reqs.items() if i.name not in PRIORITY),)

PENDING = object()
CYCLE = object()

class Recipe:
    def __init__(self, name, category, time, ingredients, products):
        self.name = name
        self.category = category
        self.time = time
        self.ingredients = ingredients
        self.products = products
        for product in self.products:
            product.item.add_recipe(self)
        for ingredient in self.ingredients:
            ingredient.item.add_use(self)

    @classmethod
    def from_dict(cls, d, items):
        time = d["energy"]
        products = []
        for product in d["products"]:
            products.append(Ingredient.from_dict(product, items))
        ingredients = []
        for ingredient in d["ingredients"]:
            ingredients.append(Ingredient.from_dict(ingredient, items))
        return cls(d["name"], d["category"], time, ingredients, products)

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.name)

    def gives(self, item):
        for product in self.products:
            if product.item == item:
                return product.amount

    def makes_resource(self):
        return False

class ResourceRecipe(Recipe):
    """Pseudo-recipe representing resource extraction."""
    def __init__(self, item, ingredients=None):
        if ingredients is None:
            ingredients = []
        super().__init__(item.name, "mining", 0, ingredients, [Ingredient(1, item)])

    def makes_resource(self):
        return True

def ignore_recipe(d):
    """Excise the barrel-emptying recipes from the graph."""
    return d["subgroup"] == "empty-barrel"

def get_recipe_graph(data):
    recipes = {}
    items = item_module.get_items(data)
    for recipe in data["recipes"].values():
        if ignore_recipe(recipe):
            continue
        r = Recipe.from_dict(recipe, items)
        recipes[r.name] = r
    for name, item in items.items():
        if item.is_resource():
            if item.name in recipes:
                raise Exception(item.name + " already exists as recipe")
            ingredients = None
            if getattr(item, "fluid_name", None):
                ingredients = [Ingredient(item.fluid_amount//10, items[item.fluid_name])]
            r = ResourceRecipe(item, ingredients)
            recipes[r.name] = r
    return items, recipes
