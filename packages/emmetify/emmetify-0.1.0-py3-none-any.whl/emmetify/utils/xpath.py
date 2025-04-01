import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from emmetify.converters.html_converter import HtmlConverterMaps


@dataclass
class XPathAttributeRestorer:
    """Class for restoring attributes in XPath expressions."""

    def get_attribute_patterns(self, attr: str) -> List[str]:
        """Returns a list of regex patterns for matching various XPath attribute expressions."""
        return [
            # Basic attribute
            rf"@{attr}=(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
            rf"@{attr.lower()}=(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
            # Contains function
            rf"contains\(@{attr}\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
            # Normalize-space function
            rf"normalize-space\(@{attr}\)=(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
            # Functions with normalize-space
            rf"contains\(normalize-space\(@{attr}\)\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",  # noqa: E501
            # Nested functions with normalize-space
            rf"ends-with\(normalize-space\(@{attr}\)\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",  # noqa: E501
            rf"starts-with\(normalize-space\(@{attr}\)\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",  # noqa: E501
            # Other functions
            rf"starts-with\(@{attr}\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
            rf"ends-with\(@{attr}\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
            rf"matches\(@{attr}\s*,\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)\)",
        ]

    def restore_attribute(
        self, xpath: str, tag: Optional[str], attr: str, replace_map: dict[str, str]
    ) -> str:
        """
        Restores attributes in an XPath expression based on a replacement map.

        Args:
            xpath: The XPath expression to process
            tag: Optional tag name to restrict replacements to
            attr: The attribute name to process
            replace_map: Dictionary mapping old values to new values

        Returns:
            The processed XPath expression with restored attributes
        """
        # Compile patterns with case-insensitive matching
        patterns = [re.compile(p, re.IGNORECASE) for p in self.get_attribute_patterns(attr)]

        # Process each step
        steps_with_separators = self._split_xpath_with_separators(xpath)
        new_steps = []

        for separator, step in steps_with_separators:
            node_name, predicate_index = self._parse_node_test(step)
            predicates_string = step[predicate_index:]

            if tag is None or node_name == tag:
                # Process predicates
                for pattern in patterns:
                    predicates_string = pattern.sub(
                        lambda m: m.group(0).replace(
                            m.group("value"), replace_map.get(m.group("value"), m.group("value")), 1
                        ),
                        predicates_string,
                    )
                new_step = step[:predicate_index] + predicates_string
            else:
                new_step = step

            new_steps.append(separator + new_step)

        return "".join(new_steps)

    def _split_xpath_with_separators(self, xpath: str) -> List[Tuple[str, str]]:
        """Function to split the XPath into steps with separators."""
        steps = []
        current_step = ""
        separator = ""
        inside_predicate = 0
        inside_quotes = None
        i = 0

        while i < len(xpath):
            char = xpath[i]

            if char == "/" and inside_quotes is None and inside_predicate == 0:
                if current_step:
                    steps.append((separator, current_step))
                    current_step = ""
                sep_start = i
                while i < len(xpath) and xpath[i] == "/":
                    i += 1
                separator = xpath[sep_start:i]
                continue

            current_step += char
            if inside_quotes:
                if char == inside_quotes:
                    inside_quotes = None
            else:
                if char in ('"', "'"):
                    inside_quotes = char
                elif char == "[":
                    inside_predicate += 1
                elif char == "]":
                    inside_predicate -= 1
            i += 1

        if current_step:
            steps.append((separator, current_step))
        return steps

    def _parse_node_test(self, step: str) -> Tuple[str, int]:
        """Function to extract the node name and predicate index."""
        step = step.strip()
        predicate_index = len(step)
        inside_quotes = None

        for idx, char in enumerate(step):
            if char in ('"', "'"):
                if not inside_quotes:
                    inside_quotes = char
                elif char == inside_quotes:
                    inside_quotes = None
            elif char == "[" and inside_quotes is None:
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


def restore_classes_in_xpath(xpath: str, classes_map: dict[str, str]) -> str:
    """
    Restores class attribute values in the XPath expression.

    Args:
        xpath (str): The XPath expression to process.
        classes_map (dict[str, str]): A mapping from old class names to new ones.

    Returns:
        str: The updated XPath expression.
    """
    restorer = XPathAttributeRestorer()
    return restorer.restore_attribute(xpath, tag=None, attr="class", replace_map=classes_map)


def restore_links_in_xpath(xpath: str, links_map: dict[str, str]) -> str:
    """
    Restores href attribute values in the XPath expression for 'a' tags.

    Args:
        xpath (str): The XPath expression to process.
        links_map (dict[str, str]): A mapping from old href values to new ones.

    Returns:
        str: The updated XPath expression.
    """
    restorer = XPathAttributeRestorer()
    return restorer.restore_attribute(xpath, tag="a", attr="href", replace_map=links_map)


def restore_images_in_xpath(xpath: str, images_map: dict[str, str]) -> str:
    """
    Restores src attribute values in the XPath expression for 'img' tags.

    Args:
        xpath (str): The XPath expression to process.
        images_map (dict[str, str]): A mapping from old src values to new ones.

    Returns:
        str: The updated XPath expression.
    """
    restorer = XPathAttributeRestorer()
    return restorer.restore_attribute(xpath, tag="img", attr="src", replace_map=images_map)


def restore_xpath_from_converter_maps(xpath: str, converter_maps: HtmlConverterMaps) -> str:
    """
    Restores attribute values in the XPath expression using the provided converter maps.

    Args:
        xpath (str): The XPath expression to process.
        converter_maps: An object containing the attribute mappings (classes, links, images).

    Returns:
        str: The updated XPath expression.
    """
    restorer = XPathAttributeRestorer()
    xpath = restorer.restore_attribute(
        xpath, tag=None, attr="class", replace_map=converter_maps.classes
    )
    xpath = restorer.restore_attribute(
        xpath, tag="a", attr="href", replace_map=converter_maps.links
    )
    xpath = restorer.restore_attribute(
        xpath, tag="img", attr="src", replace_map=converter_maps.images
    )
    return xpath
