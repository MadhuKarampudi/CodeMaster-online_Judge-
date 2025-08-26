from django import template
import markdown2

register = template.Library()

@register.filter
def markdownify(text):
    return markdown2.markdown(text, extras=["fenced-code-blocks"])
