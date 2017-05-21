import json

from factorio import recipe
from factorio import solve

def load():
    with open("data/vanilla-0.15.12.json") as f:
        return recipe.get_recipe_graph(json.load(f))
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

if __name__ == "__main__":
    items, recipes = load()
    s = solve.Solver(items.values(), recipes.values())
    oil = {items['petroleum-gas']: 45, items['heavy-oil']: 10}
    green = {items['electronic-circuit']: 1}
    red = {items['advanced-circuit']: 1}
