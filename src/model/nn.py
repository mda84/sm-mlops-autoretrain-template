from __future__ import annotations

import torch
from torch import nn


class SimpleMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64, output_dim: int = 1, problem_type: str = "classification"):
        super().__init__()
        self.problem_type = problem_type
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.model(x)
