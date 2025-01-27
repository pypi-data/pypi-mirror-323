"""
Classes encapsulating colors in different formats.
"""

from typing import Tuple
import copy


class HSLColor():
    """
    A color in HSLA format (Hue, Saturation, Lightness, and optional Alpha).

    These colors are defined in cylindrical coordinates, with hue and saturation being defined in
    polar coordinates (angle φ and radius ρ, respectively), and the lightness in a cartesian
    coordinate.
    """
    def __init__(
        self,
        hue: float,
        saturation: float,
        lightness: float,
        opacity: float = 1.0,
    ) -> None:
        """
        Initializes a color.

        :param hue: The hue component of the color in the range [0, 1].
        :type hue: float
        :param saturation: The saturation component of the color in the range [0, 1].
        :type saturation: float
        :param lightness: The lightness component of the color in the range [0, 1].
        :type lightness: float
        :param opacity: The optional opacity in the range [0, 1]; defaults to 1.0
        :type opacity: float, optional
        """
        self.hue = hue
        self.saturation = saturation
        self.lightness = lightness
        self.opacity = opacity

    @staticmethod
    def from_abs_hsla(
        abs_hue: int,
        abs_saturation: int,
        abs_lightness: int,
        abs_alpha: int = 100,
    ) -> 'HSLColor':
        """
        Factory method that instantiates a color from its absolute HSL components.

        :param abs_hue: The absolute hue in the range [0, 360]
        :type abs_hue: int
        :param abs_saturation: The absolute saturation in the range [0, 100]
        :type abs_saturation: int
        :param abs_lightness: The absolute lightness in the range [0, 100]
        :type abs_lightness: int
        :param abs_alpha: The absolute opacity in the range [0, 100], defaults to 100
        :type abs_alpha: int, optional
        :return: The new color.
        :rtype: HSLColor
        """
        abs_hue = ((abs_hue % 360) + 360) % 360
        abs_saturation = min(max(abs_saturation, 0), 100)
        abs_lightness = min(max(abs_lightness, 0), 100)
        abs_alpha = min(max(abs_alpha, 0), 100)

        return HSLColor(
            abs_hue / 360.0,
            abs_saturation / 100.0,
            abs_lightness / 100.0,
            abs_alpha / 100.0,
        )

    @staticmethod
    def from_rgba(red: float, green: float, blue: float, alpha: float = 1.0) -> 'HSLColor':
        """
        Factory method that instantiates a color from its decimal RGB or RGBA components.

        :param red: The red component of the color in the range [0, 1].
        :type red: float
        :param green: The green component of the color in the range [0, 1].
        :type green: float
        :param blue: The blue component of the color in the range [0, 1].
        :type blue: float
        :param alpha: The optional alpha component of the color in the range [0, 1]; Defaults to 1.0
        :type alpha: float, optional
        :return: The new color.
        :rtype: HSLColor
        """
        red = min(max(red, 0.0), 1.0)
        green = min(max(green, 0.0), 1.0)
        blue = min(max(blue, 0.0), 1.0)
        alpha = min(max(alpha, 0.0), 1.0)

        c_max: float = max(red, green, blue)
        c_min: float = min(red, green, blue)
        c_delta: float = c_max - c_min

        hue: float
        if c_delta == 0.0:
            hue = 0.0
        elif c_max == red:
            hue = (((green - blue) / c_delta) % 6) / 6.0
        elif c_max == green:
            hue = (((blue - red) / c_delta) + 2) / 6.0
        elif c_max == blue:
            hue = (((red - green) / c_delta) + 4) / 6.0

        lightness: float = (c_max + c_min) / 2.0

        saturation: float
        if c_delta == 0.0:
            saturation = 0.0
        else:
            saturation = c_delta / (1 - abs(2 * lightness - 1))

        return HSLColor(hue, saturation, lightness, alpha)

    @staticmethod
    def from_abs_rgba(
        abs_red: int,
        abs_green: int,
        abs_blue: int,
        abs_alpha: int = 255,
    ) -> 'HSLColor':
        """
        Factory method that instantiates a color from its absolute HSL components.

        :param abs_red: The absolute red component in the range [0, 255]
        :type abs_red: int
        :param abs_green: The absolute green component in the range [0, 255]
        :type abs_green: int
        :param abs_blue: The absolute blue component in the range [0, 255]
        :type abs_blue: int
        :param abs_alpha: The absolute alpha component in the range [0, 255], defaults to 255
        :type abs_alpha: int, optional
        :return: The new color.
        :rtype: HSLColor
        """
        abs_red = min(max(abs_red, 0), 255)
        abs_green = min(max(abs_green, 0), 255)
        abs_blue = min(max(abs_blue, 0), 255)
        abs_alpha = min(max(abs_alpha, 0), 255)

        return HSLColor.from_rgba(
            abs_red / 255.0,
            abs_green / 255.0,
            abs_blue / 255.0,
            abs_alpha / 255.0,
        )

    @staticmethod
    def from_hex(hex_color: str) -> 'HSLColor':
        """
        Factory method that instantiates a color from its hexadecimal RGB or RGBA representation.

        :param hex_color: The hexadecimal representation of the color.
        :type hex_color: str
        :raises ValueError: When a non-valid hexadecimal representation is passed.
        :return: The new color.
        :rtype: HSLColor
        """
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = (
                f'{hex_color[0]}{hex_color[0]}'
                f'{hex_color[1]}{hex_color[1]}'
                f'{hex_color[2]}{hex_color[2]}'
            )
        elif len(hex_color) == 4:
            hex_color = (
                f'{hex_color[0]}{hex_color[0]}'
                f'{hex_color[1]}{hex_color[1]}'
                f'{hex_color[2]}{hex_color[2]}'
                f'{hex_color[3]}{hex_color[3]}'
            )
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return HSLColor.from_abs_rgba(r, g, b, 255)
        elif len(hex_color) == 8:
            r, g, b, a = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))
            return HSLColor.from_abs_rgba(r, g, b, a)
        raise ValueError(f'{hex_color} is not a valid color in hexadecimal format')

    @property
    def hue(self) -> float:
        """
        The hue component of the color [0.0, 1.0].
        """
        return self.__hue

    @hue.setter
    def hue(self, hue: float) -> None:
        self.__hue = (hue + int(hue)) % 1.0

    @property
    def saturation(self) -> float:
        """
        The saturation component of the color [0.0, 1.0].
        """
        return self.__saturation

    @saturation.setter
    def saturation(self, saturation: float) -> None:
        self.__saturation = min(max(saturation, 0.0), 1.0)

    @property
    def lightness(self) -> float:
        """
        The lightness component of the color [0.0, 1.0].
        """
        return self.__lightness

    @lightness.setter
    def lightness(self, lightness: float) -> None:
        self.__lightness = min(max(lightness, 0.0), 1.0)

    @property
    def opacity(self) -> float:
        """
        The opacity of the color [0.0, 1.0].
        """
        return self.__opacity

    @opacity.setter
    def opacity(self, opacity: float) -> None:
        self.__opacity = min(max(opacity, 0.0), 1.0)

    @property
    def alpha(self) -> float:
        """
        The opacity of the color [0.0, 1.0].

        Alias of the opacity property.
        """
        return self.opacity

    @alpha.setter
    def alpha(self, alpha: float) -> None:
        self.opacity = min(max(alpha, 0.0), 1.0)

    def delta(
        self,
        hue_delta: float,
        saturation_delta: float,
        lightness_delta: float,
        opacity_delta: float = 0.0,
    ) -> 'HSLColor':
        """
        Obtains a new color by shifting the components of this color.

        :param hue_delta: The increase of the hue component (negative values to decrease).
        :type hue_delta: float
        :param saturation_delta: The increase of the saturation component (negative values to
        decrease).
        :type saturation_delta: float
        :param lightness_delta: The increase of the lightness component (negative values to
        decrease).
        :type lightness_delta: float
        :param opacity_delta: The increase of the opacity component (negative values to
        decrease).
        :type opacity_delta: float
        :return: The resulting shifted color.
        :rtype: HSLColor
        """
        new_color: HSLColor = copy.deepcopy(self)
        new_color.hue = new_color.hue + hue_delta
        new_color.saturation = new_color.saturation + saturation_delta
        new_color.lightness = new_color.lightness + lightness_delta
        new_color.opacity = new_color.opacity + opacity_delta
        return new_color

    def to_rgba(self) -> Tuple[float, float, float, float]:
        """
        Converts the HSL color to a tuple with the RGBA components in the rangs [0.0, 1.0].

        :return: A tuple with the RGBA components
        :rtype: Tuple[float, float, float, float]
        """
        hue_abs: float = self.hue * 360.0
        c: float = (1 - abs(2 * self.lightness - 1)) * self.saturation
        x: float = c * (1 - abs((hue_abs / 60.0) % 2 - 1))
        m: float = self.lightness - c / 2.0

        if 0.0 <= hue_abs < 60.0:
            return (c + m, x + m, m, self.opacity)
        elif 60.0 <= hue_abs < 120.0:
            return (x + m, c + m, m, self.opacity)
        elif 120.0 <= hue_abs < 180.0:
            return (m, c + m, x + m, self.opacity)
        elif 180.0 <= hue_abs < 240.0:
            return (m, x + m, c + m, self.opacity)
        elif 240.0 <= hue_abs < 300.0:
            return (x + m, m, c + m, self.opacity)
        else:
            return (c + m, m, x + m, self.opacity)

    def to_css_hsl(self, legacy: bool = False) -> str:
        """
        Returns this color as an HSL string formatted for CSS3.

        :param legacy: Whether to return the color in legacy format (True) or modern, absolute
        value format (False, default)
        :type legacy: bool
        :return: The color HSL representation for CSS3.
        :rtype: str
        """
        if legacy:
            components = (
                f'{int(self.hue * 360)},{int(self.saturation * 100)}%,{int(self.lightness * 100)}%'
            )
            if self.opacity < 1.0:
                return f'hsla({components},{int(self.opacity * 100)}%)'
            return f'hsl({components})'

        components = (
            f'{int(self.hue * 360)}deg {int(self.saturation * 100)}% {int(self.lightness * 100)}%'
        )
        if self.opacity < 1.0:
            return f'hsl({components} / {int(self.opacity * 100)}%)'
        return f'hsl({components})'

    def to_css_rgb(self) -> str:
        """
        Returns this color as an RGB string formatted for CSS3.

        :return: The color RGB representation for CSS3.
        :rtype: str
        """
        rgba: Tuple[float, float, float, float] = self.to_rgba()
        components = (
            f'{rgba[0] * 100:.1f}% {rgba[1] * 100:.1f}% {rgba[2] * 100:.1f}%'
        )
        if self.opacity < 1.0:
            return f'rgb({components} / {rgba[3] * 100:.1f}%)'
        return f'rgb({components})'

    def __repr__(self) -> str:
        return f'HSLColor({self.hue}, {self.saturation}, {self.lightness}, {self.opacity})'


__all__ = [
    'HSLColor',
]
