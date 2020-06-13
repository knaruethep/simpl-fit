from .helpers import *
import numpy as np

class ShoulderPress:
    def __init__(self, sets, reps, w, h):
        self.w = w
        self.h = h
        self.history = []
        self.wrist_min_pos = h
        self.wrist_max_pos = 0
        self.state = 0 #down state
        self.total_sets = sets
        self.total_reps = reps
        self.sets = 0
        self.reps = 0
    """
    Problems:
    -> Too deep on down
    -> Arms straight extended outwards
    """
    def run_critique(self, body_parts, check_specific_critique):
        self.add_to_history(body_parts)

        if not check_specific_critique:
            bool, critique, name = self.horizontal_extension_critique(body_parts, hist = False)
            if bool:
                return bool, critique, name

            bool, critique, name = self.elbow_lock_critique(body_parts, hist = False)
            if bool:
                return bool, critique, name

            bool, critique, name = self.full_range_critique(body_parts, hist = False)
            if bool:
                return bool, critique, name
        else:
            critique_func = getattr(self, check_specific_critique)
            bool, critique, name = critique_func(body_parts, hist = False)
            return bool, critique, name
            
        return False, "No critique", ""

    def horizontal_extension_critique(self, body_parts, hist = True):
        if hist:
            self.add_to_history(body_parts)
        self.update_state(body_parts)

        r, l = 0, 0
        rerror, lerror = False, False
        thresh = 15 * math.pi / 180

        try:
            rwrist_pos = bp_coordinates(body_parts, 4, self.w, self.h)
            relbow_pos = bp_coordinates(body_parts, 3, self.w, self.h)
            relbow_above_pos = (relbow_pos[0], relbow_pos[1] - 5)
            r = calculate_angle(rwrist_pos, relbow_pos, relbow_above_pos)

            if r > thresh:
                rerror = True

        except KeyError as e:
            r = 0
        try:
            lwrist_pos = bp_coordinates(body_parts, 7, self.w, self.h)
            lelbow_pos = bp_coordinates(body_parts, 6, self.w, self.h)
            lelbow_above_pos = (lelbow_pos[0], lelbow_pos[1] - 5)
            l = calculate_angle(lwrist_pos, lelbow_pos, lelbow_above_pos)

            if l > thresh:
                lerror = True
        except KeyError as e:
            l = 0

        if rerror and lerror:
            return True, "Move both your wrists until they're directly above your elbows", "horizontal_extension_critique"
        elif rerror:
            return True, "Move your right wrist until it's directly above your elbow", "horizontal_extension_critique"
        elif lerror:
            return True, "Move your left wrist until it's direclty above your elbow", "horizontal_extension_critique"
        else:
            return False, "No critique", ""

    def elbow_lock_critique(self, body_parts, hist = True):
        if hist:
            self.add_to_history(body_parts)
        self.update_state(body_parts)

        r, l = 0, 0
        rerror, lerror = False, False
        thresh = 10 * math.pi / 180

        try:
            rwrist_pos = bp_coordinates(body_parts, 4, self.w, self.h)
            relbow_pos = bp_coordinates(body_parts, 3, self.w, self.h)
            rshoulder_pos = bp_coordinates(body_parts, 2, self.w, self.h)
            r = calculate_angle(rwrist_pos, relbow_pos, rshoulder_pos)

            if r > math.pi - thresh:
                rerror = True

        except KeyError as e:
            r = 0
        try:
            lwrist_pos = bp_coordinates(body_parts, 7, self.w, self.h)
            lelbow_pos = bp_coordinates(body_parts, 6, self.w, self.h)
            lshoulder_pos = (lelbow_pos[0], lelbow_pos[1] - 5)
            l = calculate_angle(lwrist_pos, lelbow_pos, lshoulder_pos)

            if l > math.pi - thresh:
                lerror = True
        except KeyError as e:
            l = 0

        if rerror and lerror:
            return True, "Don't lock both your elbows at the top", "elbow_lock_critique"
        elif rerror:
            return True, "Don't lock your right elbow at the top", "elbow_lock_critique"
        elif lerror:
            return True, "Don't lock your left elbow at the top", "elbow_lock_critique"
        else:
            return False, "No critique", ""

    def full_range_critique(self, body_parts, hist = True):
        if hist:
            self.add_to_history(body_parts)
        self.update_state(body_parts)

        if self.avg_velocity() > 0 and self.state == 0 and self.elbow_angle(body_parts) > 55 * math.pi / 180:
            return True, "Extend your arms higher on the way up to get the full range of motion", "full_range_critique"
        elif self.avg_velocity() < 0 and self.state == 1 and self.elbow_angle(body_parts) < 135 * math.pi / 180:
            return True, "Bend your arms lower on the way down to get the full range of motion", "full_range_critique"
        else:
            return False, "No critique", ""

    def elbow_angle(self, body_parts):
        try:
            rwrist_pos = bp_coordinates(body_parts, 4, self.w, self.h)
            relbow_pos = bp_coordinates(body_parts, 3, self.w, self.h)
            rshoulder_pos = bp_coordinates(body_parts, 2, self.w, self.h)
            return calculate_angle(rwrist_pos, relbow_pos, rshoulder_pos)

        except:
            pass
        try:
            lwrist_pos = bp_coordinates(body_parts, 7, self.w, self.h)
            lelbow_pos = bp_coordinates(body_parts, 6, self.w, self.h)
            lshoulder_pos = bp_coordinates(body_parts, 5, self.w, self.h)
            return calculate_angle(lwrist_pos, lelbow_pos, lshoulder_pos)
        except:
            return False

    def avg_velocity(self):
        if len(self.history) == 3:
            weights = np.array([.3, .7])
            v = np.dot(weights, np.diff(np.array(self.history)))
            if -1.5 < v < 1.5:
                return 0
            else:
                return v
        else:
            return 0

    def update_state(self, body_parts):
        angle = self.elbow_angle(body_parts)
        if not angle:
            return
        else:
            if self.state == 0 and angle > 135 * math.pi / 180:
                self.state = 1
            elif self.state == 1 and angle < 55 * math.pi / 180:
                self.state = 0
                self.reps += 1

    def add_to_history(self, body_parts):
        avg_y = bp_coordinates_average(body_parts, 7, 4, self.w, self.h) #avg wrist pos

        if not avg_y:
            return
        else:
            avg_y = avg_y[1]

        if len(self.history) == 3:
            self.history = self.history[1:] + [avg_y]
        else:
            self.history.append(avg_y)

        if avg_y != None and avg_y < self.wrist_min_pos:
            self.wrist_min_pos = avg_y #highest position of wrist
        if avg_y != None and avg_y > self.wrist_max_pos:
            self.wrist_max_pos = avg_y #lowest position of wrist


def plank(body_parts, state, side, w, h):
    """
    Problems:
    ->  Deviation in waist:
        Body Parts:
           L/R Shoulder
           L/R Hip
           L/R Ankle
        Percent Deviation:
           (OptimalAngle - AngleDetected)/OptimalAngle * 100
        Params:
            OptimalAngle = pi
            Threshold = 0.1
    """

    def optimal_height_hips(body_parts, w, h):
        shoulder_pos = bp_coordinates_average(body_parts, 2, 5, w, h)
        ankle_pos = bp_coordinates_average(body_parts, 10, 13, w, h)

    def deviation_in_hips(body_parts, optimal_angle, w, h):
        """
        Calculate the deviation in the hips from an optimal angle.
        """
        shoulder_pos = bp_coordinates_average(body_parts, 2, 5, w, h)
        hip_pos = bp_coordinates_average(body_parts, 8, 11, w, h)
        ankle_pos = bp_coordinates_average(body_parts, 10, 13, w, h)
        try:
            # calculate angle
            angle_detected = calculate_angle(shoulder_pos, hip_pos, ankle_pos)
        except TypeError as e:
            raise e
        # calculate percent deviation
        deviation = percent_deviation(optimal_angle, angle_detected)
        return deviation

    critique = "No critique"
    if deviation_in_hips(body_parts, math.pi, w, h) > .3:
        critique = "Fix"

    return deviation_in_hips(body_parts, math.pi, w, h), critique, state-1

def curls(body_parts, state, side, w, h):
    """
    side - left or right, depending on user

    Problems:
    ->  Horizontal deviation in humerous to upper body:
        Body parts:
            L//R Shoulder
            L//R Elbow
            L//R Hip
        Percent Deviation:
            (OptimalAngle - AngleDetected)/OptimalAngle * 100
        Params:
            OptimalAngle = 0
            Threshold = 0.1
    """

    def angle_of_elbow(body_parts, side, w, h):
        try:
            if side == 'L':
                shoulder_pos = bp_coordinates(body_parts, 5, w, h)
                elbow_pos = bp_coordinates(body_parts, 6, w, h)
                wrist_pos = bp_coordinates(body_parts, 7, w, h)
            elif side == 'R':
                shoulder_pos = bp_coordinates(body_parts, 2, w, h)
                elbow_pos = bp_coordinates(body_parts, 3, w, h)
                wrist_pos = bp_coordinates(body_parts, 4, w, h)
            else:
                return -1
        except KeyError as e:
            return -1

        angle_detected = calculate_angle(wrist_pos, elbow_pos, shoulder_pos)

        return angle_detected


    def deviation_of_elbow(body_parts, side, optimal_angle, w, h):
        """
        Calculate the angular deviation of the elbow from the optimal
        """
        try:
            if side == 'L':
                shoulder_pos = bp_coordinates(body_parts, 5, w, h)
                elbow_pos = bp_coordinates(body_parts, 6, w, h)
                hip_pos = bp_coordinates(body_parts, 11, w, h)
            elif side == 'R':
                shoulder_pos = bp_coordinates(body_parts, 2, w, h)
                elbow_pos = bp_coordinates(body_parts, 3, w, h)
                hip_pos = bp_coordinates(body_parts, 8, w, h)
            else:
                return -1
        except KeyError as e:
            return -1

        try:
            if shoulder_pos and hip_pos and elbow_pos:
                # calculate angle
                angle_detected = calculate_angle(hip_pos, shoulder_pos, elbow_pos)
            else:
                return -1
        except TypeError as e:
            raise e

        # calculate percent deviation
        deviation = percent_deviation(optimal_angle, angle_detected)
        return deviation

    # Determine critique
    critique = "Nice form!"
    deviation = deviation_of_elbow(body_parts, side, 0, w, h)
    if deviation > 0.25:
        try:
            if side == 'L':
                elbow_pos = bp_coordinates(body_parts, 6, w, h)
                hip_pos = bp_coordinates(body_parts, 11, w, h)

                if elbow_pos[0] < hip_pos[0]:
                    critique = "Move your elbow backward."
                else:
                    critique = "Move your elbow forward."
            elif side == 'R':
                elbow_pos = bp_coordinates(body_parts, 3, w, h)
                hip_pos = bp_coordinates(body_parts, 8, w, h)

                if elbow_pos[0] < hip_pos[0]:
                    critique = "Move your elbow forward."
                else:
                    critique = "Move your elbow backward."
            else:
                return -1
        except KeyError as e:
            return -1

    # Determine if state change
    elbow_angle = angle_of_elbow(body_parts, side, w, h)
    if state == 1 and elbow_angle > 2.7:
        state = 2
    elif state == 2 and elbow_angle < 0.7:
        state = 1


    return deviation, critique, state

def pushup(body_parts, state, side, w, h):
    """
    Problems:
    ->  Deviation in waist:
        Body Parts:
           L/R Shoulder
           L/R Hip
           L/R Ankle
        Percent Deviation:
           (OptimalAngle - AngleDetected)/OptimalAngle * 100
        Params:
            OptimalAngle = pi
            Threshold = 0.1
    """

    def deviation_in_hips(body_parts, optimal_angle):
        # average shoulders
        shoulder_pos = bp_coordinates_average(body_parts, 2, 5, w, h)
        # average hips
        hip_pos = bp_coordinates_average(body_parts, 8, 11, w, h)
        # average ankles
        ankle_pos = bp_coordinates_average(body_parts, 10, 13, w, h)
        try:
            if shoulder_pos and hip_pos and ankle_pos:
                # calculate angle
                angle_detected = calculate_angle(shoulder_pos, hip_pos, ankle_pos)
            else:
                return -1
        except TypeError as e:
            raise e
        # calculate percent deviation
        deviation = percent_deviation(optimal_angle, angle_detected)
        return deviation

    return deviation_in_hips(body_parts, math.pi), 0, 0

def squats(body_parts, state, side, w, h):
    """
    Problems:
    - Squat depth
        Body Parts:
           L/R Ankle
           L/R Knee
           L/R Hip
        Percent Deviation:
           (OptimalAngle - AngleDetected)/OptimalAngle * 100
        Params:
            OptimalAngle = pi/2
            Threshold = TBD
    - Forward knee movement
        Body Parts:
            L/R Ankle
            L/R Knee
        Percent Deviation:
           (X_ANKLE - X_KNEE)/TibiaLength * 100
        Params:
            OptimalDeviation = 0
            Threshold = TBD
    - 'Divebombing'
        Body Parts:
            L/R Shoulder
            L/R Hip
        Percent Deviation:
           (X_SHOULDER - X_HIP)/TorsoLength * 100
        Params:
            OptimalDeviation = 0
            Threshold = TBD
    """
    def squat_depth_angle(body_parts, w, h):
        ankle = bp_coordinates_average(body_parts, 10, 13, w, h)
        knee = bp_coordinates_average(body_parts, 9, 12, w, h)
        hip = bp_coordinates_average(body_parts, 8, 11, w, h)
        try:
            if ankle and knee and hip:
                return calculate_angle(ankle, knee, hip)
            else:
                 return -1
        except TypeError as e:
            return -1

    def tibia_deviation(body_parts, w, h):
        ankle = bp_coordinates_average(body_parts, 10, 13, w, h)
        knee = bp_coordinates_average(body_parts, 9, 12, w, h)
        try:
            if ankle and knee:
                return 240*(ankle[0] - knee[0])**2
            else:
                return -1
        except:
            return -1

    squat_depth = squat_depth_angle(body_parts, w, h)
    if squat_depth < (math.pi/2):
        if state == 1:
            state = 2

    if squat_depth > (math.pi - 0.5):
        if state == 2:
            state = 1

    deviation = tibia_deviation(body_parts, w, h)
    if abs(deviation) > 1.45:
        critique = "Keep your knees above your toes!"
    else:
        critique = "Nice form! Keep it up."


    return squat_depth, critique, state
