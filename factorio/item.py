class Totals:
    def __init__(self, unfinished=None):
        # Maps recipes to their required rates.
        self.totals = {}
        # Maps items to their as-yet-unfulfilled rates.
        if unfinished is None:
            unfinished = {}
        self.unfinished = unfinished

    def combine(self, other):
        for recipe, rate in other.totals.items():
            self.add(recipe, rate)
        for item, rate in other.unfinished.items():
            self.add_unfinished(item, rate)

    def add(self, recipe, rate):
        self.totals[recipe] = self.totals.get(recipe, 0) + rate

    def add_unfinished(self, item, rate):
        self.unfinished[item] = self.unfinished.get(item, 0) + rate

    def __str__(self):
        width = max(len(r.name) for r in self.totals)
        pairs = sorted(self.totals.items(), key=lambda t: t[0].name)
        parts = []
        for recipe, rate in pairs:
            parts.append("{:<{width}} {:>8.3f}\n".format(recipe.name, float(rate), width=width))
        return "".join(parts)

class Item:
    def __init__(self, name):
        self.name = name
        self.recipes = []
        self.uses = []

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.name)

    def add_recipe(self, recipe):
        self.recipes.append(recipe)

    def add_use(self, recipe):
        self.uses.append(recipe)

    def is_resource(self):
        return not self.recipes or any(r.makes_resource() for r in self.recipes)

    def produce(self, rate):
        totals = Totals()
        if len(self.recipes) > 1:
            totals.add_unfinished(self, rate)
            return totals
        recipe = self.recipes[0]
        gives = recipe.gives(self)
        rate /= gives
        totals.add(recipe, rate)
        for ing in recipe.ingredients:
            sub_totals = ing.item.produce(rate * ing.amount)
            totals.combine(sub_totals)
        return totals

class Resource(Item):
    def is_resource(self):
        return True

def get_item(items, name):
    if name in items:
        return items[name]
    else:
        item = Item(name)
        items[name] = item
        return item

def get_items(data):
    items = {"water": Resource("water")}
    for name, entity in data["entities"].items():
        category = entity.get("resource_category")
        if not category:
            continue
        items[name] = Resource(name)
    return items
