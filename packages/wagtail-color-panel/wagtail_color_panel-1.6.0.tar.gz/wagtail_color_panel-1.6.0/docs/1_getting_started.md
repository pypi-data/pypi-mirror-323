# Getting started

### Requirements

- Python 3.9+
- Wagtail 5.2+ and Django 4.2+
- [A browser that supports `input type="color"`](https://caniuse.com/#feat=input-color)


### Installation

Install the library with pip:

```
$ pip install wagtail-color-panel
```


### Quick Setup

Add `wagtail-color-panel` to your `INSTALLED_APPS` in Django settings.

```python
INSTALLED_APPS = (
    # ...
    'wagtail_color_panel',
)
```


### Whats next?

Depending on your use case you can read either of these guides:

- [Adding panel to a page](./2_adding_to_a_page.md)
- [Adding to a StreamField](./3_adding_to_a_streamfield.md)
