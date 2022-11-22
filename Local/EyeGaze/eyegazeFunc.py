import cv2 as cv
import mediapipe as mp
import numpy as np
import math
import time

def euclidean_distance(p1, p2):
    x1, y1 = p1.ravel()
    x2, y2 = p2.ravel()
    distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    return distance

def iris_position(face, iris_center, outer_point, inner_point):
    '''
    Left eye
            xxxxxxxxxxxxxxxxx
         xxxx    xxxxxx     xxxx
       xx      xx     xx        xxxx
     (1)      xx  (2)  xx          (3)
     xx        xx     xx         xxxxx
       xxxxxx   xxxxxxx   xxxxxxxx
            xxxxxxxxxxxxxx
    (1) outer point of eye
    (2) center point of iris
    (3) inner point of eye
    ratio = distance(1, 2) / distance(1, 3)
    '''
    center_to_right_dist = euclidean_distance(iris_center, outer_point)
    total_distance = euclidean_distance(outer_point, inner_point)
    ratio = center_to_right_dist / total_distance
    
    iris_position = ""
    
    if face == 'Left':
        if ratio < 0.5:
            iris_position = "center"
        else:
            iris_position = "left"
    elif face == "Right":
        if ratio < 0.5:
            iris_position = "center"
        else:
            iris_position = "right"
    else:
        if ratio <= 0.43:
            iris_position = "left"
        elif ratio > 0.57:
            iris_position = "right"
        else:
            iris_position = "center"
    
    return iris_position, ratio

LEFT_IRIS = [469, 470, 471, 472]
RIGHT_IRIS = [474, 475, 476, 477]
L_EYE_INNER = [133]
L_EYE_OUTER = [33] 
R_EYE_INNER = [362]
R_EYE_OUTER = [263]

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

def get_eye_position(frame):
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1, 
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        # flip the image horizontally for a later selfie-view display
        # also convert the color space from BGR to RGB
        frame = cv.flip(frame, 1)
        img_h, img_w, img_c = frame.shape
        
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        
        # to improve performance
        # get the result
        rgb_frame.flags.writeable = False
        results = face_mesh.process(rgb_frame)
        
        face_3d = []
        face_2d = []
        iris_pos = ''
        
        if results.multi_face_landmarks:            
            # Case 1. head_orientation
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                        x, y = int(lm.x * img_w), int(lm.y * img_h)
            
                        # get the 2D coordinates
                        face_2d.append([x, y])
                        
                        # get the 3D coordinates
                        face_3d.append([x, y, lm.z])
                        
                # convert it to the numpy array
                face_2d = np.array(face_2d, dtype=np.float64)
                
                # convert it to the numpy array
                face_3d = np.array(face_3d, dtype=np.float64)
                
                # camera matrix
                focal_length = 1 * img_w
                cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                        [0, focal_length, img_w / 2],
                                        [0, 0, 1]])
                
                # distortion parameters
                dist_matrix = np.zeros((4, 1), dtype=np.float64)
                
                # solve PnP
                success, rot_vec, trans_vec = cv.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
                
                # get rotational matrix and angles
                rmat, jac = cv.Rodrigues(rot_vec)
                angles, mtxR, mtxQ, Qx, Qy, Qz = cv.RQDecomp3x3(rmat)
                
                # get the y rotation degree
                x = angles[0] * 360
                y = angles[1] * 360

            # Case 2. eyes_position
            mesh_points = np.array([
                np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                for p in results.multi_face_landmarks[0].landmark
            ])

            (l_cx, l_cy), l_radius = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_radius = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            center_left = np.array([l_cx, l_cy], dtype=np.int32)
            center_right = np.array([r_cx, r_cy], dtype=np.int32)
            
            if y < -8: # head left
                iris_pos, ratio = iris_position('Left', center_right, mesh_points[R_EYE_OUTER], mesh_points[R_EYE_INNER][0])
                cv.circle(frame, center_right, int(l_radius), (255, 0, 255), 1, cv.LINE_AA)
            elif y > 8: # head right
                iris_pos, ratio = iris_position('Right', center_left, mesh_points[L_EYE_OUTER], mesh_points[L_EYE_INNER][0])
                cv.circle(frame, center_left, int(l_radius), (255, 0, 255), 1, cv.LINE_AA)
            else: # head forward
                iris_pos, ratio = iris_position('Forward', center_left, mesh_points[L_EYE_OUTER], mesh_points[L_EYE_INNER][0])
                cv.circle(frame, center_left, int(l_radius), (255, 0, 255), 1, cv.LINE_AA)

            cv.putText(
                frame,
                f"iris pos: {iris_pos} {ratio:.2f}",
                (30,30),
                cv.FONT_HERSHEY_PLAIN,
                2.4,
                (0,0,0),
                1,
                cv.LINE_AA
            )
            
    return iris_pos

def is_engagement(cap, eye_gaze_dict, breakToken):
    cap = cap
    
    eye_gaze_frame = 0
    total_frame = 0
    
    while not breakToken.is_cancelled:
        success, frame = cap.read()

        if not success:
            continue

        total_frame += 1
        
        if get_eye_position(frame) == 'center':
            eye_gaze_frame += 1

    '''
    if total_frame == 0:
        eye_gaze_dict['eye_gaze_frame'] = 0
        eye_gaze_dict['total_frame'] = 0
        eye_gaze_dict['eye_gaze_score'] = 0
        return
    '''
    
    eye_gaze_dict['eye_gaze_frame'] = eye_gaze_frame
    eye_gaze_dict['total_frame'] = total_frame
    ## ** add key "eye gaze score" and calculate it
    eye_gaze_dict['eye_gaze_score'] = eye_gaze_frame / total_frame


# ** add the function which calculates eye gaze score
def calculate_score(eye_gaze_list, normalize=1):
    total = 0
    
    for i in range(len(eye_gaze_list)):
        total += eye_gaze_list[i][-1]


    norm_score = (total / len(eye_gaze_list)) * normalize
    
    return norm_score