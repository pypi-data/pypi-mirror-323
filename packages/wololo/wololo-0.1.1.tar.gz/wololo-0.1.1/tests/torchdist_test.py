import torch
from torch import nn
from tqdm import tqdm

from wololo.algorithms.bbvi import BBVI
from wololo.algorithms.svgd import SVGD
from wololo.converters import Adapter, GaussianAdapter, GaussianConverter

from .toy_functions.plot_utilities import *
from .toy_functions.toy_functions import *


class RandomBetaParameter(torch.nn.Module):
    """
    Represents a random parameter sampled from a Beta distribution.
    """

    def __init__(self, alpha: torch.Tensor, beta: torch.Tensor):
        super().__init__()
        self.raw_alpha = torch.nn.Parameter(alpha)  # Transformed via softplus
        self.raw_beta = torch.nn.Parameter(beta)  # Transformed via softplus

    def forward(self, n_samples) -> torch.Tensor:
        """
        Samples from the Beta distribution defined by softplus(alpha) and softplus(beta).
        """
        alpha = torch.nn.functional.softplus(self.raw_alpha)
        beta = torch.nn.functional.softplus(self.raw_beta)
        dist = torch.distributions.Beta(alpha, beta)
        if n_samples is None:
            return dist.rsample()
        return dist.rsample((n_samples,))


class BetaAdapter(GaussianAdapter):
    def adapt_parameter(self, parameter: torch.nn.Parameter):
        return RandomBetaParameter(alpha=torch.tensor(2.0), beta=torch.tensor(2.0))


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


def BBVI_step(model, n_samples, x, y, loss_fn, optimizer):
    optimizer.zero_grad()
    output = model(x, n_samples)
    pred_loss = torch.vmap(loss_fn, in_dims=(0, None))(output, y).mean()
    total_loss = pred_loss
    total_loss.backward()
    optimizer.step()
    return pred_loss, total_loss


fake_input = torch.randn(batch_size, input_shape)
optimizer_fn = torch.optim.AdamW
det_model = SimpleModule()
model = GaussianConverter(adapter=BetaAdapter).convert(det_model)

prova = RandomBetaParameter(alpha=torch.tensor(2.1), beta=torch.tensor(1.9))

print(prova(10).shape)
print(torch.randn(10).shape)

print(model.graph)
print(model(fake_input, 10))

# optimizer = optimizer_fn(model.parameters(), lr=learning_rate)
# n_samples = 100
# loss_fn = torch.nn.MSELoss()

# pred_history = []
# kl_history = []
# total_history = []

# for epoch in range(epochs):
#     with tqdm(total=len(dataloader), desc=f"Epoch {epoch + 1}/{epochs}") as pbar:
#         for x_batch, y_batch in dataloader:
#             pred_loss, kl_loss, total_loss = BBVI_step(
#                 model,
#                 n_samples,
#                 x_batch,
#                 y_batch,
#                 loss_fn,
#                 optimizer,
#             )

#             pred_history.append(pred_loss.detach().cpu().numpy())
#             kl_history.append(kl_loss.detach().cpu().numpy())
#             total_history.append(total_loss.detach().cpu().numpy())

#             pbar.set_postfix(
#                 tot_loss=total_loss.item(),
#                 pred=pred_loss.item(),
#                 kernel=kl_loss.item(),
#             )
#             pbar.update(1)


# plot_with_uncertainty_from_dataloader(dataloader, x_truth, y_truth, model, n_particles)
