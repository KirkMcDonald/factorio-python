from factorio import subgraphs
from factorio import totals as totals_module
from factorio import vectorize

class UnknownRecipe:
    """Placeholder for the production of an item with no definitive source.
    
    Only to be used in Totals objects, in the case of recipe matrices that
    could not produce a valid result. (E.g. when asking for a lot of heavy oil.)
    """
    def __init__(self, item):
        self.item = item

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.item.name)

class Solver:
    def __init__(self, items, recipes):
        groups = subgraphs.find_groups(items, recipes)
        assert len(groups) == 2
        # XXX: This is a hack. It ensures we process the uranium group before
        # the oil group, due to the dependency between them. Properly, we
        # should traverse the graph to determine this dependency.
        groups.sort(key=lambda g: any(recipe.name == 'uranium-ore' for recipe in g))
        self.matrix_solvers = [vectorize.Solver(group) for group in groups]

    def solve(self, rates):
        """Solve for the optimal production chain for a given series of outputs.

        Args:
            rates: Dict mapping {item: rate}. The products to solve for.

        Returns:
            Totals object representing all required recipe-rates. The unfinished
            attribute of this object should be empty.
        """
        unknowns = {}
        totals = totals_module.Totals()
        for item, rate in rates.items():
            sub_totals = item.produce(rate)
            totals.combine(sub_totals)
        if not totals.unfinished:
            return totals
        for solver in self.matrix_solvers:
            match = solver.match(totals.unfinished)
            if not match:
                continue
            for item in match:
                del totals.unfinished[item]
            solution = solver.solve_for(match)
            if solution is None:
                for item, rate in match.items():
                    unknown = unknowns.setdefault(item, UnknownRecipe(item))
                    totals.add(unknown, rate)
                continue
            for recipe, rate in solution.items():
                if recipe in solver.input_recipes:
                    assert len(recipe.products) == 1
                    ing = recipe.products[0]
                    sub_totals = ing.item.produce(rate * ing.amount)
                    totals.combine(sub_totals)
                else:
                    totals.add(recipe, rate)
        assert len(totals.unfinished) == 0
        return totals
