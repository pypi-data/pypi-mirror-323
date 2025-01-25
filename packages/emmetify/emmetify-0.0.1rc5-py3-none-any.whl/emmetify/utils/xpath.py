import re

from emmetify.converters.html_converter import HtmlConverterMaps


def restore_attribute_in_xpath(xpath: str, tag: str, attr: str, replace_map: dict[str, str]) -> str:

    patterns = [
        # Basic attribute
        rf"@{attr}=(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
        rf"@{attr.lower()}=(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
        # Contains function
        rf"contains\(@{attr}\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
        # Normalize-space function
        rf"normalize-space\(@{attr}\)=(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
        # Functions with normalize-space
        rf"contains\(normalize-space\(@{attr}\)\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
        # Nested functions with normalize-space
        rf"ends-with\(normalize-space\(@{attr}\)\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
        rf"starts-with\(normalize-space\(@{attr}\)\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
        # Other functions
        rf"starts-with\(@{attr}\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
        rf"ends-with\(@{attr}\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
        rf"matches\(@{attr}\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
    ]

    # Compile patterns with case-insensitive matching
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    # Function to split the XPath into steps with separators
    def split_xpath_with_separators(xpath):
        steps = []
        current_step = ""
        separator = ""
        inside_predicate = 0
        inside_quotes = None
        i = 0
        while i < len(xpath):
            c = xpath[i]
            if c == "/":
                if inside_quotes is None and inside_predicate == 0:
                    if current_step:
                        steps.append((separator, current_step))
                        current_step = ""
                    sep_start = i
                    while i < len(xpath) and xpath[i] == "/":
                        i += 1
                    separator = xpath[sep_start:i]
                    continue
                else:
                    current_step += c
            else:
                current_step += c
                if inside_quotes:
                    if c == inside_quotes:
                        inside_quotes = None
                else:
                    if c in ('"', "'"):
                        inside_quotes = c
                    elif c == "[":
                        inside_predicate += 1
                    elif c == "]":
                        inside_predicate -= 1
            i += 1
        if current_step:
            steps.append((separator, current_step))
        return steps

    # Function to extract the node name and predicate index
    def get_node_test_and_predicate_index(step):
        step = step.strip()
        predicate_index = len(step)
        inside_quotes = None
        for idx, c in enumerate(step):
            if c in ('"', "'"):
                if not inside_quotes:
                    inside_quotes = c
                elif c == inside_quotes:
                    inside_quotes = None
            elif c == "[" and inside_quotes is None:
                predicate_index = idx
                break
        node_test = step[:predicate_index]
        # Remove axis notation if present
        if "::" in node_test:
            node_test_split = node_test.split("::")
            node_name = node_test_split[1]
        else:
            node_name = node_test
        return node_name.strip(), predicate_index

    # Process each step
    steps_with_separators = split_xpath_with_separators(xpath)
    new_steps = []
    for sep, step in steps_with_separators:
        node_name, predicate_index = get_node_test_and_predicate_index(step)
        predicates_string = step[predicate_index:]
        if tag is None or node_name == tag:
            # Process predicates
            for pattern in compiled_patterns:

                def replace_match(m):
                    old_value = m.group("value")
                    new_value = replace_map.get(old_value, old_value)
                    return m.group(0).replace(old_value, new_value, 1)

                predicates_string = pattern.sub(replace_match, predicates_string)
            new_step = step[:predicate_index] + predicates_string
        else:
            new_step = step
        new_steps.append(sep + new_step)
    result = "".join(new_steps)
    return result


def restore_classes_in_xpath(xpath: str, classes_map: dict[str, str]) -> str:
    """
    Restores class attribute values in the XPath expression.

    Args:
        xpath (str): The XPath expression to process.
        classes_map (dict[str, str]): A mapping from old class names to new ones.

    Returns:
        str: The updated XPath expression.
    """
    # Process all tags (tag=None) for the 'class' attribute
    return restore_attribute_in_xpath(xpath, tag=None, attr="class", replace_map=classes_map)


def restore_links_in_xpath(xpath: str, links_map: dict[str, str]) -> str:
    """
    Restores href attribute values in the XPath expression for 'a' tags.

    Args:
        xpath (str): The XPath expression to process.
        links_map (dict[str, str]): A mapping from old href values to new ones.

    Returns:
        str: The updated XPath expression.
    """
    # Process only 'a' tags for the 'href' attribute
    return restore_attribute_in_xpath(xpath, tag="a", attr="href", replace_map=links_map)


def restore_images_in_xpath(xpath: str, images_map: dict[str, str]) -> str:
    """
    Restores src attribute values in the XPath expression for 'img' tags.

    Args:
        xpath (str): The XPath expression to process.
        images_map (dict[str, str]): A mapping from old src values to new ones.

    Returns:
        str: The updated XPath expression.
    """
    # Process only 'img' tags for the 'src' attribute
    return restore_attribute_in_xpath(xpath, tag="img", attr="src", replace_map=images_map)


def restore_xpath_from_converter_maps(xpath: str, converter_maps: HtmlConverterMaps) -> str:
    """
    Restores attribute values in the XPath expression using the provided converter maps.

    Args:
        xpath (str): The XPath expression to process.
        converter_maps: An object containing the attribute mappings (classes, links, images).

    Returns:
        str: The updated XPath expression.
    """
    xpath = restore_classes_in_xpath(xpath, converter_maps.classes)
    xpath = restore_links_in_xpath(xpath, converter_maps.links)
    xpath = restore_images_in_xpath(xpath, converter_maps.images)
    return xpath
