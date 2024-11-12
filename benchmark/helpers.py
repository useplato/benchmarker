from deepdiff import DeepDiff


def get_dict_structure(d):
    if isinstance(d, dict):
        return {k: get_dict_structure(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [get_dict_structure(d[0])] if d else []
    else:
        return type(d).__name__


def count_nested_keys(d, parent_key=""):
    """Recursively count all keys in a nested dictionary."""
    count = 0
    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        count += 1
        if isinstance(value, dict):
            count += count_nested_keys(value, full_key)
    return count


def compare_dicts(dict1, dict2):
    # Get the differences using DeepDiff
    diff = DeepDiff(dict1, dict2, ignore_order=True)

    # Calculate the total number of differences (keys/values changed, added, or removed)
    total_diff_count = (
        len(diff.get("values_changed", {}))
        + len(diff.get("dictionary_item_added", {}))
        + len(diff.get("dictionary_item_removed", {}))
    )

    # Count all nested keys in both dictionaries
    total_keys = count_nested_keys(dict1) + count_nested_keys(dict2)

    # Avoid division by zero
    if total_keys == 0:
        return 100.0 if dict1 == dict2 else 0.0

    # Calculate the similarity score
    similarity_score = ((total_keys - total_diff_count) / total_keys) * 100
    return max(0, similarity_score)
