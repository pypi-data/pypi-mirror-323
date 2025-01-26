def flatten(X):
    """
    Returns a flatten version of X along its first two dimensions.

    This utility function is provided to flatten an image or a batch of
    images to be used as input of LazyLinOp signal2d's functions.

    Args:
        X: ``array`` with 2 dimensions for a single image or 3 dimensions for a batch of images

    Returns:
        Flattened version of X

    Examples:
        >>> import numpy as np
        >>> from lazylinop.signal2d import flatten
        >>> X = np.arange(90).reshape(3, 3, 10)
        >>> X.shape
        (3, 3, 10)
        >>> flatten(X).shape
        (9, 10)

    .. seealso::
        :func:`.lazylinop.signal2d.unflatten`
    """
    return X.reshape(-1, *(X.shape[2:]))


def unflatten(X, shape):
    """
    Returns a un-flatten version of X, where its first dimension is expanded
    on two dimensions with shape `shape`.

    This utility function is provided to un-flatten an image or a batch of
    images as returned by LazyLinOp signal2d's functions, to be manipulated
    as usual 2D images.

    Args:
        X: ``array`` with 1 dimension for a single image or 2 dimensions for a batch of images
        shape: the 2D dimensions of image

    Returns:
        Un-flattened version of X

    Examples:
        >>> import numpy as np
        >>> from lazylinop.signal2d import unflatten
        >>> X = np.arange(90).reshape(9, 10)
        >>> X.shape
        (9, 10)
        >>> unflatten(X, (3, 3)).shape
        (3, 3, 10)

    .. seealso::
        :func:`.lazylinop.signal2d.unflatten`
    """
    return X.reshape(shape + X.shape[1:])


