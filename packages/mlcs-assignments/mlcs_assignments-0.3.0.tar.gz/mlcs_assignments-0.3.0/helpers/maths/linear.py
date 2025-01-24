from typing import Protocol
from helpers.maths.types import Matrix, Vector
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import cg, spilu, LinearOperator

import numpy as np


class PreconditionerProvider(Protocol):
    def __call__(self, A: Matrix) -> LinearOperator:
        """Provides a preconditioner for the matrix A."""
        ...


def incomplete_cholesky_preconditioner(A: Matrix) -> LinearOperator:
    """Compute the Incomplete Cholesky preconditioner for matrix A."""
    A_csc = csc_matrix(A)
    ilu = spilu(A_csc, drop_tol=1e-5)

    M = LinearOperator(A.shape, ilu.solve)
    return M


# TODO: Untested!
# The following is not yet tested:
# - Whether max_iterations is respected
# - Whether different preconditioners work
def solve(
    A: Matrix,
    B: Vector | Matrix,
    /,
    *,
    tolerance: float = 1e-10,
    max_iterations: int | None = None,
    preconditioner: PreconditionerProvider = incomplete_cholesky_preconditioner,
    warnings: bool = False,
) -> Vector | Matrix:
    """Solves AX = B for X using the Conjugate Gradient method, where A is symmetric positive definite.

    Args:
        A: The matrix A in the equation $AX = B$.
        B: The right-hand side vector or matrix in the equation $AX = B$.
        tolerance: The relative tolerance for the Conjugate Gradient method.
        max_iterations: The maximum number of iterations for the Conjugate Gradient method.
        preconditioner: The preconditioner to use for the Conjugate Gradient method. By default, the Incomplete Cholesky
            preconditioner is used.
        warnings: Whether to show warnings when the Conjugate Gradient method does not converge.

    Returns:
        The solution X to the equation $AX = B$.

    Example:
        If the right-hand side is just a single vector $b$, you can solve the equation like this:

        ```python
        A = np.array([[4, 1], [1, 3]])
        b = np.array([1, 2])

        x = solve(A, b)
        # Output: array([0.09090909, 0.63636364])
        ```

        You can also solve for multiple right-hand side vectors by passing a matrix as the right-hand side:

        ```python
        A = np.array([[4, 1], [1, 3]])
        B = np.array([[1, 2], [3, 4]])

        X = solve(A, B)
        # Output: array([[0.        , 0.18181818],
                         [1.        , 1.27272727]])
        ```

    Note:
        For small matrices, this will automatically fall back to the `np.linalg.solve` method, since that
        is much cheaper in such cases.
    """
    if not isinstance(B, np.ndarray):
        B = np.array(B)

    if A.shape[0] == 1:
        return np.array([(B / A).squeeze()])

    if B.ndim == 1:
        B = B.reshape(-1, 1)

    if A.shape[0] <= 100:
        return np.linalg.solve(A, B).squeeze()

    N, nrhs = B.shape
    solutions: list[Vector] = []

    max_iterations = max_iterations or N
    M = preconditioner(A)

    for i in range(nrhs):
        x, info = cg(A, B[:, i], M=M, rtol=tolerance, maxiter=max_iterations)

        if info > 0 and warnings:
            print(f"Warning: CG did not converge for column {i}. Error code: {info}")

        solutions.append(x)

    # We need to transpose here, because the solution vectors are stored as rows.
    # They are expected to be columns in the result (if RHS is a matrix).
    return np.array(solutions).squeeze().T
