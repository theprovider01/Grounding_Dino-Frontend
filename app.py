# -*- coding: utf-8 -*-
"""Untitled8.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dyLxZTtGkyiixNFSzmRJQjptFBRUL_Yx
"""

from groundingdino.util.inference import load_model, load_image, predict, annotate
from PIL import Image
import supervision as sv
import cv2
import os
import streamlit as st

import torch
import torchvision.transforms as transforms
import sys
import matplotlib.pyplot as plt
import numpy as np

CONFIG_PATH = "/drive/ngrok-ssh/GroundingDINO_SwinT_OGC.py"
CHECK_POINT_PATH = "/drive/ngrok-ssh/groundingdino_swint_ogc.pth"
my_model = load_model(CONFIG_PATH, CHECK_POINT_PATH)

#st.write(my_model)

def image_input(image_file):
    img = Image.open(image_file)
    return img

def concatenate(f1):
    filename = "/drive/ngrok-ssh/images_only/"
    IMAGE_PATH = "".join([filename, f1])
    value = IMAGE_PATH
    return IMAGE_PATH

def showInferenceImage(image, boxes, logits, phrases):
    """
    Plot bounding boxes and labels on the image.

    Args:
    - image (str): Tensor representation of the image
    - boxes (float): Predicted bounding box.
    - logits (float): Confidence score of the predicted box.
    - phrases (str): Associated labels/tokinizd text prompts for each bounding box.
    """

    # Convert the image tensor (C x H x W) to numpy format (H x W x C) for visualization.
    image_np = image.permute(1, 2, 0).numpy()

    # Denormalizing the image tensor. This step is essential because neural networks
    # often expect images in a normalized format. Here we are converting it back to the original format.
    mean = torch.tensor([0.485, 0.456, 0.406]).numpy()
    std = torch.tensor([0.229, 0.224, 0.225]).numpy()
    image_np = (image_np * std + mean).clip(0, 1)

    # Get the dimensions (height and width) of the image.
    img_height, img_width = image_np.shape[:2]

    # Create a figure for visualization.
    fig = plt.figure(figsize=(12, 12))
    plt.imshow(image_np)  # Display the image.

    # For each detected object in the image:
    for (box, logit, phrase) in zip(boxes, logits, phrases):
        # Extract the center coordinates and dimensions of the box.
        x_center, y_center, width, height = box

        # Convert normalized coordinates [0, 1] back to pixel values.
        x_center = x_center * img_width
        y_center = y_center * img_height
        width = width * img_width
        height = height * img_height

        # Calculate the top-left (x1, y1) and bottom-right (x2, y2) coordinates of the box.
        x1 = x_center - (width / 2)
        y1 = y_center - (height / 2)
        x2 = x_center + (width / 2)
        y2 = y_center + (height / 2)

        # Draw the bounding box on the image.
        rect = plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor='red', linewidth=1)
        plt.gca().add_patch(rect)

        # Create a label for the bounding box, containing the predicted phrase and its confidence score.
        label = f"{phrase} ({logit:.2f})"
        # Display the label just above the bounding box.
        plt.gca().text(x1, y1, label, bbox=dict(facecolor='red', alpha=0.5), fontsize=8, color='white')

    # Remove axis values for better visualization.
    plt.axis("off")
    return fig

#___________________Interface_____________________________

st.title("Grounding Dino")
st.write("Upload an image with text prompt and the model will perform annotation")
x =  st.text_input("Enter your text prompt here: ", "Type here...")
result = x.title()

st.write(result)

image_file = st.file_uploader("Upload an image",type = ['png', 'jpeg', 'jpg'])
if image_file is not None:
    file_details = {"Filename": image_file.name, "Filetype": image_file.type }
    st.write(file_details)
    img = image_input(image_file)
    st.image(img)
    with open(os.path.join("/drive/ngrok-ssh/images_only",image_file.name),"wb") as f:
      f.write(image_file.getbuffer())
      f1 = image_file.name
      st.write(f1)
      st.write(concatenate(f1))
    st.success("Saved File")
    TEXT_PROMPT = result
    BOX_TRESHOLD = 0.25
    TEXT_TRESHOLD = 0.10


#Load the image from the provided path and extract both its metadata and pixel data
    image_source, myimage = load_image(concatenate(f1))

# Use the model to predict bounding boxes, confidence scores (logits), and associated phrases (captions)
    boxes, logits, phrases = predict(
                model=my_model,
                image=myimage,
                caption=TEXT_PROMPT,
                box_threshold=BOX_TRESHOLD,
                text_threshold=TEXT_TRESHOLD,
                device="cpu"
            )
    #st.write(boxes, logits, phrases)
    
    #annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)

    #st.write(annotated_frame.shape)
    #output_img = sv.plot_image(annotated_frame, (16, 16))
    #st.write(output_img)
    st.write(showInferenceImage(myimage, boxes, logits, phrases))
