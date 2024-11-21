# Copyright 2021 The NetKet Authors - All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from itertools import count

import numpy as np

from netket.utils.float import is_approx_int
from netket.utils.types import Array
from netket.utils.moduletools import export, hide_unexported

from ._point_group import PGSymmetry, PointGroup
from ._semigroup import Identity

hide_unexported(__name__)

__all__ = ["rotation_group", "pyramidal", "dihedral", "prismatic", "antiprismatic"]


@export
def rotation(angle: float, axis: Array) -> PGSymmetry:
    """Returns a rotation by `angle` degrees around `axis`."""
    angle = np.radians(angle)
    axis = np.asarray(axis) / np.linalg.norm(axis)
    return PGSymmetry(
        np.cos(angle) * np.eye(3)
        + np.sin(angle) * np.cross(np.eye(3), axis)
        + (1 - np.cos(angle)) * np.outer(axis, axis)
    )


@export
def C(n: int, axis: Array = (0, 0, 1)) -> PointGroup:
    """
    Returns the :math:`C_n` `PointGroup` of rotations around a given axis.

    Arguments:
        n: the index of the rotation group (the smallest rotation angle is 360°/n)
        axis: the axis of rotations, need not be normalised, defaults to the z-axis

    Returns:
        a `PointGroup` implementing :math:`C_n`
    """
    return PointGroup(
        [Identity()] + [rotation(360 / n * i, axis) for i in range(1, n)], ndim=3
    )


rotation_group = C


@export
def screw(angle: float, trans: Array, origin: Array = (0, 0, 0)) -> PGSymmetry:
    """Returns a screw composed of a translation by `trans` and a rotation by `angle`
    degrees around its direction. The axis passes through `origin` (defaults to
    the Cartesian origin)."""
    angle = np.radians(angle)
    axis = np.asarray(trans) / np.linalg.norm(trans)
    W = (
        np.cos(angle) * np.eye(3)
        + np.sin(angle) * np.cross(np.eye(3), axis)
        + (1 - np.cos(angle)) * np.outer(axis, axis)
    )
    w = np.asarray(trans) + (np.eye(3) - W) @ np.asarray(origin)
    return PGSymmetry(W, w)


@export
def screw_group(angle: float, trans: Array, origin: Array = (0, 0, 0)) -> PointGroup:
    """Returns the `PointGroup` generated by a screw composed of a translation
    by `trans` and a rotation by `angle` degrees around its direction.

    The axis passes through `origin` (defaults to the Cartesian origin).
    The order of the group is controlled by `angle`.
    The output is only a valid `PointGroup` after supplying a `unit_cell`
    consistent with the screw axis; otherwise, operations like `product_table`
    will fail.
    """
    out = [Identity()]
    trans = np.asarray(trans)
    for i in count(start=1):
        if is_approx_int(i * angle / 360):
            break
        out.append(screw(i * angle, i * trans, origin))
    return PointGroup(out, ndim=3)


@export
def inversion() -> PGSymmetry:
    """Returns a 3D inversion as a `PGSymmetry`."""
    return PGSymmetry(-np.eye(3))


@export
def inversion_group() -> PGSymmetry:
    r"""
    :math:`\mathbb{Z}_2` `PointGroup` containing the identity and inversion across
    the origin.
    """
    return PointGroup([Identity(), inversion()], ndim=3)


@export
def reflection(axis: Array) -> PGSymmetry:
    r"""Returns a 3D reflection across a plane whose normal is `axis`.

    .. warning::

        For 2D reflections see
        :func:`netket.utils.group.planar.reflection`.

    Args:
        axis: The 3-component basis vector identifying the reflection axis,
            for example :code:`np.array([1,0,0])`.

    """
    if len(axis) != 3:
        raise ValueError(
            "The axis must be a 3 component vector."
            "If you want reflections in 2 dimensions, use "
            "nk.utils.group.planar.reflection instead."
        )

    axis = np.asarray(axis) / np.linalg.norm(axis)
    return PGSymmetry(np.eye(3) - 2 * np.outer(axis, axis))


@export
def reflection_group(axis: Array) -> PointGroup:
    r"""
    Returns the :math:`\mathbb{Z}_2` `PointGroup` containing the identity and a
    reflection across a plane with normal `axis`
    """
    return PointGroup([Identity(), reflection(axis)], ndim=3)


@export
def glide(axis: Array, trans: Array, origin: Array = (0, 0, 0)) -> PGSymmetry:
    r"""
    Returns a glide composed of translation by `trans` and a reflection across a
    plane that passes through `origin` and is normal to `axis`.

    `trans` and `axis` must be perpendicular.
    `origin` defaults to the Cartesian origin.
    """
    assert np.isclose(np.dot(axis, trans), 0.0)
    axis = np.asarray(axis) / np.linalg.norm(axis)
    W = np.eye(3) - 2 * np.outer(axis, axis)
    w = np.asarray(trans) + (np.eye(3) - W) @ np.asarray(origin)
    return PGSymmetry(W, w)


@export
def glide_group(axis: Array, trans: Array, origin: Array = (0, 0, 0)) -> PointGroup:
    r"""
    Returns the Z_2 `PointGroup` containing the identity and a glide composed of
    translation by `trans` and a reflection across a plane that passes through
    `origin` and is normal to `axis`.

    `trans` and `axis` must be perpendicular.
    `origin` defaults to the Cartesian origin.
    The output is only a valid `PointGroup` after supplying a `unit_cell`
    consistent with the glide plane; otherwise, operations like `product_table`
    will fail.
    """
    return PointGroup([Identity(), glide(axis, trans, origin)], ndim=3)


@export
def Ch(n: int, axis: Array = (0, 0, 1)) -> PointGroup:
    r"""
    Returns the reflection group :math:`C_{nh}` generated by an *n*-fold rotation axis
    and a reflection across the plane normal to the same axis.

    Arguments:
        n: index of the group
        axis: the axis of rotations and normal to the mirror plane, need not be
            normalised, defaults to the z-axis

    Returns:
        a `PointGroup` object implementing :math:`C_{nh}`
    """
    return reflection_group(axis) @ C(n, axis)


@export
def Cv(n: int, axis: Array = (0, 0, 1), axis2=(1, 0, 0)) -> PointGroup:
    r"""
    Returns the pyramidal group :math:`C_{nv}` generated by an *n*-fold rotation axis
    and a reflection across a plane that contains the same axis.

    Arguments:
        n: index of the group
        axis: the axis of rotations, need not be normalised, defaults to the z-axis
        axis2: normal of the generating mirror plane, need not be normalised, must
            be perpendicular to `axis`, defaults to the x-axis

    Returns:
        a `PointGroup` object implementing :math:`C_{nv}`
    """
    assert np.isclose(np.dot(axis, axis2), 0.0)
    return reflection_group(axis2) @ C(n, axis)


pyramidal = Cv


@export
def rotoreflection(angle: float, axis: Array) -> PGSymmetry:
    """Returns a rotoreflection by `angle` degrees around `axis`."""
    angle = np.radians(angle)
    axis = np.asarray(axis) / np.linalg.norm(axis)
    rot_matrix = (
        np.cos(angle) * np.eye(3)
        + np.sin(angle) * np.cross(np.eye(3), axis)
        + (1 - np.cos(angle)) * np.outer(axis, axis)
    )
    refl_matrix = np.eye(3) - 2 * np.outer(axis, axis)
    return PGSymmetry(refl_matrix @ rot_matrix)


@export
def S(n: int, axis: Array = (0, 0, 1)) -> PointGroup:
    """
    Returns the :math:`S_n` `PointGroup` of rotoreflections around a given axis.

    Arguments:
        n: the index of the rotoreflection group (the smallest rotation angle is 360°/n)
        axis: the axis, need not be normalised, defaults to the z-axis

    Returns:
        a `PointGroup` implementing :math:`S_n`
    """
    if n % 2 == 1:
        return Ch(n, axis)
    else:
        return PointGroup(
            [Identity()]
            + [
                (
                    rotoreflection(360 / n * i, axis)
                    if i % 2 == 1
                    else rotation(360 / n * i, axis)
                )
                for i in range(1, n)
            ],
            ndim=3,
        )


rotoreflection_group = S
export(rotoreflection_group)


@export
def D(n: int, axis: Array = (0, 0, 1), axis2: Array = (1, 0, 0)) -> PointGroup:
    """
    Returns the dihedral group :math:`D_n` generated by an *n*-fold rotation axis
    and a twofold rotation axis perpendicular to the former.

    Arguments:
        n: index of the group
        axis: the n-fold rotation axis, need not be normalised, defaults to the z-axis
        axis2: generating twofold rotation axis, need not be normalised, must be
            perpendicular to `axis`, defaults to the x-axis

    Returns:
        a `PointGroup` object implementing :math:`D_n`
    """
    assert np.isclose(np.dot(axis, axis2), 0.0)
    return C(2, axis2) @ C(n, axis)


dihedral = D


@export
def cuboid_rotations() -> PointGroup:
    """Rotational symmetries of a cuboid with edges aligned with the Cartesian axes."""
    return D(2)


@export
def Dh(n: int, axis: Array = (0, 0, 1), axis2=(1, 0, 0)) -> PointGroup:
    """
    Returns the prismatic group :math:`D_{nh}` generated by an *n*-fold rotation axis,
    a twofold rotation axis perpendicular to the former, and a mirror plane normal
    to the *n*-fold axis.

    Arguments:
        n: index of the group
        axis: the n-fold rotation axis and normal to the mirror plane,
            need not be normalised, defaults to the z-axis
        axis2: generating twofold rotation axis, need not be normalised,
            must be perpendicular to `axis`, defaults to the x-axis

    Returns:
        a `PointGroup` object implementing :math:`D_{nh}`
    """
    return reflection_group(axis) @ D(n, axis, axis2)


prismatic = Dh


@export
def cuboid() -> PointGroup:
    """Symmetry group of a cuboid with edges aligned with the Cartesian axes."""
    return Dh(2)


@export
def Dd(n: int, axis: Array = (0, 0, 1), axis2=(1, 0, 0)) -> PointGroup:
    """
    Returns the antiprismatic group :math:`D_{nd}` generated by a 2*n*-fold roto-
    reflection axis and a reflection across a plane that contains the same axis.

    Arguments:
        n: index of the group
        axis: the rotoreflection axis, need not be normalised, defaults to the z-axis
        axis2: normal of the generating mirror plane, need not be normalised, must be
            perpendicular to `axis`, defaults to the x-axis

    Returns:
        a `PointGroup` object implementing :math:`D_{nd}`
    """
    assert np.isclose(np.dot(axis, axis2), 0.0)
    return reflection_group(axis2) @ S(2 * n, axis)


antiprismatic = Dd
