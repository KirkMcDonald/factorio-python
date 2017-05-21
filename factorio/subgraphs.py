def find_groups(items, recipes):
    candidates = set()
    for item in items:
        if len(item.recipes) > 1:
            candidates.add(item)
    item_sets = []
    for item in candidates:
        group = set(item.recipes)
        for recipe in item.recipes:
            for ing in recipe.ingredients:
                if ing.item in candidates:
                    group.update(ing.item.recipes)
        if group:
            item_sets.append(group)

    groups = []
    while item_sets:
        item_set = item_sets.pop()
        for group in item_sets + groups:
            if item_set & group:
                group.update(item_set)
                break
        else:
            groups.append(item_set)

    return groups
