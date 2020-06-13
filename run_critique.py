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
from vision import workouts

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
fps_time = 0

# Load model

def str2bool(v):
    return v.lower() in {"yes", "true", "t", "1"}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)

    parser.add_argument('--resize', type=str, default='432x368',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=4.0')

    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')

    parser.add_argument('--tensorrt', type=str, default="False",
                        help='for tensorrt process.')
    parser.add_argument('--workout', type=str, default="shoulderpress",
                        help='shoulderpress, plank, curls, squats, pushup')
    parser.add_argument('--side', type=str, default="L", help='L for left or R for right')
    parser.add_argument('--setrep', nargs='+', type=int, default=[10], help='Sets and respective reps') #e.g. --setrep 10 8 6 --> args.setrep = [10, 8 ,6]
    parser.add_argument('--time', type = int, default = 30, help='How long to do the exercise')
    parser.add_argument('--output', type=str, help='A file or directory to save output visualizations. If directory doesn\'t exist, it will be created.')
    args = parser.parse_args()

    logger.debug('Initializating model %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)

    e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h), trt_bool=str2bool(args.tensorrt))

    logger.debug('Camera read')
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    logger.info('Camera image=%dx%d' % (image.shape[1], image.shape[0]))

    frames_per_second = cam.get(cv2.CAP_PROP_FPS)
    num_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
    cap_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if args.output:
        abspath = os.path.join(os.path.abspath('.'), args.output)

        if os.path.splitext(abspath)[1] == '': #abspath specifies a directory which may or may not exist
            if not os.path.exists(abspath):
                os.makedirs(abspath)
            output_fname = abspath + 'video_critique.avi'

        else: #abspath specifies a file
            if not os.path.exists(os.path.split(abspath)[0]):
                os.makedirs(os.path.split(abspath)[0])
            output_fname = abspath

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(output_fname, fourcc, fps = int(frames_per_second), frameSize = (cap_width, cap_height), isColor = True)

    prev_state = 0 #rest position
    state = 0
    setrep_count = [0, 0]

    shoulderpress = workouts.ShoulderPress(0, 0, w, h)
    check_specific_critique = ""
    prev_rep = 0
    while True:
        ret_val, image = cam.read()
        if args.output:
            writer.write(image)
        #
        # logger.debug('Pose Estimation')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
        body_parts = analyze.extract_body_parts(humans, image, w, h)
        bool, critique, func = shoulderpress.run_critique(body_parts, check_specific_critique)

        if bool:
            prev_rep = shoulderpress.reps
            check_specific_critique = func

        if shoulderpress.reps != prev_rep:
            check_specific_critique = ""


        logger.debug('Crtique Assignment')
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        logger.debug('Displaying')
        cv2.putText(image,"FPS: %f" %(1.0/(time.time()-fps_time)), (10, 15),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 2)
        cv2.putText(image,"Workout: %s" %args.workout ,(10, 45),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 0, 0), 2)
        cv2.putText(image,"Critique: %s" %critique ,(10, 85),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 2)
        cv2.imshow('SimpL', image)
        fps_time = time.time()

        if cv2.waitKey(1) == 27:
            break
        logger.debug('finished+')

    cv2.destroyAllWindows()
logger.debug('Terminated Successfully')
