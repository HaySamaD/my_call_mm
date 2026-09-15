def array_rotation_detector(arr1: list, arr2: list) -> bool:
    if len(arr1) != len(arr2):
        return False
    if not arr1:
        return True

    double_arr = arr1 + arr1
    n = len(arr1)
    return any(double_arr[i : i + n] == arr2 for i in range(n))
