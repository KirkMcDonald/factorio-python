from factorio import totals as totals_module

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
        totals = totals_module.Totals()
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
