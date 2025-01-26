import json

from django.forms import widgets
from django.utils.safestring import mark_safe
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.telepath import register
from wagtail.widget_adapters import WidgetAdapter


class PolyfillColorInputWidget(widgets.TextInput):
    class Media:
        css = {
            "all": (
                "https://cdnjs.cloudflare.com/ajax/libs/spectrum/1.8.0/spectrum.min.css",
            )
        }

        js = ("https://cdnjs.cloudflare.com/ajax/libs/spectrum/1.8.0/spectrum.min.js",)

    def render(self, name, value, attrs=None, renderer=None):
        out = super().render(name, value, attrs, renderer=renderer)
        field_id = attrs["id"]

        return mark_safe(
            out
            + """
            <script>
            (function(){
                function init() {
                    $("#__FIELD_ID__").spectrum({
                        showPalette: false,
                        preferredFormat: "hex",
                        showInput: true,
                    });
                }

                if (document.readyState === 'complete') {
                    init({});
                }

                $(window).on('load', function() {
                    init();
                });
            })();
            </script>
            """.replace(
                "__FIELD_ID__", field_id
            )
        )


if WAGTAIL_VERSION >= (6, 0):  # type: ignore
    from django.forms import Media

    class ColorInputWidget(widgets.TextInput):  # type: ignore
        template_name = "wagtail_color_panel/widgets/color-input-widget.html"

        def __init__(self, attrs=None):
            default_attrs = {
                "class": "color-input-widget__text-input",
            }
            attrs = attrs or {}
            attrs = {**default_attrs, **attrs}
            super().__init__(attrs=attrs)

        def build_attrs(self, *args, **kwargs):
            attrs = super().build_attrs(*args, **kwargs)
            attrs["data-controller"] = "color-input"
            return attrs

        @property
        def media(self):
            return Media(
                css={
                    "all": [
                        "wagtail_color_panel/css/color-input-widget.css",
                    ]
                },
                js=[
                    "wagtail_color_panel/js/color-input-widget.js",
                    "wagtail_color_panel/js/color-input-controller.js",
                ],
            )

else:
    from wagtail.utils.widgets import WidgetWithScript

    class ColorInputWidget(WidgetWithScript, widgets.TextInput):
        template_name = "wagtail_color_panel/widgets/color-input-widget.html"

        def __init__(self, attrs=None):
            default_attrs = {
                "class": "color-input-widget__text-input",
            }
            attrs = attrs or {}
            attrs = {**default_attrs, **attrs}
            super().__init__(attrs=attrs)

        def render_js_init(self, id_, name, value):
            return "new ColorInputWidget({0});".format(json.dumps(id_))

        class Media:
            css = {
                "all": [
                    "wagtail_color_panel/css/color-input-widget.css",
                ]
            }
            js = [
                "wagtail_color_panel/js/color-input-widget.js",
            ]


class ColorInputWidgetAdapter(WidgetAdapter):
    js_constructor = "wagtail_color_panel.widgets.ColorInput"

    class Media:
        js = [
            "wagtail_color_panel/js/color-input-widget-telepath.js",
        ]


register(ColorInputWidgetAdapter(), ColorInputWidget)
