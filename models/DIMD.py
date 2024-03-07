import torch.nn as nn 
import torch

from networks.resnet50nodown import resnet50nodown


class DIMD(nn.Module):

    def __init__(self):
        super(DIMD, self).__init__()
        self.model = resnet50nodown(num_classes=1)

    def forward(self, x):
        return self.model(x)

    def load_weights(self, ckpt):
        state_dict = torch.load(ckpt, map_location='cpu')
        try:
            self.model.load_state_dict(state_dict['model'])
        except:
            self.model.load_state_dict(state_dict)

    def predict(self, img):
        with torch.no_grad():
            logits = self.forward(img)
            return logits.sigmoid().flatten().tolist()