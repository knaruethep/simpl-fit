# SimpL-Critique

## Build Instructions
```bash
$ git clone https://github.com/SimpL-fit/SimpL-Critique.git
$ cd SimpL-Critique
$ python setup.py install
```

## Getting Started
### Webcam
```bash
$ python run_critique.py
```
This will run the critique network on your webcam using cv2 window.

args :-
```
--camera default:0
--resize if provided cv2 window is resized to match the config. Recommmended 432x368 or 656x368 or 1312x736 default:0x0
--model options:cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small default:mobilenet_thin
--workout options:shoulderpress / plank / curls / squats / pushup default:shoulderpress
--side options:L / R default:L
--output A file or directory to save output visualizations. If directory doesn't exist, it will be created.
```
### Video
```bash
$ python run_video_cr.py
```
This will run the critique network on the video provided in args.

args :-
```
--video path to video
--resolution if provided cv2 window is resized to match the config. Recommmended 432x368 or 656x368 or 1312x736 default:432x368
--model options:cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small default:mobilenet_thin
--workout options:shoulderpress / plank / curls / squats / pushup default:shoulderpress
--side options:L / R default:L
--output A file or directory to save output visualizations. If directory doesn't exist, it will be created.
```
