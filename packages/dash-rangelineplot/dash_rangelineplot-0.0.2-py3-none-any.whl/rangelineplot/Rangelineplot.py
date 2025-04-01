# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Rangelineplot(Component):
    """A Rangelineplot component.


Keyword arguments:

- id (string; optional)

- axisType (a value equal to: 'x', 'y'; default 'x')

- boundaryStyle (dict; default {color: 'transparent', width: 20})

- className (string; default '')

- data (dict; required)

    `data` is a dict with keys:

    - x (list of numbers; required)

    - y (list of numbers; required)

- grayZoneStyle (dict; default {fillcolor: 'rgba(200,200,200,0.5)'})

- lineStyle (dict; default {color: '#1f77b4', width: 2})

- style (dict; optional)

- xRange (list of numbers; optional)

- yRange (list of numbers; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'rangelineplot'
    _type = 'Rangelineplot'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, data=Component.REQUIRED, xRange=Component.UNDEFINED, yRange=Component.UNDEFINED, axisType=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, lineStyle=Component.UNDEFINED, grayZoneStyle=Component.UNDEFINED, boundaryStyle=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'axisType', 'boundaryStyle', 'className', 'data', 'grayZoneStyle', 'lineStyle', 'style', 'xRange', 'yRange']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'axisType', 'boundaryStyle', 'className', 'data', 'grayZoneStyle', 'lineStyle', 'style', 'xRange', 'yRange']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['data']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Rangelineplot, self).__init__(**args)
