import torch
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Union


def normalize_input(
    img: Union[np.ndarray, torch.Tensor], normalization: str = "base"
) -> Union[np.ndarray, torch.Tensor]:
    """
    Normalize input image.

    Args:
        img (Union[np.ndarray, torch.Tensor]): The input image.
        normalization (str, optional): The normalization technique. Defaults to "base".

    Returns:
        Union[np.ndarray, torch.Tensor]: The normalized image.
    """
    if isinstance(img, np.ndarray):
        img = torch.from_numpy(img).float()

    if normalization == "base":
        return img

    if normalization == "raw":
        img *= 255.0
    elif normalization == "Facenet":
        mean = img.mean()
        std = img.std()
        img = (img - mean) / std
    elif normalization == "Facenet2018":
        img = img * 2 - 1  # Equivalent to: img / 127.5 - 1
    elif normalization == "VGGFace":
        img *= 255.0
        img[0] -= 93.5940
        img[1] -= 104.7624
        img[2] -= 129.1863
    elif normalization == "VGGFace2":
        img *= 255.0
        img[0] -= 91.4953
        img[1] -= 103.8827
        img[2] -= 131.0912
    elif normalization == "ArcFace":
        img = (img - 0.5) / 0.5  # Equivalent to: (img - 127.5) / 128
    else:
        raise ValueError(f"Unimplemented normalization type - {normalization}")

    return img


def resize_image(img: torch.Tensor, target_size: Tuple[int, int]) -> torch.Tensor:
    """
    Resize an image to expected size of a ml model with adding black pixels.

    Args:
        img (torch.Tensor): Pre-loaded image tensor with shape (C, H, W).
        target_size (tuple): Input shape of ml model (width, height).

    Returns:
        torch.Tensor: Resized input image.
    """
    _, h, w = img.shape
    target_h, target_w = target_size

    if h == target_h and w == target_w:
        return img

    # Resize while maintaining aspect ratio
    scale = min(target_h / h, target_w / w)
    new_h, new_w = int(h * scale), int(w * scale)
    img_resized = F.interpolate(
        img.unsqueeze(0), size=(new_h, new_w), mode="bilinear", align_corners=False
    ).squeeze(0)

    # Pad the image to the target size
    pad_h = target_h - new_h
    pad_w = target_w - new_w
    padding = (
        pad_w // 2,  # left
        pad_w - pad_w // 2,  # right
        pad_h // 2,  # top
        pad_h - pad_h // 2,  # bottom
    )
    img_padded = F.pad(img_resized, padding, mode="constant", value=0)

    # Final size verification
    final_c, final_h, final_w = img_padded.shape
    if final_h != target_h or final_w != target_w:
        img_padded = F.interpolate(
            img_padded.unsqueeze(0),
            size=(target_h, target_w),
            mode="bilinear",
            align_corners=False,
        ).squeeze(0)

    return img_padded
