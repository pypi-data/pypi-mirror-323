import einops
import torch
import torch.nn.functional as Fn

from .nystrom_utils import (
    EigSolverOptions,
    OnlineKernel,
    OnlineNystromSubsampleFit,
    solve_eig,
)
from ..distance_utils import (
    DistanceOptions,
    affinity_from_features,
)
from ..sampling_utils import (
    SampleConfig,
)


class LaplacianKernel(OnlineKernel):
    def __init__(
        self,
        affinity_focal_gamma: float,
        distance: DistanceOptions,
        adaptive_scaling: bool,
        eig_solver: EigSolverOptions,
    ):
        self.affinity_focal_gamma = affinity_focal_gamma
        self.distance: DistanceOptions = distance
        self.adaptive_scaling: bool = adaptive_scaling
        self.eig_solver: EigSolverOptions = eig_solver

        # Anchor matrices
        self.anchor_features: torch.Tensor = None               # [n x d]
        self.A: torch.Tensor = None                             # [n x n]
        self.Ainv: torch.Tensor = None                          # [n x n]

        # Updated matrices
        self.a_r: torch.Tensor = None                           # [n]
        self.b_r: torch.Tensor = None                           # [n]

    def fit(self, features: torch.Tensor) -> None:
        self.anchor_features = features                         # [n x d]
        self.A = affinity_from_features(
            self.anchor_features,                               # [n x d]
            affinity_focal_gamma=self.affinity_focal_gamma,
            distance=self.distance,
        )                                                       # [n x n]
        d = features.shape[-1]
        U, L = solve_eig(
            self.A,
            num_eig=d + 1,  # d * (d + 3) // 2 + 1,
            eig_solver=self.eig_solver,
        )                                                       # [n x (d + 1)], [d + 1]
        self.Ainv = U @ torch.diag(1 / L) @ U.mT                # [n x n]
        self.a_r = torch.sum(self.A, dim=-1)                    # [n]
        self.b_r = torch.zeros_like(self.a_r)                   # [n]

    def _affinity(self, features: torch.Tensor) -> torch.Tensor:
        B = affinity_from_features(
            self.anchor_features,                               # [n x d]
            features,                                           # [m x d]
            affinity_focal_gamma=self.affinity_focal_gamma,
            distance=self.distance,
        )                                                       # [n x m]
        if self.adaptive_scaling:
            diagonal = (
                einops.rearrange(B, "n m -> m 1 n")             # [m x 1 x n]
                @ self.Ainv                                     # [n x n]
                @ einops.rearrange(B, "n m -> m n 1")           # [m x n x 1]
            ).squeeze(1, 2)                                     # [m]
            adaptive_scale = diagonal ** -0.5                   # [m]
            B = B * adaptive_scale
        return B                                                # [n x m]

    def update(self, features: torch.Tensor) -> torch.Tensor:
        B = self._affinity(features)                            # [n x m]
        b_r = torch.sum(B, dim=-1)                              # [n]
        b_c = torch.sum(B, dim=-2)                              # [m]
        self.b_r = self.b_r + b_r                               # [n]

        row_sum = self.a_r + self.b_r                           # [n]
        col_sum = b_c + B.mT @ self.Ainv @ self.b_r             # [m]
        scale = (row_sum[:, None] * col_sum) ** -0.5            # [n x m]
        return (B * scale).mT                                   # [m x n]

    def transform(self, features: torch.Tensor = None) -> torch.Tensor:
        row_sum = self.a_r + self.b_r                           # [n]
        if features is None:
            B = self.A                                          # [n x n]
            col_sum = row_sum                                   # [n]
        else:
            B = self._affinity(features)
            b_c = torch.sum(B, dim=-2)                          # [m]
            col_sum = b_c + B.mT @ self.Ainv @ self.b_r         # [m]
        scale = (row_sum[:, None] * col_sum) ** -0.5            # [n x m]
        return (B * scale).mT                                   # [m x n]


class NCut(OnlineNystromSubsampleFit):
    """Nystrom Normalized Cut for large scale graph."""

    def __init__(
        self,
        n_components: int = 100,
        affinity_focal_gamma: float = 1.0,
        distance: DistanceOptions = "cosine",
        adaptive_scaling: bool = True,
        sample_config: SampleConfig = SampleConfig(),
        eig_solver: EigSolverOptions = "svd_lowrank",
        chunk_size: int = 8192,
    ):
        """
        Args:
            n_components (int): number of top eigenvectors to return
            affinity_focal_gamma (float): affinity matrix temperature, lower t reduce the not-so-connected edge weights,
                smaller t result in more sharp eigenvectors.
            distance (str): distance metric for affinity matrix, ['cosine', 'euclidean', 'rbf'].
            adaptive_scaling (bool): whether to scale off-diagonal affinity vectors so extended diagonal equals 1
            sample_config (str): subgraph sampling, ['farthest', 'random'].
                farthest point sampling is recommended for better Nystrom-approximation accuracy
            eig_solver (str): eigen decompose solver, ['svd_lowrank', 'lobpcg', 'svd', 'eigh'].
            chunk_size (int): chunk size for large-scale matrix multiplication
        """
        OnlineNystromSubsampleFit.__init__(
            self,
            n_components=n_components,
            kernel=LaplacianKernel(affinity_focal_gamma, distance, adaptive_scaling, eig_solver),
            distance=distance,
            sample_config=sample_config,
            eig_solver=eig_solver,
            chunk_size=chunk_size,
        )


def axis_align(eigen_vectors: torch.Tensor, max_iter=300):
    """Multiclass Spectral Clustering, SX Yu, J Shi, 2003

    Args:
        eigen_vectors (torch.Tensor): continuous eigenvectors from NCUT, shape (n, k)
        max_iter (int, optional): Maximum number of iterations.

    Returns:
        torch.Tensor: Discretized eigenvectors, shape (n, k), each row is a one-hot vector.
    """
    # Normalize eigenvectors
    n, k = eigen_vectors.shape
    eigen_vectors = Fn.normalize(eigen_vectors, p=2, dim=-1)

    # Initialize R matrix with the first column from a random row of EigenVectors
    R = torch.empty((k, k), device=eigen_vectors.device)
    R[0] = eigen_vectors[torch.randint(0, n, (1,))].squeeze()

    # Loop to populate R with k orthogonal directions
    c = torch.zeros(n, device=eigen_vectors.device)
    for i in range(1, k):
        c += torch.abs(eigen_vectors @ R[i - 1])
        R[i] = eigen_vectors[torch.argmin(c, dim=0)]

    # Iterative optimization loop
    eps = torch.finfo(torch.float32).eps
    prev_objective = torch.inf
    for _ in range(max_iter):
        # Discretize the projected eigenvectors
        idx = torch.argmax(eigen_vectors @ R.mT, dim=-1)
        M = torch.zeros((k, k)).index_add_(0, idx, eigen_vectors)

        # Compute the NCut value
        objective = torch.norm(M)

        # Check for convergence
        if torch.abs(objective - prev_objective) < eps:
            break
        prev_objective = objective

        # SVD decomposition
        U, S, Vh = torch.linalg.svd(M, full_matrices=False)
        R = U @ Vh

    return Fn.one_hot(idx, num_classes=k).to(torch.float), R
