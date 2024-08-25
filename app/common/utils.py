import difflib


async def find_all_matches(query: str, options: list[str], cutoff: float = 0.5):
    """
    Get all close matches from the options list based on the cutoff similarity

    Args:
        query (str): The query
        options list[str]: The list of options
        cutoff (float = 0.6): The cutoff mark
    """

    matches = difflib.get_close_matches(query, options, n=len(options), cutoff=cutoff)

    return matches


def paginate_list(items: list, page: int, size: int):
    """
    Paginate list

    Args:
        items (list): The list of items
        page (int): The page
        size (int): The size

    Returns:
        list
    """
    # Calculate start and end indices
    start = (page - 1) * size
    end = start + size

    # Return the sliced list
    return items[start:end] if start < len(items) else []
