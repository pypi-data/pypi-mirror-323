from dataclasses import dataclass
from typing import Union

from emmetify.config.base_config import EmmetifierConfig
from emmetify.config.html_config import HtmlAttributesPriority
from emmetify.converters.base_converter import BaseConverter
from emmetify.nodes.html_nodes import HtmlNode, HtmlNodePool
from emmetify.utils.tokens import SingleTokenNames


class HtmlPriorityAttributeFilter:
    """Filters HTML attributes based on priority rules"""

    def __init__(self, priority_config: HtmlAttributesPriority):
        self.config = priority_config

    def _is_data_attribute(self, attr: str) -> bool:
        """Check if attribute is a data-* attribute"""
        return attr.startswith("data-")

    def _is_event_handler(self, attr: str) -> bool:
        """Check if attribute is an event handler"""
        return attr.startswith("on")

    def filter_attributes(self, attrs: dict[str, str]) -> dict[str, str]:
        """
        Filter attributes based on priority rules.
        Returns the most relevant attributes for LLM understanding and XPath creation.
        """
        if not attrs:
            return {}

        # Always remove ignored attributes
        filtered_attrs = {
            k: v
            for k, v in attrs.items()
            if k not in self.config.ignore_attrs
            and not self._is_data_attribute(k)
            and not self._is_event_handler(k)
        }

        # Check for primary attributes
        primary_attrs_present = {
            k: v for k, v in filtered_attrs.items() if k in self.config.primary_attrs
        }

        # If we have primary attributes, return only those
        if primary_attrs_present:
            return primary_attrs_present

        # Otherwise, keep secondary attributes
        return {k: v for k, v in filtered_attrs.items() if k in self.config.secondary_attrs}


@dataclass
class HtmlConverterMaps:
    classes: dict[str, str]
    links: dict[str, str]
    images: dict[str, str]


@dataclass
class HtmlConverterResult:
    result: str
    maps: HtmlConverterMaps


class HtmlConverter(BaseConverter[HtmlNodePool]):
    """Converts HTML nodes to Emmet"""

    def __init__(self, config: EmmetifierConfig):
        super().__init__(config)

        self.priority_filter = HtmlPriorityAttributeFilter(config.html.attributes_priority)
        self.single_token_names = SingleTokenNames()

        self.classes_map: dict[str, str] = {}
        self.links_map: dict[str, str] = {}
        self.images_map: dict[str, str] = {}

    def _escape_text(self, text: str) -> str:
        """Escape * and $ in text content."""
        escape_chars = {
            "\\": "\\\\",
            "*": r"\*",
            "$": r"\$",
        }
        escaped = text.translate(str.maketrans(escape_chars))
        no_white_chars = " ".join(escaped.split())
        return no_white_chars

    def _node_to_emmet(self, node: HtmlNode) -> str:
        """Convert single node to Emmet notation with attribute filtering."""
        if node.is_text_node:
            return f"{{{self._escape_text(node.text_content)}}}"

        # Start with tag name
        parts = [node.tag]

        # Filter attributes before processing
        if self.config.html.prioritize_attributes:
            attributes = self.priority_filter.filter_attributes(node.attrs)
        else:
            attributes = node.attrs

        # Process id if present
        if "id" in attributes:
            parts.append(f'#{attributes["id"]}')

        # Process classes if present
        if "class" in attributes:
            emmet_class_name = f".{'.'.join(attributes['class'])}"
            space_separated_class_name = " ".join(attributes["class"])  # for class map
            if self.config.html.simplify_classes:
                mapped_class = self.classes_map.get(space_separated_class_name)
                # the same class must be mapped to the same token
                # because llm making wrong assumptions in xpath generation
                # and often mix classes on xpath selectors
                if not mapped_class:
                    single_token_class = self.single_token_names.get_name()
                    self.classes_map[space_separated_class_name] = single_token_class
                    parts.append(f".{single_token_class}")
                else:
                    parts.append(f".{mapped_class}")
            else:
                parts.append(emmet_class_name)

        # Process href for absolute links
        if node.tag == "a" and "href" in attributes:
            href = attributes["href"]

            # Simplify absolute links
            if self.config.html.simplify_absolute_links and href.startswith("http"):
                mapped_url = self.links_map.get(href)
                if not mapped_url:
                    single_token_url = self.single_token_names.get_name()
                    self.links_map[href] = single_token_url
                    attributes["href"] = single_token_url
                else:
                    attributes["href"] = mapped_url

            # Simplify relative links
            elif self.config.html.simplify_relative_links and not href.startswith("http"):
                mapped_url = self.links_map.get(href)
                if not mapped_url:
                    single_token_url = self.single_token_names.get_name()
                    self.links_map[href] = single_token_url
                    attributes["href"] = single_token_url
                else:
                    attributes["href"] = mapped_url

        # Process src for images
        if self.config.html.simplify_images and node.tag == "img" and "src" in attributes:
            mapped_src = self.images_map.get(attributes["src"])
            if not mapped_src:
                single_token_src = self.single_token_names.get_name()
                self.images_map[attributes["src"]] = single_token_src
                attributes["src"] = single_token_src
            else:
                attributes["src"] = mapped_src

        # Remove id and class from remaining attributes since we've handled them
        remaining_attrs = {k: v for k, v in attributes.items() if k not in ["id", "class"]}

        if self.config.html.skip_empty_attributes:
            remaining_attrs = {k: v for k, v in remaining_attrs.items() if v}

        # Add remaining filtered attributes
        if remaining_attrs:
            # if there are spaces in attribute value, it must be wrapped in quotes
            attr_str_list = []
            for k, v in remaining_attrs.items():
                if " " in v:
                    attr_str_list.append(f'{k}="{v}"')
                elif v == "":
                    attr_str_list.append(k)
                else:
                    attr_str_list.append(f"{k}={v}")
            attr_str = " ".join(attr_str_list)
            parts.append(f"[{attr_str}]")

        return "".join(parts)

    def _build_emmet(
        self, node_pool: HtmlNodePool, node_data: Union[str, HtmlNode], level: int = 0
    ) -> str:
        """Recursively build Emmet notation with optional indentation."""
        indent = " " * (self.config.indent_size * level) if self.config.indent else ""

        if isinstance(node_data, str):
            node = node_pool.get_node(node_data)
        else:
            node = node_data

        if not node:
            return ""

        # Emmetify current node
        node_emmet = self._node_to_emmet(node)

        # Get children nodes
        children_nodes: list[HtmlNode] = []
        direct_text_child_node: Union[HtmlNode, None] = None
        for child_index, child_id in enumerate(node.children_ids):
            child_node = node_pool.get_node(child_id)
            is_first_text_child = (
                child_node.is_text_node and child_index == 0 and not direct_text_child_node
            )
            if is_first_text_child:
                direct_text_child_node = child_node
            else:
                children_nodes.append(child_node)

        # Emmetify children
        children_emmet: list[str] = []
        for child_node in children_nodes:
            child_emmet = self._build_emmet(node_pool, child_node, level + 1)
            children_emmet.append(child_emmet)

        # Emmetify direct text child node
        text_node_emmet = (
            self._node_to_emmet(direct_text_child_node) if direct_text_child_node else ""
        )

        if self.config.indent:
            children_emmet_str = "+\n".join(children_emmet)
        else:
            children_emmet_str = "+".join(children_emmet)

        if children_emmet_str:
            if self.config.indent:
                children_group = f">\n{children_emmet_str}"
            else:
                children_group = f">{children_emmet_str}"
        else:
            children_group = ""

        sibilings_count = node_pool.get_siblings_count(node.id)
        is_node_with_siblings_and_children = sibilings_count > 0 and len(children_nodes) > 0

        node_emmet_str = ""
        if is_node_with_siblings_and_children:
            node_emmet_str = f"({node_emmet}{text_node_emmet}{children_group})"
        else:
            node_emmet_str = f"{node_emmet}{text_node_emmet}{children_group}"

        return f"{indent}{node_emmet_str}"

    def convert(self, node_pool: HtmlNodePool) -> HtmlConverterResult:
        result = super().convert(node_pool)

        return HtmlConverterResult(
            result=result,
            maps=HtmlConverterMaps(
                classes={v: k for k, v in self.classes_map.items()},
                links={v: k for k, v in self.links_map.items()},
                images={v: k for k, v in self.images_map.items()},
            ),
        )
