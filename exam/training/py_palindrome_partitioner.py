def palindrome_partitioner(s: str) -> int:
    if s == s[::-1]:
        return 0
    min_cut = len(s) - 1
    for i in range(1, len(s) + 1):
        left = s[:i]
        if left == left[::-1]:
            cuts = 1 + palindrome_partitioner(s[i:])
            if cuts < min_cut:
                min_cut = cuts
    return min_cut
