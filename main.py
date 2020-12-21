import itertools
import logging
from logging.config import fileConfig
import re
from operator import concat, itemgetter
from typing import TextIO

fileConfig("log.ini")

logger = logging.getLogger("dev")


def get_intput_data(filename: str) -> tuple[list[list[str]], list[list[str]]]:
    f: TextIO = open(filename)

    incredients_list: list[list[str]] = []
    allergens_list: list[list[str]] = []

    for line in f.readlines():
        match = re.search(r"(.+)\((.+)\)", line)

        incredients: list[str] = match.group(1).strip().split(" ")
        incredients_list.append(incredients)

        allergens: list[str] = list(map(lambda s: s.strip(), match.group(2).replace("contains", "").strip().split(",")))
        allergens_list.append(allergens)

    f.close()

    return incredients_list, allergens_list


def build_allergens_dict(ingredients_list: list[list[str]], allergens_list: list[list[str]]) -> dict[
    str, list[list[str]]]:
    result_dict: dict[str, list[list[str]]] = {}
    for i, ingredients in enumerate(ingredients_list):
        for allergen in allergens_list[i]:
            tmp_list = result_dict.get(allergen, [])
            tmp_list.append(ingredients)
            result_dict[allergen] = tmp_list
    return result_dict


def intersection_of_lists(list_of_lists: list[list[str]]) -> list[str]:
    current_set: set[str] = set(list_of_lists[0])
    for single_list in list_of_lists[1:]:
        current_set = current_set & set(single_list)
    return list(current_set)


def build_possible_allergen_ingredient_dict(ingredients_list: list[list[str]],
                                            allergens_list: list[list[str]]) -> dict[str, list[str]]:
    allergens_dict: dict[str, list[list[str]]] = build_allergens_dict(ingredients_list, allergens_list)
    intersection_allergens_dict: dict[str, list[str]] = {}

    for allergen, ingredients_list_per_allergen in allergens_dict.items():
        intersection_allergens_dict[allergen] = intersection_of_lists(ingredients_list_per_allergen)

    return intersection_allergens_dict


def solution_part_1(filename: str):
    ingredients_list, allergens_list = get_intput_data(filename)

    all_ingredients = list(set(itertools.chain(*[ingredients for ingredients in ingredients_list])))

    intersection_allergens_dict = build_possible_allergen_ingredient_dict(ingredients_list, allergens_list)

    for intersection_list in intersection_allergens_dict.values():
        for ingredient in intersection_list:
            if ingredient in all_ingredients:
                all_ingredients.remove(ingredient)

    count: int = 0
    for ingredient in all_ingredients:
        for ingredients in ingredients_list:
            if ingredient in ingredients:
                count += 1
    logger.debug(count)
    return count


def delete_cycle(intersection_allergens_list: list[tuple[str, list[str]]], i: int):
    delete_key: str = intersection_allergens_list[i][1][0]

    for allergen, ingredients in intersection_allergens_list[i + 1:]:
        if delete_key in ingredients:
            ingredients.remove(delete_key)


def solution_part_2(filename: str) -> str:
    ingredients_list, allergens_list = get_intput_data(filename)

    intersection_allergens_dict = build_possible_allergen_ingredient_dict(ingredients_list, allergens_list)

    intersection_allergens_list: list[tuple[str, list[str]]] = [(allergen, ingredients) for allergen, ingredients
                                                                in intersection_allergens_dict.items()]

    for i in range(len(intersection_allergens_list)):
        intersection_allergens_list.sort(key=lambda t: len(t[1]))

        for allergen, ingredients in intersection_allergens_list:
            logger.debug(f"{allergen}: {ingredients}")

        delete_cycle(intersection_allergens_list, i)

    intersection_allergens_list.sort(key=itemgetter(0))

    for allergen, ingredients in intersection_allergens_list:
        logger.debug(f"{allergen}: {ingredients}")

    return ",".join([ingredients[0] for allergen, ingredients in intersection_allergens_list])


if __name__ == '__main__':
    logger.debug(solution_part_1("inputData.txt"))
    logger.debug(solution_part_2("inputData.txt"))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
