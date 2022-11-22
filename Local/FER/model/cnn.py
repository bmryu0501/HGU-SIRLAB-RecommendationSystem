import torch
import torch.nn as nn

class CNN(nn.Module):
    def __init__(self, num_classes=7):
        super().__init__()
        self.feature = nn.Sequential(
            nn.Conv2d(3, 6, kernel_size=37, padding=1),
            #nn.BatchNorm2d(6),
            nn.ReLU(),
            nn.Conv2d(6, 12, kernel_size=37, padding=1),
            #nn.BatchNorm2d(12),
            nn.ReLU(),
            nn.Dropout(0.50),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(12, 24, kernel_size=37, padding=1),
            #nn.BatchNorm2d(24),
            nn.ReLU(),
            nn.Conv2d(24, 24, kernel_size=37, padding=1),
            #nn.BatchNorm2d(24),
            nn.ReLU(),
            nn.Dropout(0.75),
            nn.MaxPool2d(2, 2),
        )
        
        self.fc_layer = nn.Sequential(
            nn.Linear(24*5*5, 120),
            nn.ReLU(),
            nn.Linear(120, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes),
        )
        
    def forward(self, x):
        x = self.feature(x)
        #print("After convolution layers:", x.shape)
        x = torch.flatten(x, 1) # 배치를 제외한 모든 차원을 평탄화
        #print("After flatten:", x.shape)
        x = self.fc_layer(x)
        return x