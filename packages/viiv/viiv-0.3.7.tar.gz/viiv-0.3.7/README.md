#warning ViiV

<div></div>

Might be the most comfortable VsCode theme.

# Features

- _Perfect_ and _automatically_ tuned color contrast ratio complying the
  [WCGA Accessibility Creteria](https://www.w3.org/TR/WCAG20-TECHS/G17.html).
- _Automatically_ generate _countless_ beautiful themes.
- _One_ configuration supports both Dark and Light themes.
- _Easy_ configuration for customization.

# Preview

## Dark Theme

![Dark Theme Preview](images/dark_theme_demo.png)

## Light Theme

![Light Theme Preview](images/light_theme_demo.png)

# Configuration

All configurations are managed in `config.json` file.

## To customize the token color, add one more color configuration item in `token`:

```
{
    "color": {
        "hex": "#9a449a"
    },
    "groups": [
        ".*support.type.*"
    ]
}
```

## To customize the decoration color, add `hex` in `color` of `decoration`:

```
"decoration": [
    {
        "color": {
            "hex": "#00b300",
            "alpha_range": [
                "0xfe",
                "0xff"
            ],
            "basic_range": [
                13,
                14
            ],
            "light_range": [
                59,
                60
            ]
        },
        "groups": [
            "default"
        ]
    }
]
```

## To use specific color as the editor background:

set the option `workbench_editor_background_color` in `options`

```
"workbench_editor_background_color": "#231f32"
```

## contrast ratio

Best values based on lots of testing results:

```
"token_color_min_contrast_ratio": 7,
"token_color_max_contrast_ratio": 10,
"workbench_color_min_contrast_ratio": 10,
"workbench_color_max_contrast_ratio": 20,
```

```
"min_contrast_ratio": 10,
"max_contrast_ratio": 18,
```

## Some properties are naming as foreground or background but in fact they behaves inverse

To reverse back, use the below `options` to configure them.

```
"workbench_foreground_properties": [
    "(?!.*(badge).*).*foreground$",
    ".*badge.*background$",
    ".*gutter.{2,}background$",
    ".*strongborder$",
    ".*IndentGuide.*active.*background[0-9]*$"
],
"workbench_background_properties": [
    "(?!.*(badge|gutter|(IndentGuide.*active)).*).*background[0-9]*$",
    ".*badge.*foreground$",
    ".*(?!strong).*border$",
    "editorGutter.background"
]
```

NOTE: After setting 'background' color as 'foreground' properties, do remember
to tuning down its ALPHA value to make it not too light. The same for those
'foreground' color setted as 'background', do remember to tuning up its ALPHA
value make it not too dark.

## Matching rule:

When matching a color property with color property group, the following rules
are applied:

- EXACT = 1
- ENDSWITH = 2
- STARTSWITH = 3
- FUZZY = 4

Therefore, to customize the specific color property, use property full value as
group value in config.json file.

```
    {
        "colors": {
            "editor.foreground": "#a4ac7f"
        }
    }
```

## Areas

The color properties are divided into several areas: default, background,
foreground, border, token

The 'default' area has highest priority and it can override other areas
configurations when the 'group' value is the same as the color property value -
the specific color property could be customized.

The areas background, foreground, and border are mainly used for general
purpose to define general color code for color properties falling in those
areas.

In each area, we can define color code for color properties 'groups'. Each
group could be the full name of the color property, prefix or suffix of the
color property, regular expression which is used to match all the relevant
color properties.

## Default

The default purpose for 'default' area is to change the ALPHA value of the
color for different status like active, inactive, highlight as such.

It might need to reset BASIC, LIGHT, ALPHA ranges for some color perperties.
For example, if "editor" is set in 'background' area, then all color properties
color of "editor.\*Background" will follow the colors defined in 'background'
area for 'editor' since "editor" is treated as the prefix of the properties.
So, when it need to set color for "editor.wordHighlightBackground", the basic
color will still the same with the editor basic color which is dark color. If
we want to use other color, then we need to be allowed to change the basic
color. In configuration, this is controlled by the attribute
`replace_color_component`. Its value could be `ALPHA`, `BASIC`, `LIGHT`, and
`ALL`. The `replace` here means the color code in configuration file will
replace the one in the template file.

"default" area in config.json has highest priority and can override any
previous configuration.

Note: If any property need customization, it's better to do it in 'default'
area, especially when it contains 'status' keywords like 'active', 'focus' as
such. When do customization or tuning, do add extra configuration rather than
modifying the original configuration since it might result in mess and need
more extra time to tuning and make it workable, especially for those
configurations having regular expression.

## Static color

To use static color for property, use the below format:

```

    {
        "groups": [
            ".*foreground.*"
        ],
        "color": {
            "hex": "#b7b7ff",
            "alpha_range": [
                "0xdf",
                "0xe1"
            ]
        }
    }

```

## Dynamic color

To use dynamic color, use the below format:

```

    {
        "groups": [
            ".*editorSuggestWidget.*"
        ],
        "color": {
            "basic_range": [
                1,
                11
            ],
            "light_range": [
                10,
                35
            ],
            "alpha_range": [
                "0x95",
                "0xa5"
            ]
        }
    }

```

## Decoration Colors

A new area 'decoration' is added. It has one 'default' group. 'decoration'
group name could be used in any other groups for workbench to make those groups
are 'decoration' groups. The 'decoration' groups can ignore the 'basic_range'
and use the default 'decoration' group's color 'basic_range' configuration. The
same applies to 'hex'. The 'basic_range' of default decoration color group is
automatically updated by using one random int from start to end of the basic
range and the value by plusing 1 to the random int. For example, if the
'basic_range' of the default decoration group is configured as `[8-14]`, then
random int could be any value from 8 to 14 (included boundaries). If the random
int is `9`, then the basic range will be updated as `[9,10]`. Therefore, the
max value of 'basic_range' is the sum value of `colors total` of workbench and
token. By default, it's `14`. If the max value is bigger than 14, error will
occur since the basic range will be valid. For example, it could be `[15, 16]`
which are not supported by the generated color palette. The result is that the
decoration color will be `RED` which is default value for VsCode when the color
value is not valid.

## Options

- The option `workbench_base_color_rate` is used to generate the darker
  workbench color (`workbench_base_color`) if the `workbench_editor_color` is
  given and the `workbench_base_color` is NOT given.
- The option `force_to_use_workbench_editor_background_color` - `true` to use
  the pre-defined editor background forcely even the better color is
  auto-generated according to WCGA standard. - `false` to use the
  auto-generated editor background color according to the contrast ratio.
- By default, it's not recommended to set
  `is_auto_adjust_contrast_radio_enabled` as `false` and set
  `force_to_use_workbench_editor_background_color` as `true` because the
  auto-tuned color is based on the standard from WCGA which is based on
  science. The auto-tuned color should be the most comfortable color for human
  eyes.

# Developers User Guide

## Workbench Background Tuning

- Basic range

Generate theme with darker workbench background colors by using smaller values
pairs for the properties `workbench_colors_min` and `workbench_colors_max`.

```
    "workbench_colors_min": 5,
    "workbench_colors_max": 10,
```

On the contrary, setting bigger values pairs for the properties
`workbench_colors_min` and `workbench_colors_max` to generate lighter workbench
background colors.

```
    "workbench_colors_min": 30,
    "workbench_colors_max": 60,
```

Note:

- The max value of `workbench_colors_max` should be less than 60. Bigger
  (lighter) value is not proper for the background color.

- Saturation and Lightness

Use `workbench_colors_saturation` and `workbench_colors_lightness` to control
saturation and lightness of the workbench colors.

The properties

## Pre-Built Theme Configuration

The configuration template for pre-built theme:

- Use `workbench_editor_background_color` to set the editor background color

```
    {
        "name": "THEME NAME",
        "theme_mode": "DARK|LIGHT",
        "workbench_editor_background_color": "#RRGGBB",
        "workbench_base_background_color_rate": [0-1](float number)
    }
```

- Use `workbench_editor_background_name` to set the editor background color

```
    {
        "name": "[THEME NAME]",
        "theme_mode": "[DARK|LIGHT]",
        "workbench_editor_background_name": "[RED, GREEN, BLUE, YELLOW, CYAN, VIOLET, BLACK]",
        "workbench_base_background_color_rate": [0-1](float number)
    }
```

Pre-Built theme configuration doesn't need to set `contrast_ratio` which should
be globally generic. Instead, use `workbench_colors_saturation` and
`workbench_colors_lightness` to control the `saturation` and `lightness`.

## Set fixed color for tokens

To set fixed color for a group of tokens, use the below configuration in
`token` area:

```
    {
        "color": {
            "hex": "#9a449afe"
        },
        "groups": [
            ".*support.type.*"
        ]
    }
```

This example sets all tokens matching `.*support.type.*` as `#9a449afe`.

# Usage

## Commands

To generate a random new theme, run the command under the directory of the
project:

```
    python viiv.py -r

```

Normally, the randomly generated theme is better than manullay configured
theme.

To re-generate the built-in theme, run the command under the directory of the
project:

```
    python viiv.py -g -t "[THEME NAME]$"
```

To get all built-in themes' names, run the command under the directory of the
project:

```
python .\viiv.py -T
```
