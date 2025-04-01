from importlib import metadata

from emmetify.config import __all__ as config_all
from emmetify.emmetifier import Emmetifier


def emmetify_html(content, format="html", **options):
    """Convenience function for quick conversions"""
    emmetifier = Emmetifier(format=format, **options)
    return emmetifier.emmetify(content)


def emmetify_compact_html(content):
    """Convenience function for quick HTML conversion with simplified tags and attributes"""
    emmetifier = Emmetifier(
        format="html",
        config={
            "html": {
                "skip_tags": True,
                "prioritize_attributes": True,
                "simplify_classes": True,
                "simplify_images": True,
                # LLM agents works better when they know the relative links
                # otherwise they will start looping on redirects
                "simplify_relative_links": False,
                "simplify_absolute_links": True,
            }
        },
    )
    return emmetifier.emmetify(content)


__all__ = [
    "Emmetifier",
    "emmetify_html",
    "emmetify_compact_html",
    *config_all,
]

__version__ = metadata.version("emmetify")
