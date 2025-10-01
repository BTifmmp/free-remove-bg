from PIL import Image
from skimage import io
import torch
import torch.nn.functional as F
from transformers import AutoConfig, AutoModelForImageSegmentation
from torchvision.transforms.functional import normalize
from torchvision import transforms
import numpy as np


class InferenceManager:
    AVAILABLE_MODELS = ["rmbg14", "rmbg20"]
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # avoid re-init
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model_name = None
            self.model = None
            self._initialized = True

    def load_model(self, model_name: str):
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} is not available. Choose from {self.AVAILABLE_MODELS}")

        self.model_name = model_name
        self.model = AutoModelForImageSegmentation.from_pretrained(
            pretrained_model_name_or_path=f'models/{model_name}',
            trust_remote_code=True
        )
        if model_name == "rmbg14":
            self.model.to(self.device)
        if model_name == "rmbg20":
            self.model.eval().to(self.device)

    def switch_model(self, model_name: str):
        self.load_model(model_name)

    def remove_background(self, image_path: str) -> Image.Image:
        if self.model_name == "rmbg14":
            return self._remove_bg14(image_path)
        elif self.model_name == "rmbg20":
            return self._remove_bg20(image_path)
        else:
            raise ValueError(f"Unknown model name: {self.model_name}")

    def _remove_bg14(self, image_path: str) -> Image.Image:
        # prepare input
        orig_im = Image.open(image_path).convert("RGB")
        orig_im_size = orig_im.size[::-1]  # (height, width)
        model_input_size = [1024, 1024]
        image = self._preprocess(orig_im, model_input_size).to(self.device)

        # inference
        result = self.model(image)

        # post process
        result_image = self._postprocess(result[0][0], orig_im_size)

        # save result
        pil_mask_im = Image.fromarray(result_image)
        orig_image = Image.open(image_path)
        no_bg_image = orig_image.copy()
        no_bg_image.putalpha(pil_mask_im)

        return no_bg_image

    def _remove_bg20(self, image_path: str) -> Image.Image:
        orig_im = Image.open(image_path).convert("RGB")
        model_input_size = [1024, 1024]
        transform_image = transforms.Compose([
            transforms.Resize(model_input_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        input_images = transform_image(orig_im).unsqueeze(0).to(self.device)

        with torch.no_grad():
            preds = self.model(input_images)[-1].sigmoid().cpu()
        pred = preds[0].squeeze()
        pred_pil = transforms.ToPILImage()(pred)
        mask = pred_pil.resize(orig_im.size)
        orig_im.putalpha(mask)

        return orig_im

    def _preprocess(self, image: Image.Image, model_input_size: list) -> torch.Tensor:
        im = np.array(image)
        if len(im.shape) < 3:
            im = im[:, :, np.newaxis]
        # orig_im_size=im.shape[0:2]
        im_tensor = torch.tensor(im, dtype=torch.float32).permute(2,0,1)
        im_tensor = F.interpolate(torch.unsqueeze(im_tensor,0), size=model_input_size, mode='bilinear')
        image = torch.divide(im_tensor,255.0)
        image = normalize(image,[0.5,0.5,0.5],[1.0,1.0,1.0])
        return image

    def _postprocess(self, result: torch.Tensor, im_size: list) -> np.ndarray:
        result = torch.squeeze(F.interpolate(result, size=im_size, mode='bilinear'), 0)
        ma = torch.max(result)
        mi = torch.min(result)
        result = (result-mi)/(ma-mi)
        im_array = (result*255).permute(1,2,0).cpu().data.numpy().astype(np.uint8)
        im_array = np.squeeze(im_array)
        return im_array