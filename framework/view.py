# View wrapper for Larapak Web Framework

from .template_engine import TemplateEngine

def view(name, context=None):
    """Factory helper to construct response and render view."""
    from .response import Response
    return Response().view(name, context)
