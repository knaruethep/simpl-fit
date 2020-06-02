# SimpL-Critique

## Build Instructions
```bash
$ git clone https://github.com/sanil-shrvn/SimpL-Critique.git
$ cd SimpL-Critique
$ python setup.py install
```

## Getting Started
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
--output #in process
```
