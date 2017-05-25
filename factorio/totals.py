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
