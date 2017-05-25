class Module:
    """The attributes of a module item. Immutable."""
    def __init__(self, name, speed, productivity, limit):
        self.name = name
        self.speed = speed
        self.productivity = productivity
        self.limit = limit

class FactoryDef:
    """Defines the attributes of a factory entity. Immutable."""
    def __init__(self, name, categories, max_ingredients, speed, module_slots):
        self.name = name
        self.categories = set(categories)
        self.max_ing = max_ingredients
        self.speed = speed
        self.module_slots = module_slots

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.name)

    def __lt__(self, other):
        return (self.speed, self.module_slots) < (other.speed, other.module_slots)

    def make_factory(self):
        return Factory(self)

class MinerDef(FactoryDef):
    def __init__(self, name, categories, power, speed, module_slots):
        super().__init__(name, categories, 0, 0, module_slots)
        self.mining_power = power
        # Different from crafting speed.
        self.mining_speed = speed

    def __lt__(self, other):
        return (self.mining_power, self.mining_speed) < (other.mining_power, other.mining_speed)

    def make_factory(self):
        return Miner(self)

class Factory:
    """Defines the state of a specific recipe's factories."""
    def __init__(self, factory):
        self.factory = factory
        self.modules = [None] * factory.module_slots
        self.beacon_module = None
        self.beacon_count = 0

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.factory.name)

    @property
    def name(self):
        return self.factory.name

    def set_factory(self, factory):
        assert type(self.factory) == type(factory)
        assert self.factory.categories & factory.categories
        self.factory = factory
        self.modules = self.modules[:factory.module_slots] + [None] * (factory.module_slots - len(self.modules))

    def set_module(self, i, module):
        self.modules[i] = module

    def speed_effect(self):
        speed = 1
        for module in self.modules:
            if not module:
                continue
            speed += module.speed
        if self.beacon_module:
            speed += self.beacon_module.speed * self.beacon_count * 0.5
        return speed

    def prod_effect(self):
        prod = 1
        for module in self.modules:
            if not module:
                continue
            prod += module.productivity
        return prod

    def recipe_rate(self, recipe):
        """Calculates the number of times this factory will complete the recipe
        per minute."""
        return 60/recipe.time * self.factory.speed * self.speed_effect()

class Miner(Factory):
    def recipe_rate(self, recipe):
        miner = self.factory
        return 60 * (miner.mining_power - recipe.hardness) * miner.mining_speed / recipe.mining_time * self.speed_effect()

assembly_machine_categories = {
    "advanced-crafting", 
    "crafting", 
    "crafting-with-fluid",
}

class FactorySpec:
    """Contains the map from recipes to their factories."""
    def __init__(self, factories):
        self.spec = {}
        self.factories = {}
        for factory in factories:
            for category in factory.categories:
                self.factories.setdefault(category, []).append(factory)
        for factories in self.factories.values():
            factories.sort()

        self.minimum = self.factories["crafting"][0]
        self.furnace = self.factories["smelting"][-1]
        self.mining_prod = 0

    def get_factory(self, recipe):
        factory = self.spec.get(recipe)
        if factory:
            return factory
        if recipe.category is None:
            return None
        factories = self.factories[recipe.category]
        if recipe.category in assembly_machine_categories:
            for factory in factories:
                if factory < self.minimum:
                    continue
                break
        else:
            factory = factories[-1]
        self.spec[recipe] = factory.make_factory()
        return self.spec[recipe]

    def get_count(self, recipe, rate):
        factory = self.get_factory(recipe)
        if factory is None:
            return None, 0
        return factory.factory, rate / factory.recipe_rate(recipe)

def get_factories(data):
    factories = []
    for d in data["entities"].values():
        if "crafting_categories" in d and d["name"] != "player":
            factories.append(FactoryDef(
                d["name"],
                set(d["crafting_categories"]),
                d["ingredient_count"],
                d["crafting_speed"],
                d["module_inventory_size"],
            ))
        elif "mining_power" in d:
            if d["name"] == "pumpjack":
                continue
            factories.append(MinerDef(
                d["name"],
                {"mining-basic-solid"},
                d["mining_power"],
                d["mining_speed"],
                d["module_inventory_size"],
            ))
    return factories
