from bs4 import BeautifulSoup


def clean_html(
    html_content: str,
    remove_styles: bool = True,
    remove_scripts: bool = True,
    remove_noscripts: bool = True,
    remove_iframes: bool = True,
    remove_metas: bool = True,
    tags: list[str] = [],
    return_as_string: bool = False,
) -> BeautifulSoup | str:
    """
    Cleans the HTML content by removing unwanted tags and returns a BeautifulSoup object or a string.

    Parameters:
    html_content (str): The HTML content to clean.
    remove_styles (bool): Remove style tags.
    remove_scripts (bool): Remove script tags.
    remove_noscripts (bool): Remove noscript tags.
    remove_iframes (bool): Remove iframe tags.
    remove_metas (bool): Remove meta tags.
    addional_tags (list[str]): Additional tags to remove.
    return_as_string (bool): Return the cleaned content as a string.

    Returns:
    BeautifulSoup | str: The cleaned HTML content.
    """
    if not html_content:
        raise ValueError("The HTML content is required.")
    if not isinstance(html_content, str):
        raise ValueError("The HTML content must be a string.")

    bool_params = [
        ("remove_styles", remove_styles),
        ("remove_scripts", remove_scripts),
        ("remove_noscripts", remove_noscripts),
        ("remove_iframes", remove_iframes),
        ("remove_metas", remove_metas),
        ("return_as_string", return_as_string),
    ]

    for param_name, param_value in bool_params:
        if not isinstance(param_value, bool):
            raise ValueError(f"{param_name} must be a boolean.")

    if not isinstance(tags, list):
        raise ValueError("addional_tags must be a list.")

    for tag in tags:
        if not isinstance(tag, str):
            raise ValueError(
                f"Each element in addional_tags must be a string. Found {type(tag)}."
            )

    tag_mapping = {
        'style': remove_styles,
        'script': remove_scripts,
        'noscript': remove_noscripts,
        'iframe': remove_iframes,
        'meta': remove_metas
    }

    elements_to_remove = [tag for tag, should_remove in tag_mapping.items() if should_remove]

    elements_to_remove.extend(tags)
    soup = BeautifulSoup(html_content, "html.parser")

    for element in soup.find_all(elements_to_remove):
        element.decompose()

    return str(soup) if return_as_string else soup
