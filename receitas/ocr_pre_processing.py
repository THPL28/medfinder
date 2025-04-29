import cv2
import numpy as np
from pdf2image import convert_from_path



def convert_pdf_to_images(pdf_path, dpi=200):
    """
    Converts a PDF file to a list of images.

    Args:
        pdf_path (str): The file path of the PDF.
        dpi (int): The DPI resolution for the output images.

    Returns:
        list: A list of PIL Image objects.
    """
    images = convert_from_path(pdf_path, dpi=dpi)
    return images


def reduce_noise(image):
    """
    Reduces noise in an image using thresholding.
    
    Args:
        image: The input image.
        
    Returns:
        The image with noise reduced.
    This method uses a simple threshold method
    """
    ret, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)    
    return thresh


def correct_rotation(image):
    """
    Corrects the rotation of an image if it's skewed.
    
    Args:
        image: The input image.
        
    Returns:
        The rotated image if needed.
    """
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def adjust_resolution(image, target_dpi=300):
    """
    Adjusts the resolution of an image to the target DPI.

    Args:
        image: The input image.
        target_dpi (int): The desired DPI.

    Returns:
        The image with adjusted resolution.
    """
    current_dpi = image.info.get('dpi', (72, 72))[0]
    scale_factor = target_dpi / current_dpi
    new_size = (int(image.size[0] * scale_factor), int(image.size[1] * scale_factor))
    return image.resize(new_size)
def preprocess_image(image):
    """
    Preprocesses an image for better OCR results.
    
    Args:
        image: The input image.
        
    Returns:
        The preprocessed image.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

    opening = reduce_noise(gray)

    # Handle skew
    coords = np.column_stack(np.where(opening > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = opening.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(opening, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

def pre_process_pdf(pdf_path):
    """
    Pre-processes a PDF file.

    Args:
        pdf_path (str): The file path of the PDF.

    Returns:
        list: A list of pre-processed images.
    """
    images = convert_pdf_to_images(pdf_path)
    pre_processed_images = []
    for image in images:
        adjusted_image = adjust_resolution(image)
        rotated_image = correct_rotation(adjusted_image)
        pre_processed_images.append(rotated_image)
    return pre_processed_images