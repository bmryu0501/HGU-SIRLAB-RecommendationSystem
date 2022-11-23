#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 16:00:38 2022

@author: shimgahyeon

This is the file for the image processing.
"""


import math
import cv2
import numpy as np
import matplotlib.pyplot as plt
import mediapipe as mp
from PIL import Image


def image_preprocessing(image):
    """
    This function preprocesses the input image.
    It calls all the function(resize, normalize, rotation, roi, face mesh)
        and return the result image.

    Parameters
    ----------
    image : input image (numpy)

    Returns
    -------
    result : preprocessed output image (numpy)
    """
    
    #image = cv2.imread(path)
    
    if(type(image) == type(None)):
        #print("Cannot preprocess. image is None.")
        return
    
    # resize (48, 48) -> (224, 224)
    resized_image = resize(image)
    # normalize
    normalized_image = normalize(resized_image)
    # face rotation with extracting roi 
    roi_image = rotation_roi(normalized_image)
    # resize roi.shape -> -> (224, 224)
    resized_roi = resize(roi_image) 
    # apply face mesh
    result = reduced_face_mesh(resized_roi)
    
    return result


def euclidean_distance(a, b):
    """
    This function calculates the euclidean distance between point a and b

    Parameters
    ----------
    a : point1 [x1, y1].
    b : point2 [x2, y2]

    Returns
    -------
    euclidean distance between a and b
    """
    
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    
    return math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1)* (y2 - y1))


def resize(image):
    """
    This function resizes the input image to (224, 224).

    Parameters
    ----------
    image : input image (numpy)

    Returns
    -------
    resized_image : resized output image (numpy)
    """
    
    if(type(image) == type(None)):
        #print("Cannot preprocess. image is None.")
        return
    
    image = image.astype(np.uint8)
    resized_image = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_LINEAR)
    return resized_image


def normalize(image):
    """
    This function normalizes the input image.

    Parameters
    ----------
    image :input image(numpy)

    Returns
    -------
    result : normalized output image (numpy)
    """
    
    if(type(image) == type(None)):
        #print("Cannot normalize. image is None.")
        return
    
    result = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    # print(type(result))
    return result


def rotation_roi(image):
    """
    This function rotates the input image to aligns with face
    and calls roi() to extract the ROI which matches the area of face.

    Parameters
    ----------
    image : input image (numpy)

    Returns
    -------
    roi_image: rotated roi output image (numpy)
    """
    
    if(type(image) == type(None)):
        #print("Cannot rotation. image is None.")
        return None, None
    
    # the position number of silhoueets
    silhouette = [
        10,  338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
        397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
        172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109]
    
    # for ROI
    x, y = 0, 0
    minX, minY = 1000, 1000 
    maxX, maxY = 0, 0
    roi_t = 10
    
    # for face mesh style
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_face_mesh = mp.solutions.face_mesh
    
    # For static images:
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:
        
        width = image.shape[1]
        height = image.shape[0]
        new_image = image.copy()
        
        # Convert the BGR image to RGB before processing.
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Print and draw face mesh landmarks on the image.
        if not results.multi_face_landmarks:
              return None
            
        annotated_image = image.copy()

        for face_landmarks in results.multi_face_landmarks:
            ### rotation
            irises = list(mp_face_mesh.FACEMESH_IRISES)
                
            # left eye 눈동자 상하 위치 인덱스: 0, 1 
            l_pt1_x = int(face_landmarks.landmark[irises[0][0]].x * width)
            l_pt1_y = int(face_landmarks.landmark[irises[0][0]].y * height)
            l_pt2_x = int(face_landmarks.landmark[irises[1][0]].x * width)
            l_pt2_y = int(face_landmarks.landmark[irises[1][0]].y * height)
            # right eye 눈동자 상하 위치 인덱스: 3, 6
            r_pt1_x = int(face_landmarks.landmark[irises[7][0]].x * width)
            r_pt1_y = int(face_landmarks.landmark[irises[7][0]].y * height)
            r_pt2_x = int(face_landmarks.landmark[irises[3][0]].x * width)
            r_pt2_y = int(face_landmarks.landmark[irises[3][0]].y * height)

            # left eye
            if l_pt1_x > l_pt2_x:
                left_eye_x = l_pt2_x + (l_pt1_x - l_pt2_x) // 2
            else:
                left_eye_x = l_pt1_x + (l_pt2_x - l_pt1_x) // 2

            left_eye_y = l_pt1_y + (l_pt2_y - l_pt1_y) // 2

            # right eye
            if r_pt1_x > r_pt2_x:
                right_eye_x = r_pt2_x + (r_pt1_x - r_pt2_x) // 2
            else:
                right_eye_x = r_pt1_x + (r_pt2_x - r_pt1_x) // 2

            right_eye_y = r_pt1_y + (r_pt2_y - r_pt1_y) // 2

            left_eye_center = (left_eye_x, left_eye_y)
            right_eye_center = (right_eye_x, right_eye_y)
            
            if left_eye_y < right_eye_y :
                point_3rd = (right_eye_x, left_eye_y)
                direction = 1 # 반시계방향
                # print("반시계방향 회전")
            else:
                point_3rd = (left_eye_x, right_eye_y)
                direction = -1 # 시계방향
                # print("시계방향 회전")

            a = euclidean_distance(left_eye_center, point_3rd)
            b = euclidean_distance(right_eye_center, left_eye_center)
            c = euclidean_distance(right_eye_center, point_3rd)

            cos_a = (b * b + c * c - a * a) / (2 * b * c)
            # print("cos(a) = ", cos_a)

            angle = np.arccos(cos_a)
            # print("angle : " , angle, " in radian")

            angle = (angle * 180) / math.pi
            # print("angle : ", angle, " in degree")

            if direction == 1:
                angle = 90 - angle

        rotated_image = Image.fromarray(annotated_image)
        rotated_image = np.array(rotated_image.rotate(direction * (-1) * angle))
    
    roi_image = roi(face_landmarks, rotated_image)
    
    return roi_image


def roi(face_landmarks, image):
    """
    This function extracts ROI which matches the area of face.

    Parameters
    ----------
    face_landmarks : data type only available with MediaPipe 
    image : input image (numpy)

    Returns
    -------
    roi image: ROI output image (numpy)
    """
    
    if(type(image) == type(None)):
        #print("Cannot extract roi. ")
        return _, None
    
     # the position number of silhoueets
    silhouette = [
        10,  338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
        397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
        172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109]
    
    # for ROI
    x, y = 0, 0
    minX, minY = 1000, 1000 
    maxX, maxY = 0, 0
    roi_t = 10
    
    height = image.shape[0]
    width = image.shape[1]
    
    for i in silhouette:
        # find silhouette
        x = int(face_landmarks.landmark[i].x * image.shape[1])
        y = int(face_landmarks.landmark[i].y * image.shape[0])
        
        # find ROI coordinate
        if x < minX:
            minX = x
        if y < minY:
            minY = y
        if x > maxX:
            maxX = x
        if y > maxY:
            maxY = y

    # adjust the points (x1, y1), (x2, y2)
    x1 = minX - roi_t
    y1 = minY - roi_t
    x2 = maxX + roi_t + 1
    y2 = maxY + roi_t + 1

    if(x1 < 0):
        x1 = 0
    if(y1 < 0):
        y1 = 0
    if(x2 > width or x2 < 0):
        x2 = width
    if(y2 > height or y2 < 0):
        y2 = height

    # extract roi
    #print(x1, x2, y1, y2)
    roi_image = image[y1:y2, x1:x2]

    return roi_image


def reduced_face_mesh(image):
    """
    This function applies face mesh to the face image
    and marks the major landmark on the image (eye, eyebrow, lips, silhouette).

    Parameters
    ----------
    image : input image (numpy)

    Returns
    -------
    annotated_image : marked facial landmark output image (numpy)
    """
    
    if(type(image) == type(None)):
        #prppprpsdfint("Cannot face mesh. image is None.")
        return
    
    # for face mesh style
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_face_mesh = mp.solutions.face_mesh
    
    # For static images:
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    
    height = image.shape[0]
    width = image.shape[1]
  
    landmarks = list(mp_face_mesh.FACEMESH_CONTOURS)
    
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:
        
        # Convert the BGR image to RGB before processing.
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Print and draw face mesh landmarks on the image.
        if not results.multi_face_landmarks:
            #print("Cannot find landmark on the image.")
            return
            
        annotated_image = image.copy()
        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2GRAY)
        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_GRAY2BGR)
        
        for face_landmarks in results.multi_face_landmarks:
            for i in range(len(landmarks)):
                x = int(face_landmarks.landmark[landmarks[i][0]].x * width)
                y = int(face_landmarks.landmark[landmarks[i][0]].y * height)
                
                cv2.line(annotated_image, (x, y), (x, y), (255, 0, 0), 2)
            
    return annotated_image