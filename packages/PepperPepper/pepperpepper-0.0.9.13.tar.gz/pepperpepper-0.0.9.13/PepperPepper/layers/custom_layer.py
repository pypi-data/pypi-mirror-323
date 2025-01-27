from PepperPepper.environment import torch, nn, F, rearrange, math

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride = 1):
        super(ResidualBlock, self).__init__()
        self.body = nn.Sequential(
            nn.Conv2d(in_channels, out_channels,  kernel_size=3, stride=stride, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride, padding=1),
            nn.BatchNorm2d(out_channels),
        )
        if stride != 1 or out_channels != in_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm2d(out_channels),
            )
        else:
            self.shortcut = None

        self.relu = nn.LeakyReLU(inplace=True)

    def forward(self, x):
        residual = x
        x = self.body(x)

        if self.shortcut is not None:
            residual = self.shortcut(residual)
        out = self.relu(x+residual)
        return out



class _FCNHead(torch.nn.Module):
    def __init__(self, in_channels, channels, norm_layer=torch.nn.BatchNorm2d):
        super(_FCNHead, self).__init__()
        self.block = torch.nn.Sequential()
        inter_channels = in_channels // 4
        self.block.append(torch.nn.Conv2d(in_channels=in_channels, out_channels=inter_channels, kernel_size=3, padding=1, bias=False))
        self.block.append(norm_layer(inter_channels))
        self.block.append(torch.nn.LeakyReLU(negative_slope=0.2))
        self.block.append(torch.nn.Dropout(0.1))
        self.block.append(torch.nn.Conv2d(in_channels=inter_channels, out_channels=channels, kernel_size=1))

    def forward(self, x):
        return self.block(x)



class Patch_embed(nn.Module):
    def __init__(self, in_channels, out_channels, patch_size, V='V1'):
        super().__init__()
        self.in_channels = in_channels
        self.patch_size = patch_size
        self.V = V
        self.out_channels = out_channels

        if self.V == 'V1' and self.is_power_of_two(patch_size):
            self.block = self._make_patch_embed_V1(in_channels, out_channels, patch_size)
        else:
            self.block = self._make_patch_embed_last(in_channels, out_channels, patch_size)
            # raise ValueError(f"Unsupported version: {self.V}")



    def forward(self, x):
        y = self.block(x)
        return y

    def is_power_of_two(self, n):
        if n <= 1:
            return False
        log2_n = math.log2(n)
        return log2_n.is_integer()

    def check_divisible_by_power_of_two(self, n, k):
        divisor = 2 ** k

        if n % divisor != 0:
            raise ValueError(f"Error: {n} is not divisible by 2^{k}. Please try again.")

        return


    def _make_patch_embed_V1(self, in_channels, out_channels, patch_size):
        stage_num = int(math.log2(patch_size))

        # self.check_divisible_by_power_of_two(out_channels, stage_num)
        dim = out_channels // stage_num



        block = []
        for d in range(stage_num):
            block.append(nn.Sequential(
                nn.Conv2d(in_channels * (d + 1) if d == 0 else dim * (d), dim * (d + 1) if d+1 != stage_num else out_channels, kernel_size=2, stride=2),
                Permute(0, 2, 3, 1),
                nn.LayerNorm(dim * (d + 1) if d+1 != stage_num else out_channels),
                Permute(0, 3, 1, 2),
                (nn.GELU() if d+1 != stage_num else nn.Identity() )
            ))

        return nn.Sequential(*block)


    def _make_patch_embed_last(self, in_channels, channels, patch_size):
        # block = []

        block = nn.Sequential(
            nn.Conv2d(in_channels, channels // 2, kernel_size=patch_size,stride=patch_size),
            Permute(0, 2, 3, 1),
            nn.LayerNorm(channels // 2),
            Permute(0, 3, 1, 2),
            nn.GELU(),
            nn.Conv2d(channels//2, channels, kernel_size=1, stride=1),
            Permute(0, 2, 3, 1),
            nn.LayerNorm(channels // 2),
            Permute(0, 3, 1, 2)
        )


        return block






class Permute(nn.Module):
    def __init__(self, *args):
        super().__init__()
        self.args = args

    def forward(self, x: torch.Tensor):
        return x.permute(*self.args)


class PatchExpand2D(nn.Module):
    def __init__(self, in_channels, out_channels, patch_size):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.patch_size = patch_size
        self.expand = nn.Linear(in_channels, patch_size*patch_size*self.out_channels, bias=False)
        self.norm = nn.LayerNorm(out_channels)

    def forward(self, x):#(b,h,w,c)->(b,h,w,2c)->(b,2h,2w,c/2)
        x=x.permute(0,2,3,1)
        B, H, W, C = x.shape
        x = self.expand(x)

        x = rearrange(x, 'b h w (p1 p2 c)-> b (h p1) (w p2) c', p1=self.patch_size, p2=self.patch_size, c=self.out_channels)
        x= self.norm(x).permute(0,3,1,2)

        return x




class FFT_PriorFilter(nn.Module):
    def __init__(self, in_channels , windows_size):
        super().__init__()
        self.dim = in_channels
        self.windows_size = windows_size
        self.cond = nn.Parameter(torch.randn(self.windows_size, self.windows_size // 2 + 1, self.dim, 2, dtype=(torch.float32)) * 0.02)


    def forward(self, x):
        B, C, H, W = x.size()
        assert H % self.windows_size == 0 and W % self.windows_size == 0, 'windows_size must be divisible by windows_size'
        x = rearrange(x, 'b c (h p1) (w p2) -> (b h w) p1 p2 c', p1=self.windows_size, p2=self.windows_size)

        X = torch.fft.rfft2(x, dim=(1, 2), norm='ortho')
        cond = torch.view_as_complex(self.cond)

        X = X * cond

        x = torch.fft.irfft2(X, s=(self.windows_size, self.windows_size), dim=(1, 2), norm='ortho')
        x = rearrange(x, '(b h w) p1 p2 c -> b c (h p1) (w p2)', h=H // self.windows_size, w=W // self.windows_size)

        return x

# in_channels, out_channels, patch_size


# def __init__(self, in_channels, out_channels, patch_size, V='V1'):
# class FFT_Filter_Mamba(nn.Module):
#     def __init__(self, in_dim , hiden_dim, img_size, windows_size, num_layers=2):
#         super().__init__()
#         self.num_layers = num_layers
#         self.fftfilter = FFT_PriorFilter(in_dim, img_size)
#         self.PE = Patch_embed(in_dim, hiden_dim, patch_size=windows_size)
#
#         self.PD = PatchExpand2D(hiden_dim, in_dim, patch_size=windows_size)
#
#
#     def forward(self, x):
#         x = self.fftfilter(x)
#
#         patch = self.PE(x)
#
#         out = self.PD(patch)
#
#         return out












