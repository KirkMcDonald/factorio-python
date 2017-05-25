import json

from factorio import factory
from factorio import recipe
from factorio import solve as solve_module

def load():
    with open("data/vanilla-0.15.12.json") as f:
        data = json.load(f)
        items, recipes = recipe.get_recipe_graph(data)
        factories = factory.FactorySpec(factory.get_factories(data))
        return items, recipes, factories
# Settings:
#   Minimum assembler
#   Furnace
#   Mining productivity level
#     Burner miners?
#   Preferred fuel?
#   Coal liquefaction vs. crude oil

# Need info:
#   Assemblers
#   Water pump
#     offshore-pump entity
#       'fluid' and 'pumping_speed' attributes; not documented
#       'fluid' appears to define which fluid it produces
#       'pumping_speed' is the quantity it produces per tick
#         set to 20, or 1200/s
#       XXX: Not exposed by Lua API. Hard-code?
#   Miners?
#   Furnaces
#   Other crafting buildings.
#   Mining "recipes"; uranium ore requiring acid.
#     required_fluid, fluid_amount
#   Nuclear reactor cycle "recipe"
#     Infer from nuclear-reactor entity.
#     'burner' attribute tells tale:
#       fuel_category: "nuclear"
#       effectivity: 1
#       fuel_inventory_size: 1
#       burnt_inventory_size: 1
#       XXX: Or would if not bugged?
#     consumption: "40MW"
#     'uranium-fuel-cell' item also tells tale:
#       fuel_value: "8GJ"
#       burnt_result: "used-up-uranium-fuel-cell"
#       fuel_category: "nuclear"
#     8 GJ / 40 MW = 200 seconds

def print_solution(s, factories, products):
    totals = s.solve(products)
    recipe_width = max(len(r.name) for r in totals.totals)
    factory_width = 0
    for r in totals.totals:
        factory = factories.get_factory(r)
        if factory:
            factory_width = max(factory_width, len(factory.name))
    pairs = sorted(totals.totals.items(), key=lambda t: t[0].name)
    for recipe, rate in pairs:
        factory, count = factories.get_count(recipe, float(rate))
        if factory:
            fname = factory.name
        else:
            fname = ""
        print("{:<{rwidth}} {:>8.3f} {:<{fwidth}} {:>8.3f}".format(
                recipe.name,
                float(rate),
                fname,
                count,
                rwidth=recipe_width,
                fwidth=factory_width,
        ))

def solve(products):
    print_solution(s, factories, products)

if __name__ == "__main__":
    items, recipes, factories = load()
    s = solve_module.Solver(items.values(), recipes.values())
    oil = {items['petroleum-gas']: 45, items['heavy-oil']: 10}
    green = {items['electronic-circuit']: 1}
    red = {items['advanced-circuit']: 1}
