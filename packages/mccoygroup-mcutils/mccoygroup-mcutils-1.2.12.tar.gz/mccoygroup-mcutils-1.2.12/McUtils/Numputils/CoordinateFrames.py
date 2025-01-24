
__all__ = [
    "center_of_mass",
    "inertia_tensors",
    "moments_of_inertia",
    "inertial_frame_derivatives",
    "translation_rotation_eigenvectors",
    "remove_translation_rotations",
    "translation_rotation_invariant_transformation"
]

import numpy as np
from . import VectorOps as vec_ops
from . import TensorDerivatives as td_ops
from . import SetOps as set_ops

def center_of_mass(coords, masses):
    """Gets the center of mass for the coordinates

    :param coords:
    :type coords: CoordinateSet
    :param masses:
    :type masses:
    :return:
    :rtype:
    """

    masses = masses.copy()
    masses[masses < 0] = 0

    return np.tensordot(masses / np.sum(masses), coords, axes=[0, -2])

def inertia_tensors(coords, masses):
    """
    Computes the moment of intertia tensors for the walkers with coordinates coords (assumes all have the same masses)

    :param coords:
    :type coords: CoordinateSet
    :param masses:
    :type masses: np.ndarray
    :return:
    :rtype:
    """

    com = center_of_mass(coords, masses)
    coords = coords - com[..., np.newaxis, :]

    real_spots = masses > 0 # allow for dropping out dummy atoms
    coords = coords[..., real_spots, :]
    masses = masses[real_spots]

    d = np.zeros(coords.shape[:-1] + (3, 3), dtype=float)
    diag = vec_ops.vec_dots(coords, coords)
    d[..., (0, 1, 2), (0, 1, 2)] = diag[..., np.newaxis]
    # o = np.array([[np.outer(a, a) for a in r] for r in coords])
    o = vec_ops.vec_outer(coords, coords, axes=[-1, -1])
    tens = np.tensordot(masses, d - o, axes=[0, -3])

    return tens

def inertial_frame_derivatives(crds, mass, sel=None):
    mass = np.asanyarray(mass)
    crds = np.asanyarray(crds)
    real_pos = mass > 0
    if sel is not None:
        real_pos = np.intersect1d(sel, real_pos)

    smol = crds.ndim == 2
    if smol:
        crds = crds[np.newaxis]
    base_shape = crds.shape[:-2]
    crds = crds.reshape((-1,) + crds.shape[-2:])
    if mass.ndim == 1:
        mass = mass[np.newaxis]
    else:
        mass = np.reshape(mass, (-1, mass.shape[-1]))

    mass = mass[..., real_pos]
    crds = crds[..., real_pos, :]

    mass = np.sqrt(mass)
    carts = mass[..., :, np.newaxis] * crds  # mass-weighted Cartesian coordinates

    ### compute basic inertia tensor derivatives
    # first derivs are computed as a full (nAt, 3, I_rows (3), I_cols (3)) tensor
    # and then reshaped to (nAt * 3, I_rows, I_cols)
    eyeXeye = np.eye(9).reshape(3, 3, 3, 3).transpose((2, 0, 1, 3))
    I0Y_1 = np.tensordot(carts, eyeXeye, axes=[2, 0])

    nAt = carts.shape[1]
    nY = nAt * 3
    I0Y_21 = (
            np.reshape(np.eye(3), (9,))[np.newaxis, :, np.newaxis]
            * carts[:, :, np.newaxis, :]
    )  # a flavor of outer product
    I0Y_21 = I0Y_21.reshape((-1, nAt, 3, 3, 3))
    I0Y_2 = (I0Y_21 + I0Y_21.transpose((0, 1, 2, 4, 3)))
    I0Y = 2 * I0Y_1 - I0Y_2
    I0Y = I0Y.reshape(base_shape + (nY, 3, 3))

    # second derivatives are 100% independent of coorinates
    # only the diagonal blocks are non-zero, so we compute that block
    # and then tile appropriately
    keyXey = np.eye(9).reshape(3, 3, 3, 3)
    I0YY_nn = 2 * eyeXeye - (keyXey + keyXey.transpose((0, 1, 3, 2)))
    I0YY = np.zeros((nAt, 3, nAt, 3, 3, 3))
    for n in range(nAt):
        I0YY[n, :, n, :, :, :] = I0YY_nn
    I0YY = I0YY.reshape((nY, nY, 3, 3))
    I0YY = np.broadcast_to(I0YY[np.newaxis, :, :, :, :], (carts.shape[0],) + I0YY.shape)
    I0YY = np.reshape(I0YY, base_shape + (nY, nY, 3, 3))

    if smol:
        I0Y = I0Y[0]
        I0YY = I0YY[0]

    return [I0Y, I0YY]

def moments_of_inertia(coords, masses):
    """
    Computes the moment of inertia tensor for the walkers with coordinates coords (assumes all have the same masses)

    :param coords:
    :type coords: CoordinateSet
    :param masses:
    :type masses: np.ndarray
    :return:
    :rtype:
    """

    if coords.ndim == 1:
        raise ValueError("can't get moment of inertia for single point (?)")
    elif coords.ndim == 2:
        multiconfig = False
        coords = coords[np.newaxis]
        extra_shape = None
    else:
        multiconfig = True
        extra_shape = coords.shape[:-2]
        coords = coords.reshape((np.prod(extra_shape),) + coords.shape[-2:])

    massy_doop = inertia_tensors(coords, masses)
    moms, axes = np.linalg.eigh(massy_doop)
    # a = axes[..., :, 0]
    # c = axes[..., :, 2]
    # b = nput.vec_crosses(a, c)  # force right-handedness to avoid inversions
    # axes[..., :, 1] = b
    a = axes[..., :, 0]
    b = axes[..., :, 1]
    c = vec_ops.vec_crosses(b, a)  # force right-handedness to avoid inversions
    axes[..., :, 2] = c
    dets = np.linalg.det(axes) # ensure we have true rotation matrices to avoid inversions
    axes[..., :, 2] /= dets[..., np.newaxis]

    if multiconfig:
        moms = moms.reshape(extra_shape + (3,))
        axes = axes.reshape(extra_shape + (3, 3))
    else:
        moms = moms[0]
        axes = axes[0]
    return moms, axes

def translation_rotation_eigenvectors(coords, masses, mass_weighted=True):
    """
    Returns the eigenvectors corresponding to translations and rotations
    in the system

    :param coords:
    :type coords:
    :param masses:
    :type masses:
    :return:
    :rtype:
    """

    n = len(masses)
    # explicitly put masses in m_e from AMU
    # masses = UnitsData.convert("AtomicMassUnits", "AtomicUnitOfMass") * masses
    mT = np.sqrt(np.sum(masses))
    mvec = np.sqrt(masses)

    # no_derivs = order is None
    # if no_derivs:
    #     order = 0

    smol = coords.ndim == 2
    if smol:
        coords = coords[np.newaxis]
    # base_shape = None
    # if coords.ndim > 3:
    base_shape = coords.shape[:-2]
    coords = coords.reshape((-1,) + coords.shape[-2:])

    M = np.kron(mvec / mT, np.eye(3)).T  # translation eigenvectors
    mom_rot, ax_rot = moments_of_inertia(coords, masses)
    # if order > 0:
    #     base_tensor = StructuralProperties.get_prop_inertia_tensors(coords, masses)
    #     mom_expansion = StructuralProperties.get_prop_inertial_frame_derivatives(coords, masses)
    #     inertia_expansion = [base_tensor] + mom_expansion
    #     sqrt_expansion = nput.matsqrt_deriv(inertia_expansion, order)
    #     inv_rot_expansion = nput.matinv_deriv(sqrt_expansion, order=order)
    #     inv_rot_2 = inv_rot_expansion[0]
    # else:
    inv_mom_2 = vec_ops.vec_tensordiag(1 / np.sqrt(mom_rot))
    inv_rot_2 = vec_ops.vec_tensordot(
        ax_rot,
        vec_ops.vec_tensordot(
            ax_rot,
            inv_mom_2,
            shared=1,
            axes=[-1, -1]
        ),
        shared=1,
        axes=[-1, -1]
    )
    # inv_rot_expansion = [inv_rot_2]
    com = center_of_mass(coords, masses)
    com = np.expand_dims(com, 1) # ???
    shift_crds = mvec[np.newaxis, :, np.newaxis] * (coords - com[: np.newaxis, :])
    # if order > 0:
    #     # could be more efficient but oh well...
    #     e = np.broadcast_to(nput.levi_cevita3[np.newaxis], (shift_crds.shape[0], 3, 3, 3))
    #     n = shift_crds.shape[-2]
    #     shift_crd_deriv = np.broadcast_to(
    #         np.eye(3*n).reshape(3*n, n, 3)[np.newaxis],
    #         (shift_crds.shape[0], 3*n, n, 3)
    #     )
    #     shift_crd_expansion = [shift_crds]
    #     R_expansion = nput.tensorops_deriv(
    #         shift_crd_expansion,
    #             [-1, -1],
    #         [e],
    #             [-1, -2],
    #         inv_rot_expansion,
    #         order=order,
    #         shared=1
    #     )
    #     with np.printoptions(linewidth=1e8):
    #         print()
    #         # print(R_expansion[0][0])
    #         print(R_expansion[1][0].reshape(3*n, 3*n, 3)[:, :, 0])
    #         print(
    #             np.moveaxis(
    #                 np.tensordot(
    #                     np.tensordot(shift_crds[0], e[0], axes=[-1, 1]),
    #                     inv_rot_expansion[1][0],
    #                     axes=[1, -1]
    #                 ),
    #                 -2,
    #                 0
    #             ).reshape(15, 15, 3)[:, :, 0]
    #         )
    #     raise Exception(...)
    #     R_expansion = [
    #         r.reshape(r.shape[:-3] + (r.shape[-3]*r.shape[-2], r.shape[-1]))
    #         for r in R_expansion
    #     ]
    #     R = R_expansion[0]
    #     raise Exception(R_expansion[1][0] - np.moveaxis(R_expansion[1][0], 1, 0))
    #
    # else:
    cos_rot = td_ops.levi_cevita_dot(3, inv_rot_2, axes=[0, -1], shared=1) # kx3bx3cx3j
    R = vec_ops.vec_tensordot(
        shift_crds, cos_rot,
        shared=1,
        axes=[-1, 1]
    ).reshape((coords.shape[0], 3 * n, 3))  # rotations
    # raise Exception(R)

    freqs = np.concatenate([
        np.broadcast_to([[1e-14, 1e-14, 1e-14]], mom_rot.shape),
        (1 / (2 * mom_rot))
        # this isn't right, I'm totally aware, but I think the frequency is supposed to be zero anyway and this
        # will be tiny
    ], axis=-1)
    M = np.broadcast_to(M[np.newaxis], R.shape)
    eigs = np.concatenate([M, R], axis=2)

    if not mass_weighted:
        W = np.diag(np.repeat(1/np.sqrt(masses), 3))
        eigs = np.moveaxis(np.tensordot(eigs, W, axes=[-2, 0]), -1, -2)

    if smol:
        eigs = eigs[0]
        freqs = freqs[0]
    else:
        eigs = eigs.reshape(base_shape + eigs.shape[1:])
        freqs = freqs.reshape(base_shape + freqs.shape[1:])

    return freqs, eigs

def translation_rotation_projector(coords, masses=None, mass_weighted=False, return_modes=False):
    if masses is None:
        masses = np.ones(coords.shape[-2])
    _, tr_modes = translation_rotation_eigenvectors(coords, masses, mass_weighted=mass_weighted)
    shared = tr_modes.ndim - 2
    eye = vec_ops.identity_tensors(tr_modes.shape[:-2], tr_modes.shape[-2])
    projector = eye - vec_ops.vec_tensordot(tr_modes, tr_modes, axes=[-1, -1], shared=shared)

    if return_modes:
        return projector, tr_modes
    else:
        return projector


def remove_translation_rotations(expansion, coords, masses=None, mass_weighted=False):
    projector = translation_rotation_projector(coords, masses=masses, mass_weighted=mass_weighted)
    shared = projector.ndim - 2

    proj_expansion = []
    for n,d in enumerate(expansion):
        for ax in range(n+1):
            d = vec_ops.vec_tensordot(projector, d, axes=[-1, shared+ax], shared=shared)
        proj_expansion.append(d)

    return proj_expansion

def translation_rotation_invariant_transformation(
        coords, masses,
        mass_weighted=True,
        strip_embedding=True
):
    A, L_tr = translation_rotation_projector(coords, masses, mass_weighted=True, return_modes=True)
    base_shape = A.shape[:-2]
    A = A.reshape((-1,) + A.shape[-2:])
    L_tr = L_tr.reshape((-1,) + L_tr.shape[-2:])
    evals, tf = np.linalg.eigh(A)
    # zero_pos = np.where(np.abs(evals) < 1e-4) # the rest should be 1
    # raise Exception(
    #     evals.shape,
    #     zero_pos,
    #     # set_ops.vector_ix(tf.shape, zero_pos)
    # )

    # zero_pos = zero_pos[:-1] + (slice(None),) + zero_pos[-1:]
    # raise Exception(zero_pos, tf.shape, tf[zero_pos].shape, L_tr.shape)
    # tf[zero_pos] = np.moveaxis(L_tr)
    tf[:, :, :6] = L_tr
    if strip_embedding:
        # nzpos = np.where(np.abs(evals) > 1e-4) # the rest should be 1
        # nzpos = nzpos[:-1] + (slice(None),) + nzpos[-1:]
        tf = tf[:, :, 6:]
    else:
        tf[:, :, :6] = L_tr

    inv = np.moveaxis(tf, -1, -2)
    if not mass_weighted:
        W = np.diag(np.repeat(np.sqrt(masses), 3))
        tf = np.moveaxis(
            np.tensordot(W, tf, axes=[0, 1]),
            1, 0
        )

        W = np.diag(np.repeat(1/np.sqrt(masses), 3))
        inv = np.tensordot(inv, W, axes=[2, 0])

    tf = tf.reshape(base_shape + tf.shape[-2:])
    inv = inv.reshape(base_shape + inv.shape[-2:])

    return tf, inv