import argparse
import logging
import time
import base64
import cv2
import numpy as np
import imutils
import sys
import os

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
from vision import analyze

logger = logging.getLogger('TfPoseEstimator-Video')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation Video')
    parser.add_argument('--video', type=str, default='')
    parser.add_argument('--resolution', type=str, default='432x368', help='network input resolution. default=432x368')
    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    parser.add_argument('--workout', type=str, default="shoulderpress",
                        help='shoulderpress, plank, curls, squats, pushup')
    parser.add_argument('--side', type=str, default="L", help='L for left or R for right')
    parser.add_argument('--output', type=str, help='A file or directory to save output visualizations.')
    parser.add_argument('--setrep', nargs='+', type=int, default=[10], help='Sets and respective reps') #e.g. --setrep 10 8 6 --> args.setrep = [10, 8 ,6]

    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    prev_state = 0 #rest position
    state = 0
    setrep_count = (0, 0)

    w, h = model_wh(args.resolution)
    e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    cap = cv2.VideoCapture(args.video)
    frames_per_second = cap.get(cv2.CAP_PROP_FPS)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if cap.isOpened() is False:
        print("Error opening video stream or file")
    while cap.isOpened():
        ret_val, image = cap.read()
        logger.debug('Pose Estimation')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=4.0)
        body_parts = analyze.extract_body_parts(humans, image)
        if body_parts == -1:
            deviation = -1.0000
            critique = "No critique"
            state = prev_state
        else:
            prev_state = state
            deviation, critique, state = analyze.analyze_workout(body_parts, args.workout, prev_state, args.side)
        if prev_state == 2 and state == 1:
            setrep_count[1] += 1
        logger.debug('Crtique Assignment')
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        if state == 0:
            State = "rest"
        elif state == 1:
            State = "up"
        elif state == 2:
            State = "down"
        cv2.putText(image,"FPS: %f" % (1.0 / (time.time() - fps_time)),(10, 15),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 2)
        cv2.putText(image,"Workout: %s" %args.workout ,(10, 45),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 0, 0), 2)
        #cv2.putText(image,"Deviation: %f" %deviation ,(10, 65),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 2)
        cv2.putText(image,"Critique: %s" %critique ,(10, 85),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)
        cv2.putText(image,"State: %s" %State ,(10, 105),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)
        cv2.putText(image,"Set Count: %s" %setrep_count[0]+1, (10, 125), cv2,FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)
        cv2.putText(image,"Rep Count: %s" %setrep_count[1] ,(10, 145),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)
        cv2.imshow('SimpL', image)
        fps_time = time.time()
        if cv2.waitKey(1) == 27:
            break
        if setrep_count[1] == args.setrep[setrep_count[0]]:
            setrep_count[0] += 1
            setrep_count[1] = 0
        if cv2.waitKey(1) == 27:

    cv2.destroyAllWindows()
logger.debug('Terminated Successfully')
