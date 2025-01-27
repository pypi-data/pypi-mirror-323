from typing import List, Tuple
import copy
import enum
import math

from polychromos.color import HSLColor
from polychromos.easing import EasingFunctionId, get_easing_function


HSLColorSequence = List[HSLColor]
HSLColorScale = List[Tuple[float, HSLColor]]

class Palette():
    """
    Palette generation and utilities toolkit class.
    """
    class CylindricalInterpolationPath(enum.Enum):
        """
        Enumeration of approaches to cylindrical interpolation.
        """
        SHORTEST = enum.auto()
        LONGEST = enum.auto()
        FORWARD = enum.auto()
        BACKWARD = enum.auto()

    class MixIndexing(enum.Enum):
        """
        The different mix indexing strategies.
        """
        BY_POSITION = enum.auto()
        BY_USE = enum.auto()

    @staticmethod
    def complementary(
        color: HSLColor,
        mute_saturation: float = 0.0,
        mute_lightness: float = 0.0,
    ) -> HSLColor:
        """
        Calculates the complementary color of another color.

        :param color: The original color.
        :type color: HSLColor
        :param mute_saturation: How much to decrease the saturation in absolute terms;
        defaults to 0.0
        :type mute_saturation: float, optional
        :param mute_lightness: How much to decrease the lightness in absolute terms;
        defaults to 0.0
        :type mute_lightness: float, optional
        :return: The complementary color.
        :rtype: HSLColor
        """
        return color.delta(0.5, -mute_saturation, -mute_lightness)

    @staticmethod
    def triadic(
        color: HSLColor,
        mute_saturation: float = 0.0,
        mute_lightness: float = 0.0,
    ) -> Tuple[HSLColor, HSLColor]:
        """
        Calculates the triadic color scheme.

        :param color: The original color.
        :type color: HSLColor
        :param mute_saturation: How much to decrease the saturation in absolute terms;
        defaults to 0.0
        :type mute_saturation: float, optional
        :param mute_lightness: How much to decrease the lightness in absolute terms;
        defaults to 0.0
        :type mute_lightness: float, optional
        :return: A tuple with the other two colors of the scheme.
        :rtype: Tuple[HSLColor, HSLColor]
        """
        return (
            color.delta(-1.0/3, -mute_saturation, -mute_lightness),
            color.delta(1.0/3, -mute_saturation, -mute_lightness)
        )

    @staticmethod
    def split_complementary(
        color: HSLColor,
        mute_saturation: float = 0.0,
        mute_lightness: float = 0.0,
    ) -> Tuple[HSLColor, HSLColor]:
        """
        Calculates the split complementary color scheme.

        :param color: The original color.
        :type color: HSLColor
        :param mute_saturation: How much to decrease the saturation in absolute terms;
        defaults to 0.0
        :type mute_saturation: float, optional
        :param mute_lightness: How much to decrease the lightness in absolute terms;
        defaults to 0.0
        :type mute_lightness: float, optional
        :return: A tuple with the other two colors of the scheme.
        :rtype: Tuple[HSLColor, HSLColor]
        """
        return (
            color.delta(-5.0/12, -mute_saturation, -mute_lightness),
            color.delta(5.0/12, -mute_saturation, -mute_lightness)
        )

    @staticmethod
    def sequence_from_deltas(
        base_color: HSLColor,
        steps_before: int,
        steps_after: int,
        hue_delta: float,
        saturation_delta: float,
        lightness_delta: float,
    ) -> HSLColorSequence:
        """
        Generates a color sequence from a base color and the step increments of the components.

        :param base_color: The base color.
        :type base_color: HSLColor
        :param steps_before: How many steps to generate before the base color.
        :type steps_before: int
        :param steps_after: How many steps to generate after the base color.
        :type steps_after: int
        :param hue_delta: The hue increment per step, in absolute terms.
        :type hue_delta: float
        :param saturation_delta: The saturation increment per step, in absolute terms.
        :type saturation_delta: float
        :param lightness_delta: The lightness increment per step, in absolute terms.
        :type lightness_delta: float
        :raises ValueError: When a negative number of steps is given.
        :return: The color sequence.
        :rtype: HSLColorSequence
        """
        if steps_before < 0:
            raise ValueError(f'steps_before cannot be a negative number; {steps_before} given')
        if steps_after < 0:
            raise ValueError(f'steps_after cannot be a negative number; {steps_after} given')
        colors: HSLColorSequence = [base_color]
        prev_color: HSLColor = base_color
        for _ in range(steps_before):
            prev_color = prev_color.delta(-hue_delta, -saturation_delta, -lightness_delta)
            colors.append(prev_color)
        colors.reverse()
        prev_color = base_color
        for _ in range(steps_after):
            prev_color = prev_color.delta(hue_delta, saturation_delta, lightness_delta)
            colors.append(prev_color)
        return colors

    @staticmethod
    def __lerp_value(s: float, e: float, x: float) -> float:
        return s + (e - s) * x

    @staticmethod
    def lerp(
        start_color: HSLColor,
        end_color: HSLColor,
        delta: float,
    ) -> HSLColor:
        """
        Linearly interppolates between two colors.

        :param start_color: The starting color.
        :type start_color: HSLColor
        :param end_color: The final color.
        :type end_color: HSLColor
        :param delta: The relative position between the start and the end, in the range [0, 1].
        :type delta: float
        :return: The linearly interpolated color.
        :rtype: HSLColor
        """
        start_color_rgba: Tuple[float, float, float, float] = start_color.to_rgba()
        end_color_rgba: Tuple[float, float, float, float] = end_color.to_rgba()
        return HSLColor.from_rgba(
            Palette.__lerp_value(start_color_rgba[0], end_color_rgba[0], delta),
            Palette.__lerp_value(start_color_rgba[1], end_color_rgba[1], delta),
            Palette.__lerp_value(start_color_rgba[2], end_color_rgba[2], delta),
            Palette.__lerp_value(start_color_rgba[3], end_color_rgba[3], delta),
        )

    @staticmethod
    def cylindrical_slerp(
        start_color: HSLColor,
        end_color: HSLColor,
        delta: float,
        path_strategy: CylindricalInterpolationPath,
    ) -> HSLColor:
        """
        Cylindrically interppolates between two colors.

        :param start_color: The starting color.
        :type start_color: HSLColor
        :param end_color: The final color.
        :type end_color: HSLColor
        :param delta: The relative position between the start and the end, in the range [0, 1].
        :type delta: float
        :param path_strategy: The interpolation path strategy.
        Defaults to ``CylindricalInterpolationPath.SHORTEST``
        :type path_strategy: CylindricalInterpolationPath, optional
        :return: The cylindrically interpolated color.
        :rtype: HSLColor
        """
        new_hue: float = 0.0
        start_hue: float = start_color.hue
        end_hue: float = end_color.hue
        start_hue_plus_one: float = start_hue + 1.0
        end_hue_plus_one: float = end_hue + 1.0
        if path_strategy == Palette.CylindricalInterpolationPath.SHORTEST:
            if abs(end_hue_plus_one - start_hue) < abs(end_hue - start_hue):
                new_hue = Palette.__lerp_value(start_hue, end_hue_plus_one, delta)
            else:
                new_hue = Palette.__lerp_value(start_hue, end_hue, delta)
        if path_strategy == Palette.CylindricalInterpolationPath.LONGEST:
            if abs(end_hue_plus_one - start_hue) > abs(end_hue - start_hue):
                new_hue = Palette.__lerp_value(start_hue, end_hue_plus_one, delta)
            else:
                new_hue = Palette.__lerp_value(start_hue, end_hue, delta)
        elif path_strategy == Palette.CylindricalInterpolationPath.FORWARD:
            if end_hue > start_hue:
                new_hue = Palette.__lerp_value(start_hue, end_hue, delta)
            else:
                new_hue = Palette.__lerp_value(start_hue, end_hue_plus_one, delta)
        elif path_strategy == Palette.CylindricalInterpolationPath.BACKWARD:
            if end_hue >= start_hue:
                new_hue = Palette.__lerp_value(start_hue_plus_one, end_hue, delta)
            else:
                new_hue = Palette.__lerp_value(start_hue, end_hue, delta)
        return HSLColor(
            new_hue,
            Palette.__lerp_value(start_color.saturation, end_color.saturation, delta),
            Palette.__lerp_value(start_color.lightness, end_color.lightness, delta),
            Palette.__lerp_value(start_color.opacity, end_color.opacity, delta),
        )

    @staticmethod
    def sequence_from_linear_interpolation(
        start_color: HSLColor,
        end_color: HSLColor,
        steps: int,
        open_ended: bool = False,
    ) -> HSLColorSequence:
        """
        Generates a color sequence interpolating linearly between a start and end color.

        Being "linear" in a straight line, if the start and end colors have opposing hues, the
        intermediate colors will become desaturated, passing through the "center" of the
        hue-saturation wheel.

        :param start_color: The starting color.
        :type start_color: HSLColor
        :param end_color: The final color.
        :type end_color: HSLColor
        :param steps: How many steps the sequence should have (min. 2).
        :type steps: int
        :param open_ended: If ``True``, the final color is not included. Defaults to ``False``
        :type open_ended: bool, optional
        :raise ValueError: When a number of steps lower than 2 is given.
        :return: The color sequence
        :rtype: HSLColorSequence
        """
        if steps < 2:
            raise ValueError(f'steps cannot be less than two; {steps} given')
        colors: HSLColorSequence = []
        for i in range(steps - (1 if open_ended else 0)):
            colors.append(
                Palette.lerp(
                    start_color,
                    end_color,
                    i * 1.0 / (steps - 1),
                )
            )
        return colors

    @staticmethod
    def sequence_from_cylindrical_interpolation(
        start_color: HSLColor,
        end_color: HSLColor,
        steps: int,
        path_strategy: CylindricalInterpolationPath = CylindricalInterpolationPath.SHORTEST,
        open_ended: bool = False,
    ) -> HSLColorSequence:
        """
        Generates a color sequence interpolating cylindrically between two given colors.

        In the "cylindrical" interpolation the hue and the saturation are interpolated
        independently, meaning that regardless of the relative hues, no color in the interpolation
        will go nearer to the "center" of the hue-saturation wheel than the less saturated of the
        ends.

        :param start_color: The starting color.
        :type start_color: HSLColor
        :param end_color: The final color.
        :type end_color: HSLColor
        :param steps: How many steps the sequence should have (min. 2)
        :type steps: int
        :param path_strategy: The interpolation path strategy.
        Defaults to ``CylindricalInterpolationPath.SHORTEST``
        :type path_strategy: CylindricalInterpolationPath, optional
        :param open_ended: If ``True`` the final color is not included in the sequence.
        Defaults to ``False``
        :raise ValueError: When a number of steps lower than 2 is given.
        :type open_ended: bool, optional
        :return: The color sequence
        :rtype: HSLColorSequence
        """
        if steps < 2:
            raise ValueError(f'steps cannot be less than two; {steps} given')
        colors: HSLColorSequence = []
        for i in range(steps - (1 if open_ended else 0)):
            colors.append(
                Palette.cylindrical_slerp(
                    start_color,
                    end_color,
                    i * 1.0 / (steps - 1),
                    path_strategy,
                )
            )
        return colors

    @staticmethod
    def sequence_from_elliptical_interpolation(
        start_color: HSLColor,
        end_color: HSLColor,
        steps: int,
        straightening: float = 0.5,
        open_ended: bool = False,
    ) -> HSLColorSequence:
        """
        Generates a color sequence interpolating elliptically between a start and an end color.

        Is a combination between a cylindrical (shortest path) and a linear interpolation.

        :param start_color: The starting color.
        :type start_color: HSLColor
        :param end_color: The final color.
        :type end_color: HSLColor
        :param steps: How many steps the sequence should have (min. 2)
        :type steps: int
        :param straightening: The straightening factor in the range [0, 1]. A factor of 0.0 is
        equivalent to a cylindrical interpolation. A factor of 1.0 is equivalent to a linear
        interpolation. Defaults to 0.5
        :type straightening: float, optional
        :param open_ended: If ``True``, the final color is not included in the sequence.
        Defaults to False
        :type open_ended: bool, optional
        :return: The color sequence.
        :rtype: HSLColorSequence
        """
        straightening = max(min(straightening, 1.0), 0.0)
        linear: HSLColorSequence = Palette.sequence_from_linear_interpolation(
            start_color,
            end_color,
            steps,
            open_ended=open_ended,
        )
        cylindrical: HSLColorSequence = Palette.sequence_from_cylindrical_interpolation(
            start_color,
            end_color,
            steps,
            path_strategy=Palette.CylindricalInterpolationPath.SHORTEST,
            open_ended=open_ended,
        )
        def lerp_colors(a: HSLColor, b: HSLColor, x: float) -> HSLColor:
            a_rgba = a.to_rgba()
            b_rgba = b.to_rgba()
            return HSLColor.from_rgba(
                Palette.__lerp_value(a_rgba[0], b_rgba[0], x),
                Palette.__lerp_value(a_rgba[1], b_rgba[1], x),
                Palette.__lerp_value(a_rgba[2], b_rgba[2], x),
                Palette.__lerp_value(a_rgba[3], b_rgba[3], x),
            )
        elliptical: HSLColorSequence = list(
            map(
                lambda colors: lerp_colors(colors[0], colors[1], straightening),
                zip(cylindrical, linear)
            )
        )
        return elliptical

    @staticmethod
    def sequence_from_multiple_linear_interpolation(
        colors: HSLColorSequence,
        steps: List[int],
        open_ended: bool = False,
    ) -> HSLColorSequence:
        """
        Generates a color sequence from the linear interpolations between several colors.

        The intermediate colors are the end colors of the previous subsequences and the start colors
        of the next subsequences.

        :param colors: A list of N colors.
        :type colors: HSLColorSequence
        :param steps: A list of N-1 steps for each of the subsequences.
        :type steps: List[int]
        :param open_ended: If ``True`` the last color of the ``colors`` parameter is not included in
        the complete sequence. Defaults to ``False``
        :type open_ended: bool, optional
        :raises ValueError: When the size of the colors and steps lists do not follow a N:N-1 ratio,
        or when an invalid value is passed to one of the subsequences (e.g. a negative number of
        steps)
        :return: The complete sequence.
        :rtype: HSLColorSequence
        """
        if len(steps) != len(colors) - 1:
            raise ValueError(
                f'Length of steps array ({len(steps)}) must be exactly one less than '
                f'the length of colors array ({len(colors)})'
            )

        gradient: HSLColorSequence = []
        for i, partial_steps in enumerate(steps):
            partial_gradient: HSLColorSequence = Palette.sequence_from_linear_interpolation(
                colors[i],
                colors[i + 1],
                partial_steps,
                open_ended=True,
            )
            gradient.extend(partial_gradient)

        if not open_ended:
            gradient.append(colors[len(colors) - 1])

        return gradient

    @staticmethod
    def sequence_from_multiple_cylindrical_interpolation(
        colors: HSLColorSequence,
        steps: List[int],
        strategy: CylindricalInterpolationPath = CylindricalInterpolationPath.SHORTEST,
        open_ended: bool = False,
    ) -> HSLColorSequence:
        """
        Generates a color sequence from the cylindrical interpolations between several colors.

        The intermediate colors are the end colors of the previous subsequences and the start colors
        of the next subsequences.

        :param colors: A list of N colors.
        :type colors: HSLColorSequence
        :param steps: A list of N-1 steps for each of the subsequences.
        :type steps: List[int]
        :param open_ended: If ``True`` the last color of the ``colors`` parameter is not included in
        the complete sequence. Defaults to ``False``
        :type open_ended: bool, optional
        :raises ValueError: When the size of the colors and steps lists do not follow a N:N-1 ratio,
        or when an invalid value is passed to one of the subsequences (e.g. a negative number of
        steps)
        :return: The complete sequence.
        :rtype: HSLColorSequence
        """
        if len(steps) != len(colors) - 1:
            raise ValueError(
                f'Length of steps array ({len(steps)}) must be exactly one less than '
                f'the length of colors array ({len(colors)})'
            )

        gradient: HSLColorSequence = []
        for i, partial_steps in enumerate(steps):
            partial_gradient: HSLColorSequence = Palette.sequence_from_cylindrical_interpolation(
                colors[i],
                colors[i + 1],
                partial_steps,
                path_strategy=strategy,
                open_ended=True,
            )
            gradient.extend(partial_gradient)

        if not open_ended:
            gradient.append(colors[len(colors) - 1])

        return gradient

    @staticmethod
    def sequence_from_multiple_elliptical_interpolation(
        colors: HSLColorSequence,
        steps: List[int],
        straightening: float = 0.5,
        open_ended: bool = False,
    ) -> HSLColorSequence:
        """
        Generates a color sequence from the elliptical interpolations between several colors.

        The intermediate colors are the end colors of the previous subsequences and the start colors
        of the next subsequences.

        :param colors: A list of N colors.
        :type colors: HSLColorSequence
        :param steps: A list of N-1 steps for each of the subsequences.
        :type steps: List[int]
        :param straightening: The straightening factor in the range [0, 1]. A factor of 0.0 is
        equivalent to a cylindrical interpolation. A factor of 1.0 is equivalent to a linear
        interpolation. Defaults to 0.5
        :type straightening: float, optional
        :param open_ended: If ``True`` the last color of the ``colors`` parameter is not included in
        the complete sequence. Defaults to ``False``
        :type open_ended: bool, optional
        :raises ValueError: When the size of the colors and steps lists do not follow a N:N-1 ratio,
        or when an invalid value is passed to one of the subsequences (e.g. a negative number of
        steps)
        :return: The complete sequence.
        :rtype: HSLColorSequence
        """
        if len(steps) != len(colors) - 1:
            raise ValueError(
                f'Length of steps array ({len(steps)}) must be exactly one less than '
                f'the length of colors array ({len(colors)})'
            )

        gradient: HSLColorSequence = []
        for i, partial_steps in enumerate(steps):
            partial_gradient: HSLColorSequence = Palette.sequence_from_elliptical_interpolation(
                colors[i],
                colors[i + 1],
                partial_steps,
                straightening=straightening,
                open_ended=True,
            )
            gradient.extend(partial_gradient)

        if not open_ended:
            gradient.append(colors[len(colors) - 1])

        return gradient

    @staticmethod
    def to_css_hsl_list(colors: HSLColorSequence) -> List[str]:
        """
        Generates a sequence of CSS HSL colors from a sequence of colors.

        :param colors: The original colors sequence.
        :type colors: HSLColorSequence
        :return: The sequence of CSS HSL colors.
        :rtype: List[str]
        """
        return list(map(lambda c: c.to_css_hsl(), colors))

    @staticmethod
    def alternate_colors(colors: HSLColorSequence) -> HSLColorSequence:
        """
        Alternates the colors of the sequence so there is a significant difference between each
        step and its neighbors.

        This assumes the colors in the sequence are ordered somehow (e.g., by hue, by saturation...)
        The shuffling/alternating sequence, for a sequence of N colors, is:
        ``1, N/2+1, 2, N/2+2 ... N/2, N``

        It is particularly useful when the sequence is used to plot categorical data that will be
        placed side-by-side in no particular order.

        :param colors: The original color sequence.
        :type colors: HSLColorSequence
        :return: The new, "shuffled" color sequence.
        :rtype: HSLColorSequence
        """
        old_colors: HSLColorSequence = copy.copy(colors)
        new_colors: HSLColorSequence = []
        flag: bool = False
        flag = False
        for i in range(len(old_colors)):
            new_colors.append(
                old_colors[math.floor(math.ceil(len(old_colors) / 2) + i / 2 if flag else i / 2)]
            )
            flag = not flag
        return new_colors

    @staticmethod
    def to_color_scale(
        colors: HSLColorSequence,
        easing_function: EasingFunctionId = EasingFunctionId.NO_EASING,
    ) -> HSLColorScale:
        """
        Generates a color scale (a sequence of tuples, each with a position in the range [0, 1] and
        a color) from a color sequence, so it can be interpolated linearly as color gradients.

        If colors are to be more concentrated at one (or both) of the scale sequence, easing
        functions can be used.

        :param colors: The color sequence to generate the scale from.
        :type colors: HSLColorSequence
        :param easing_function: An optional easing function. Defaults to
        ``EasingFunctionId.NO_EASING``, meaning the colors of the sequence are distributed evenly
        across the scale.
        :type easing_function: EasingFunctionId, optional
        :raises ValueError: When less than two colors are provided in the sequence.
        :return: The new color scale.
        :rtype: HSLColorScale
        """
        if len(colors) < 2:
            raise ValueError('At least two colors are required to create a scale')
        color_scale: HSLColorScale = []
        position_delta: float = 1.0 / (len(colors) - 1)
        for i, color in enumerate(colors):
            color_scale.append((i * position_delta, color))
        for i, color_stop in enumerate(color_scale):
            color_scale[i] = (get_easing_function(easing_function)(color_stop[0]), color_stop[1])
        return color_scale

    @staticmethod
    def mix_color_sequences(
        col_seq_a: HSLColorSequence,
        col_seq_b: HSLColorSequence,
        selectors: List[bool],
        indexing: MixIndexing = MixIndexing.BY_POSITION,
    ) -> HSLColorSequence:
        """
        Combines two sequences into a single one.

        The resulting sequence will contain as many colors as selectors in the parameter
        ``selectors``, picking colors from the sequence A ``col_seq_a`` or the sequence B
        ``col_seq_b``, depending on the value of each of the selectors.

        :param col_seq_a: The colors to use for the ``False`` selectors.
        :type col_seq_a: HSLColorSequence
        :param col_seq_b: The colors to use for the ``True`` selectors.
        :type col_seq_b: HSLColorSequence
        :param selectors: The list of selectors (``False`` to pick colors from ``col_seq_a``,
        ``True`` to pick colors from ``col_seq_b``).
        :type selectors: List[bool]
        :param indexing: How to pick the colors from the sequences. Picking them by position means
        that the color depends only on the position inside the resulting sequence, cycling,
        regardless of how many times that sequence has been picked colors from. Picking them by use
        means that the colors are picked in order, regardless of the position in the resulting
        sequence. Defaults to MixIndexing.BY_POSITION
        :type indexing: MixIndexing, optional
        :return: A new sequence mixing colors from the other two.
        :rtype: HSLColorSequence
        """
        mixed: HSLColorSequence = []
        a_cur: int = 0
        b_cur: int = 0
        for i, selector in enumerate(selectors):
            if selector:
                mixed.append(col_seq_b[b_cur])
            else:
                mixed.append(col_seq_a[a_cur])

            if indexing == Palette.MixIndexing.BY_POSITION:
                a_cur = i + 1
                b_cur = i + 1
            elif indexing == Palette.MixIndexing.BY_USE:
                if selector:
                    b_cur += 1
                else:
                    a_cur += 1
            a_cur = a_cur % len(col_seq_a)
            b_cur = b_cur % len(col_seq_b)

        return mixed


__all__ = [
    'Palette',
    'HSLColorSequence',
    'HSLColorScale',
]
