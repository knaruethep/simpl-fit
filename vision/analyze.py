import os
import time
import math

import cv2
import numpy as np
import imutils
from .helpers import *

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
from vision import workouts

def extract_body_parts(humans, image, w, h, rotate=None):
    """
    Perform inference on image for body part locations.

    returns the best human subject object
    """

    if rotate:
        image = imutils.rotate(image, rotate)

    if not len(humans):
        return -1

    # extract the best subject
    subject = best_subject(humans, w, h)

    if subject:
        body_parts = subject.body_parts
    else:
        return -1

    if rotate:
        for i in body_parts:
            try:
                bp = (body_parts[i].x, body_parts[i].y)
                rt = rotation((0,0), bp, math.radians(-rotate))

                body_parts[i].x = rt[0]
                body_parts[i].y = rt[1]
            except AttributeError:
                pass

    return body_parts


def analyze_workout(body_parts, w, h, workout, state, timed = False, side=None):
    """
    Run the appropriate analyzer.

    return deviation and appropriate critiques
    """

    analyzer = getattr(workouts, workout)

    if timed:
        deviation, critique, state = analyzer(body_parts, state, side, w, h)
        if state == 0:
            state = "done"
        return deviation, critique, state
    else:
        pass

    if side:
        deviation, critique, state = analyzer(body_parts, state, side, w, h)
    else:
        deviation, critique, state = analyzer(body_parts, state, w, h)

    return deviation, critique, state
