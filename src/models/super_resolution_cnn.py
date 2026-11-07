import torch
import torch.nn as nn


class ResidualBlock(nn.Module):
    """Basic residual block for feature refinement."""

    def __init__(self, channels: int):
        super().__init__()

        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
        )

    def forward(self, x):
        return x + self.block(x)


class SuperResolutionCNN(nn.Module):
    """
    4-band 2× multispectral super-resolution CNN.

    Input:
        (batch, 4, 128, 128)

    Output:
        (batch, 4, 256, 256)
    """

    def __init__(
        self,
        in_channels: int = 4,
        out_channels: int = 4,
        features: int = 64,
        num_residual_blocks: int = 4,
    ):
        super().__init__()

        self.head = nn.Conv2d(
            in_channels,
            features,
            kernel_size=3,
            padding=1,
        )

        self.residual_blocks = nn.Sequential(
            *[
                ResidualBlock(features)
                for _ in range(num_residual_blocks)
            ]
        )

        self.body = nn.Conv2d(
            features,
            features,
            kernel_size=3,
            padding=1,
        )

        self.upsample = nn.Sequential(
            nn.Conv2d(
                features,
                features * 4,
                kernel_size=3,
                padding=1,
            ),
            nn.PixelShuffle(upscale_factor=2),
            nn.ReLU(inplace=True),
        )

        self.tail = nn.Conv2d(
            features,
            out_channels,
            kernel_size=3,
            padding=1,
        )

    def forward(self, x):
        x = self.head(x)

        residual = x

        x = self.residual_blocks(x)
        x = self.body(x)
        x = x + residual

        x = self.upsample(x)
        x = self.tail(x)

        return x


if __name__ == "__main__":
    model = SuperResolutionCNN()

    x = torch.randn(1, 4, 128, 128)
    y = model(x)

    print("Input shape :", tuple(x.shape))
    print("Output shape:", tuple(y.shape))