def package_dependency_resolver(packages: dict[str, list[str]]) -> list[str]:
    deps = {
        pkg: [d for d in reqs if d in packages]
        for pkg, reqs in packages.items()
    }

    result = []

    while len(result) < len(packages):
        found = False
        for pkg, reqs in deps.items():
            if not reqs:
                result.append(pkg)
                found = True
                del deps[pkg]
                for other in deps:
                    if pkg in deps[other]:
                        deps[other].remove(pkg)
                break

        if not found:
            return []

    return result
