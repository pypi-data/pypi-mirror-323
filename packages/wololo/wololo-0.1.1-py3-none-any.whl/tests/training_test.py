import torch
from torch import nn

from ..wololo import Converter
from .toy_functions.plot_utilities import *
from .toy_functions.toy_functions import *

input_shape = 1
output_shape = 1
hidden_shape = 16
hidden_shape_2 = 32
hidden_shape_3 = 64
batch_size = 64
total_data = 32
n_particles = 50
epochs = 1
learning_rate = 0.02


class StochParam(torch.nn.Module):
    def __init__(self, parameter):
        super().__init__()
        self.mu = torch.nn.Parameter(parameter)
        self.shape = self.mu.shape
        self.std = torch.nn.Parameter(torch.full_like(self.mu, 0.01))

    def forward(self, n_samples):
        epsilon = torch.randn(n_samples, *self.shape, device=self.mu.device)
        return self.mu + epsilon * self.std


class GaussianParam(torch.nn.Module):
    def __init__(self, parameter):
        super().__init__()
        self.mu = torch.nn.Parameter(parameter)
        self.std = torch.nn.Parameter(torch.full_like(self.mu, 0.01))

    def forward(self, n_samples):
        dist = torch.distributions.Normal(self.mu, self.std)
        return dist.rsample((n_samples,))  # Reparameterized sampling


class UniformParam(torch.nn.Module):
    def __init__(self, parameter):
        super().__init__()
        self.low = torch.nn.Parameter(torch.zeros_like(parameter))
        self.high = torch.nn.Parameter(torch.ones_like(parameter))

    def forward(self, n_samples):
        dist = torch.distributions.Uniform(self.low, self.high)
        return dist.rsample((n_samples,))


class BetaParam(torch.nn.Module):
    def __init__(self, parameter):
        super().__init__()
        self.alpha = torch.nn.Parameter(torch.full_like(parameter, 2.0))
        self.beta = torch.nn.Parameter(torch.full_like(parameter, 2.0))

    def forward(self, n_samples):
        dist = torch.distributions.Beta(self.alpha, self.beta)
        return dist.rsample((n_samples,))


class ParticleParam(torch.nn.Module):
    def __init__(self, parameter):
        self.parameters


dataloader, x_truth, y_truth = create_data_and_ground_truth(
    func=nonlinear_sinusoidal,
    input_shape=input_shape,
    batch_size=batch_size,
    total_data=total_data,
    ground_truth_range=(-3.1, 3.1),
)


class SimpleModule(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(input_shape, hidden_shape)
        self.middle = nn.Linear(hidden_shape, hidden_shape_2)
        self.middle2 = nn.Linear(hidden_shape_2, hidden_shape_3)
        self.last = nn.Linear(hidden_shape_3, output_shape)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.linear(x)
        x = self.relu(x)
        x = self.middle(x)
        x = self.relu(x)
        x = self.middle2(x)
        x = self.relu(x)
        x = self.last(x)
        return x


model = SimpleModule()
stoch_model = Converter().convert(model, BetaParam)


# model, pred_history, kernel_history, total_history = SVGD(
#     starting_model=SimpleModule(),
#     n_samples=n_particles,
#     epochs=epochs,
#     dataloader=dataloader,
#     loss_fn=torch.nn.MSELoss(),
#     optimizer_fn=torch.optim.Adam,
#     learning_rate=learning_rate,
# )

# plot_with_uncertainty_from_dataloader(dataloader, x_truth, y_truth, model, n_particles)

# model, pred_history, kernel_history, total_history = BBVI(
#     starting_model=SimpleModule(),
#     n_samples=n_particles,
#     epochs=epochs,
#     dataloader=dataloader,
#     loss_fn=torch.nn.MSELoss(),
#     optimizer_fn=torch.optim.Adam,
#     learning_rate=learning_rate,
# )

# plot_with_uncertainty_from_dataloader(dataloader, x_truth, y_truth, model, n_particles)
