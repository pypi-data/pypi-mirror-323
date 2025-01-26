from io import BytesIO
import PIL
from datetime import datetime
import os
import sys
from typing import Optional, Union
from pathlib import Path
import argparse
import numpy as np
import io
import matplotlib.pyplot as plt
import base64
import yaml
import json

def uint8_imread(path: str):
    img = plt.imread(path)
    if img.dtype != np.uint8 and img.max() <= 1.0:
        img = img * 255
        img = img.astype(np.uint8)
    return img


def pil2str(x):
    buffer = BytesIO()
    x.save(buffer, format='PNG')
    b64 = base64.b64encode(buffer.getvalue())
    res = str(b64, 'utf-8')
    return res


def str2pil(s):
    b64 = base64.b64decode(s.encode('utf-8'))
    return PIL.Image.open(BytesIO(b64))


def get_datetime():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def init_project_dir_with(project_dir="."):
    def f(*args, **kwargs):
        return os.path.join(project_dir, *args, **kwargs)
    return f


def is_abs_path(path: Union[Path, str]):
    if isinstance(path, Path):
        return path.is_absolute()
    elif isinstance(path, str):
        return os.path.isabs(path)
    else:
        raise NotImplementedError 
        return False


def load_yaml(path):
    return yaml.safe_load(open(path, 'r'))


def load_namespace_from_yaml(path):
    D = load_yaml(path)
    return argparse.Namespace(**D)


def create_namespace(D:dict):
    return argparse.Namespace(**D)


def pt_to_pil(images):
    """
    Convert a torch image to a PIL image.
    """
    images = (images / 2 + 0.5).clamp(0, 1)
    images = images.cpu().permute(0, 2, 3, 1).float().numpy()
    images = numpy_to_pil(images)
    return images


def numpy_to_pil(np_images):
    """
    Convert a numpy image or a batch of images to PIL images.

    Args:
        np_images (numpy.ndarray): A numpy array of shape (H, W, C), (H, W), 
                                    or (N, H, W, C), (N, H, W).

    Returns:
        list: A list of PIL.Image objects, even if the input is a single image.
    """
    # Ensure batch dimension for single images
    if np_images.ndim == 3:  # Single RGB image or grayscale image (H, W, C)
        np_images = np_images[None, ...]
    elif np_images.ndim == 2:  # Single grayscale image (H, W)
        np_images = np_images[None, ..., None]  # Add channel and batch dimension

    # Ensure images are in uint8 format
    if np_images.dtype != np.uint8:
        np_images = (np_images * 255).round().astype("uint8")

    # Convert each image in the batch to a PIL Image
    pil_images = []
    for image in np_images:
        if image.shape[-1] == 1:  # Grayscale image
            pil_images.append(PIL.Image.fromarray(image.squeeze(), mode="L"))
        elif image.shape[-1] == 3:  # RGB image
            pil_images.append(PIL.Image.fromarray(image, mode="RGB"))
        elif image.shape[-1] == 4:  # RGBA image
            pil_images.append(PIL.Image.fromarray(image, mode="RGBA"))
        else:
            raise ValueError(f"Unsupported number of channels: {image.shape[-1]}")

    return pil_images if len(pil_images) > 1 else pil_images[0]  # Return a single image if applicable


def is_video_file(file_name):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']  # 添加其他视频文件格式
    return any(file_name.lower().endswith(ext) for ext in video_extensions)


def is_image_file(file_name):
    photo_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']  # 添加其他照片文件格式
    # 将文件名后缀转换为小写，并检查是否在照片文件后缀列表中
    return any(file_name.lower().endswith(ext) for ext in photo_extensions)


def is_document_file(file_name):
    document_extensions = ['.doc', '.docx', '.pdf', '.txt', '.odt']  # 添加其他文档文件格式

    # 将文件名后缀转换为小写，并检查是否在文档文件后缀列表中
    return any(file_name.lower().endswith(ext) for ext in document_extensions)


def o_d():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def mkdir_or_exist(dir_name, mode=0o777):
    if dir_name == '':
        return
    dir_name = os.path.expanduser(dir_name)
    os.makedirs(dir_name, mode=mode, exist_ok=True)


def append_current_dir(filepath):
    current_dir = os.path.dirname(os.path.abspath(filepath))
    sys.path.append(current_dir)
    return current_dir


def append_parent_dir(filepath):
    current_dir = os.path.dirname(os.path.abspath(filepath))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    return parent_dir


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)
    
    
def dump_json(d, path):
    with open(path, "w") as f:
        return json.dump(d, f, indent=4)


def pt2numpy(images):
    images.cpu().permute(0, 2, 3, 1).float().numpy()
    return images


def figure2pil(fig):
    buf = io.BytesIO()
    fig.savefig(buf, bbox_inches="tight", pad_inches=0.1)
    buf.seek(0)
    return PIL.Image.open(buf)


def normalize_image(image: np.ndarray, target_min: float = 0.0, target_max: float = 1.0) -> np.ndarray:
    """
    Normalize the pixel values of an image to a specified range.

    Parameters:
        image (np.ndarray): The input image as a NumPy array.
        target_min (float): The minimum value of the normalized output range. Default is 0.0.
        target_max (float): The maximum value of the normalized output range. Default is 1.0.

    Returns:
        np.ndarray: The normalized image with pixel values in the specified range.
    """
    min_val = np.min(image)
    max_val = np.max(image)

    if max_val == min_val:
        raise ValueError("Maximum and minimum values of the image are the same. Normalization cannot be performed.")

    normalized_image = (image - min_val) / (max_val - min_val) * (target_max - target_min) + target_min
    return normalized_image

#TODO
def use_importlib():
    pass