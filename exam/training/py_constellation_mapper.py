def constellation_mapper(stars: list[tuple[int, int]], dim: int) -> list[str]:
    valid_stars = set(stars)
    return [
        "".join("*" if (r, c) in valid_stars else "." for c in range(dim))
        for r in range(dim)
    ]
