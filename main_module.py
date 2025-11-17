from collections import OrderedDict
import cv2
import numpy as np

region_params = [
        ("Face", 1.2, 1.2),
        ("LeftEyebrow", 1.2, 1.2),
        ("RightEyebrow", 1.2, 1.2),
        ("LeftEye", 1.5, 2.0),
        ("RightEye", 1.5, 2.0),
        ("Nose", 2.0, 1.2),
        ("Mouth", 1.3, 1.2)
    ]

def shape_to_list(shape):
    return [int(shape.part(i).x) if j % 2 == 0 else int(shape.part(i).y)
            for i in range(68) for j in range(2)]


def shape_to_numpy_array(shape, dtype="int"):
    return np.array([[shape.part(i).x, shape.part(i).y] for i in range(68)], dtype=dtype)


def scale_shape(shape, xscale, yscale):
    coordinates = np.copy(shape)
    xmean, ymean = np.mean(coordinates, axis=0)
    coordinates[:, 0] = xscale * (coordinates[:, 0] - xmean) + xmean
    coordinates[:, 1] = yscale * (coordinates[:, 1] - ymean) + ymean
    return coordinates


def visualize_facial_landmarks(image, shape, colors=None, alpha=0.75):
    FACIAL_LANDMARKS_INDEXES = OrderedDict([
        ("Face", (0, 17)),
        ("LeftEyebrow", (22, 27)),
        ("RightEyebrow", (17, 22)),
        ("LeftEye", (42, 48)),
        ("RightEye", (36, 42)),
        ("Nose", (27, 36)),
        ("Mouth", (48, 68)),
        ("Jaw", (0, 17))
    ])

    if colors is None:
        colors = [
            (220, 220, 220), (19, 199, 109), (79, 76, 240), (230, 159, 23),
            (168, 100, 168), (158, 163, 32), (163, 38, 32), (180, 142, 220)
        ]

    overlay = image.copy()
    output = image.copy()

    SCALE_MAP = {name: (xscale, yscale) for name, xscale, yscale in region_params}
    pts_middle = np.array([
                    [0, 0], [0, 0],
                    [0, 0], [0, 0]
                ])
    new_eye_pts = np.array([
                    [0, 0], [0, 0],
                    [0, 0], [0, 0]
                ])
    for i, (name, (j, k)) in enumerate(FACIAL_LANDMARKS_INDEXES.items()):
        pts = shape[j:k]
        if name in SCALE_MAP:
            pts = scale_shape(pts, *SCALE_MAP[name])
            if name == "Face":
                face_x_min, face_x_max = np.min(pts[:, 0]), np.max(pts[:, 0])
                face_y_min, face_y_max = np.min(pts[:, 1]), np.max(pts[:, 1])
                face_y_min -= (face_y_max - face_y_min)
                pts = np.array([
                    [face_x_min, face_y_min], [face_x_min, face_y_max],
                    [face_x_max, face_y_max], [face_x_max, face_y_min]
                ])
                pts_middle = np.array([
                    [int((face_x_min+face_x_max)/2), face_y_min], [int((face_x_min+face_x_max)/2), face_y_max],
                    [face_x_min, int((face_y_min+face_y_max)/2)], [face_x_max, int((face_y_min+face_y_max)/2)]
                ])
            if name == "LeftEyebrow":
                new_array =pts
            if name == "RightEyebrow":
                new_array = np.vstack((new_array, pts))
            if name == "LeftEye":
                new_array = np.vstack((new_array, pts))
            if name == "RightEye":
                new_array = np.vstack((new_array, pts))
                eye_x_min, eye_x_max = np.min(new_array[:, 0]), np.max(new_array[:, 0])
                eye_y_min, eye_y_max = np.min(new_array[:, 1]), np.max(new_array[:, 1])
                new_eye_pts = np.array([
                    [eye_x_min, eye_y_min], [eye_x_min, eye_y_max],
                    [eye_x_max, eye_y_max], [eye_x_max, eye_y_min]
                ])
        # Draw landmark points
        for point in pts:
            cv2.circle(overlay, tuple(point), radius=3, color=(255, 0, 0), thickness=-1)

        # Draw regions
        if name == "Jaw":
            for l in range(1, len(pts)):
                cv2.line(overlay, tuple(pts[l - 1]), tuple(pts[l]), colors[i], 2)
        elif name == "Face":
            # cv2.rectangle(overlay, tuple(pts[0]), tuple(pts[2]), colors[i], 2)
            ##
            # cv2.rectangle(overlay, tuple(pts[0]), tuple(pts_middle[1]), colors[i], 2)
            # cv2.rectangle(overlay, tuple(pts_middle[0]), tuple(pts[2]), colors[i+1], 2)
            ##
            cv2.rectangle(overlay, tuple(pts[0]), tuple(pts_middle[3]), colors[i], 4)
            cv2.rectangle(overlay, tuple(pts_middle[2]), tuple(pts[2]), colors[i+1], 4)
        else:
            hull = cv2.convexHull(pts)
            cv2.drawContours(overlay, [hull], -1, colors[i], -1)
        # if name == "RightEye":
        #     cv2.rectangle(overlay, tuple(new_eye_pts[0]), tuple(new_eye_pts[2]), colors[i], 2)
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
    return output
