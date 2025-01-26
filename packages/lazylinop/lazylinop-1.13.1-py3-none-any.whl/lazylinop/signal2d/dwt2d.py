import numpy as np
from lazylinop import LazyLinOp
from lazylinop.basicops import block_diag, eye, kron, vstack
from lazylinop.signal.dwt import dwt, _wavelet, _max_level, _ncoeffs
from lazylinop.signal.utils import chunk
import sys
sys.setrecursionlimit(100000)


def dwt2d(in_shape: tuple, wavelet: str = 'haar',
          mode: str = 'zero', level: int = None,
          backend: str = 'pywavelets'):
    """
    Returns a :class:`.LazyLinOp` ``L`` for the 2D
    Discrete-Wavelet-Transform (DWT) of a 2D signal of shape
    ``in_shape = (M, N)`` (provided in flattened version).

    ``L @ x`` will return a 1d NumPy array as the concatenation
    of the DWT coefficients in the form
    ``[cAn, cHn, cVn, cDn, ..., cH1, cV1, cD1]``
    where ``n`` is the decomposition level.

    - ``cAi`` are the approximation coefficients for level ``i``.
    - ``cHi`` are the horizontal coefficients for level ``i``.
    - ``cVi`` are the vertical coefficients for level ``i``.
    - ``cDi`` are the detail coefficients for level ``i``.
    ``cAi``, ``cHi``, ``cVi`` and ``cDi`` matrices have been flattened.

    Shape of ``L`` is $(P,~MN)$ where $P>=MN$.
    The value of $P$ depends on the ``mode``.
    In general, ``L`` is not orthogonal.

    Args:
        in_shape: ``tuple``
            Shape of the 2d input array $(M,~N)$.
        wavelet: ``str`` or tuple of ``(np.ndarray, np.ndarray)``, optional

            - If a ``str`` is provided, the wavelet name from
              `Pywavelets library <https://pywavelets.readthedocs.io/
              en/latest/regression/wavelet.html#
              wavelet-families-and-builtin-wavelets-names>`_
            - If a tuple ``(dec_lo, dec_hi)`` of two ``np.ndarray``
              is provided, the low and high-pass filters (for *decomposition*)
              used to define the wavelet.

              :octicon:`megaphone;1em;sd-text-danger` The ``dwt2d()``
              function does not test whether these two filters are
              actually Quadrature-Mirror-Filters.
        mode: ``str``, optional

            - ``'zero'``, signal is padded with zeros (default).
            - ``'periodic'``, signal is treated as periodic signal.
            - ``'symmetric'``, use mirroring to pad the signal.
            - ``'antisymmetric'``, signal is extended by mirroring and
              multiplying elements by minus one.
            - ``'reflect'``, signal is extended by reflecting elements.
            - ``'periodization'``, signal is extended like ``'periodic'``
              extension mode. Only the smallest possible number
              of coefficients is returned. Odd-length signal is extended
              first by replicating the last value.
        level: ``int``, optional
            If level is None compute full decomposition (default).
        backend: ``str``, optional
            ``'pywavelets'`` (default) or ``'lazylinop'`` for
            the underlying computation of the DWT.

    Returns:
        :class:`.LazyLinOp`

    Examples:
        >>> from lazylinop.signal2d import dwt2d, flatten
        >>> import numpy as np
        >>> import pywt
        >>> X = np.array([[1., 2.], [3., 4.]])
        >>> L = dwt2d(X.shape, wavelet='db1', level=1)
        >>> y = L @ flatten(X)
        >>> cA, (cH, cV, cD) = pywt.wavedec2(X, wavelet='db1', level=1)
        >>> z = np.concatenate([cA, cH, cV, cD], axis=1)
        >>> np.allclose(y, z)
        True

    .. seealso::
        - `Pywavelets module <https://pywavelets.readthedocs.io/en/
          latest/ref/2d-dwt-and-idwt.html#ref-dwt2>`_,
        - `Wavelets <https://pywavelets.readthedocs.io/en/latest/
          regression/wavelet.html>`_,
        - `Extension modes <https://pywavelets.readthedocs.io/en/
          latest/ref/signal-extension-modes.html>`_,
        - :func:`lazylinop.signal.dwt`,
        - :func:`lazylinop.signal.idwt`,
        - :func:`lazylinop.signal.idwt2d`.
    """
    if not isinstance(in_shape, tuple) or len(in_shape) != 2:
        raise Exception("in_shape expects tuple (M, N).")
    if isinstance(level, int) and level < 0:
        raise ValueError("Decomposition level must be >= 0.")
    if backend != 'pywavelets' and backend != 'lazylinop':
        raise ValueError("backend must be either" +
                         " 'pywavelets' or 'lazylinop'.")

    _, _, W, _ = _wavelet(wavelet)

    # Shape of the 2d array.
    M, N = in_shape[0], in_shape[1]

    # Number of decomposition levels.
    n_levels = min(_max_level(M, wavelet, level),
                   _max_level(N, wavelet, level))
    if n_levels == 0:
        # Nothing to decompose, return identity matrix.
        return eye(M * N)

    L = None
    for _ in range(n_levels):
        # Use dwt and kron lazy linear operators to write dwt2d.
        # Kronecker product trick: A @ X @ B^T = kron(A, B) @ vec(X).
        K = kron(
            dwt(M, wavelet=wavelet, mode=mode, level=1, backend=backend),
            dwt(N, wavelet=wavelet, mode=mode, level=1, backend=backend)
        )
        # Number of coefficients per dimension.
        M, N = _ncoeffs(M, W, mode), _ncoeffs(N, W, mode)
        # Use chunk operator to extract four sub-images
        # ---------------------
        # | LL (cA) | LH (cH) |
        # ---------------------
        # | HL (cV) | HH (cD) |
        # ---------------------
        # and fill the following list of coefficients
        # [cAn, cHn, cVn, cDn, ..., cH1, cV1, cD1].
        # Slices to extract sub-image LL.
        V = chunk(K.shape[0], N, 2 * N, start=0, stop=2 * N * M)
        # Slices to extract sub-image LH.
        V = vstack((V, chunk(K.shape[0], N, 2 * N,
                             start=2 * N * M, stop=4 * N * M)))
        # Slices to extract sub-image HL.
        V = vstack((V, chunk(K.shape[0], N, 2 * N,
                             start=N, stop=2 * N * M + N)))
        # Slices to extract sub-image HH.
        V = vstack((V, chunk(K.shape[0], N, 2 * N, start=2 * N * M + N)))
        if L is None:
            # First level of decomposition.
            L = V @ K
        else:
            # Apply low and high-pass filters + decimation only to LL.
            # Because of lazy linear operator V, LL always comes first.
            L = block_diag(*[V @ K,
                             eye(L.shape[0] - K.shape[1])]) @ L
    return L


def dwt2d_coeffs_shapes(in_shape: tuple, wavelet: str = 'haar',
                        level: int = None, mode: str = 'zero'):
    """
    Return a ``list`` of ``tuple`` that gives the shape
    of the flattened coefficients
    ``[cAn, cHn, cVn, cDn, ..., cH1, cV1, cD1]``.

    Args:
        in_shape, wavelet, level, mode:
            See :func:`dwt2d` for more details.

    Returns:
        ``list`` of ``tuple``.

    Examples:
        >>> from lazylinop.signal2d import dwt2d_coeffs_shapes
        >>> dwt2d_coeffs_shapes((5, 6), 'haar', level=2)
        [(2, 2), (2, 2), (2, 2), (2, 2), (3, 3), (3, 3), (3, 3)]
    """
    M, N = in_shape
    n_levels = min(_max_level(M, wavelet, level),
                   _max_level(N, wavelet, level))
    if n_levels == 0:
        return [in_shape]

    _, _, W, _ = _wavelet(wavelet)

    # First approximation coefficients.
    ll = [(_ncoeffs(M, W, mode), _ncoeffs(N, W, mode))] * 3
    for _ in range(1, n_levels):
        tmp = (_ncoeffs(ll[0][0], W, mode),
               _ncoeffs(ll[0][1], W, mode))
        for _ in range(3):
            ll.insert(0, tmp)
    # Last approximation coefficients.
    ll.insert(0, (ll[0][0], ll[0][1]))
    return ll


def dwt2d_to_pywt_coeffs(x, in_shape: tuple, wavelet: str = 'haar',
                         level: int = None, mode: str = 'zero'):
    r"""
    Returns Pywavelets compatible
    ``[cAn, (cHn, cVn, cDn), ..., (cH1, cV1, cD1)]``
    built from the 1d array ``x`` of flattened coefficients
    ``[cAn, cHn, cVn, cDn, ..., cH1, cV1, cD1]``
    where ``n`` is the decomposition level.

    Args:
        x: ``np.ndarray``
            List of coefficients
            ``[cAn, cHn, cVn, cDn, ..., cH1, cV1, cD1]``.
        in_shape, wavelet, level, mode:
            See :func:`dwt2d` for more details.

    Returns:
        Pywavelets compatible ``list``
        ``[cAn, (cHn, cVn, cDn), ..., (cH1, cV1, cD1)]``.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.signal2d import dwt2d, flatten, dwt2d_to_pywt_coeffs
        >>> import pywt
        >>> M, N = 5, 6
        >>> x = np.arange(M * N).reshape(M, N)
        >>> L = dwt2d((M, N), wavelet='haar', level=2, mode='zero')
        >>> y = L @ flatten(x)
        >>> y = dwt2d_to_pywt_coeffs(y, (M, N), 'haar', level=2, mode='zero')
        >>> z = pywt.wavedec2(x, wavelet='haar', level=2, mode='zero')
        >>> np.allclose(y[0], z[0])
        True
        >>> np.allclose(y[0][0], z[0][0])
        True
    """
    if not isinstance(in_shape, tuple) or len(in_shape) != 2:
        raise Exception("in_shape expects tuple (M, N).")
    if isinstance(level, int) and level < 0:
        raise ValueError("Decomposition level must be >= 0.")

    # Shape of the 2d array.
    M, N = in_shape[0], in_shape[1]

    # Number of decomposition levels.
    n_levels = min(_max_level(M, wavelet, level),
                   _max_level(N, wavelet, level))

    if n_levels == 0:
        # Nothing to convert, return identity matrix.
        return [x.reshape(M, N)]
    
    # Shape of coefficients per decomposition level.
    shapes = dwt2d_coeffs_shapes((M, N), wavelet, level, mode)

    cum, y, idx = 0, [], 0
    for i in range(n_levels):
        # Current shape of the coefficients.
        m, n = shapes[idx]
        mn = m * n
        if i == 0:
            # cA, (cH, cV, cD)
            y.append(x[:mn].reshape(m, n))
            y.append((x[mn:(2 * mn)].reshape(m, n),
                      x[(2 * mn):(3 * mn)].reshape(m, n),
                      x[(3 * mn):(4 * mn)].reshape(m, n)))
            cum += 4 * mn
            idx += 4
        else:
            # (cH, cV, cD)
            y.append((x[cum:(cum + mn)].reshape(m, n),
                      x[(cum + mn):(cum + 2 * mn)].reshape(m, n),
                      x[(cum + 2 * mn):(cum + 3 * mn)].reshape(m, n)))
            cum += 3 * mn
            idx += 3
    return y


def convert(N: int, dims: tuple):
    r"""
    From $vec(A),~vec(H),~vec(V),~vec(D)$ to

    .. math::

        \begin{equation}
        vec\begin{pmatrix}
        A & H\\
        V & D
        \end{pmatrix}
        \end{equation}

    Args:
        N: ``int``
            Size of $vec(A),~vec(H),~vec(V),~vec(D)$.
        dims: ``tuple``
            Shape of ``A``, ``H``, ``V`` and ``D``.

    Returns:
        ``np.ndarray``.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.signal2d.dwt2d import convert
        >>> x = np.full(6, 1.0)
        >>> x = np.append(x, np.full(6, 2.0))
        >>> x = np.append(x, np.full(6, 3.0))
        >>> x = np.append(x, np.full(6, 4.0))
        >>> C = convert(x.shape[0], dims=(2, 3))
        >>> y = C @ x
        >>> y.reshape(4, 6)
        array([[1., 1., 1., 3., 3., 3.],
               [1., 1., 1., 3., 3., 3.],
               [2., 2., 2., 4., 4., 4.],
               [2., 2., 2., 4., 4., 4.]])
        >>> C = convert(x.shape[0], dims=(3, 2))
        >>> y = C @ x
        >>> y.reshape(6, 4)
        array([[1., 1., 3., 3.],
               [1., 1., 3., 3.],
               [1., 1., 3., 3.],
               [2., 2., 4., 4.],
               [2., 2., 4., 4.],
               [2., 2., 4., 4.]])
    """

    def _matmat(x):
        m, n = dims
        y = np.empty_like(x)
        idx = np.arange(m * n)
        row = idx // n
        col = idx - row * n
        y[row * 2 * n + col, :] = x[:(m * n), :]
        # y[row * 2 * n + col + n, :] = x[(m * n):(2 * m * n), :]
        # y[(row + m) * 2 * n + col, :] = x[(2 * m * n):(3 * m * n), :]
        y[row * 2 * n + col + n, :] = x[(2 * m * n):(3 * m * n), :]
        y[(row + m) * 2 * n + col, :] = x[(m * n):(2 * m * n), :]
        y[(row + m) * 2 * n + col + n, :] = x[(3 * m * n):(4 * m * n), :]
        return y

    def _rmatmat(x):
        m, n = dims
        y = np.empty_like(x)
        idx = np.arange(m * n)
        row = idx // n
        col = idx - row * n
        y[:(m * n), :] = x[row * 2 * n + col, :]
        y[(2 * m * n):(3 * m * n), :] = x[row * 2 * n + col + n, :]
        y[(m * n):(2 * m * n), :] = x[(row + m) * 2 * n + col, :]
        y[(3 * m * n):(4 * m * n), :] = x[(row + m) * 2 * n + col + n, :]
        return y

    return LazyLinOp(
        shape=(N, N),
        matmat=lambda x: _matmat(x),
        rmatmat=lambda x: _rmatmat(x)
    )


# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
