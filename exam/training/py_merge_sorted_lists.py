def merge_sorted_lists(lists: list[list[int]]) -> list[int]:
    return sorted(sum(lists, []))
