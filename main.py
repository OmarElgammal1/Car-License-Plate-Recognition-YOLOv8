from ultralytics import YOLO
import cv2

from sort.sort import *

from utils import *

results = {}

mot_tracker = Sort()

# import model for cars
car_model = YOLO('yolov8n.pt')

#import model for license plates
license_model = YOLO('train4\\weights\\best.pt')

capture = cv2.VideoCapture('video.mp4')

vehicles = [2, 3, 5, 7]
n_frames = -1

ret = True
while ret:
    n_frames += 1
    ret, frame = capture.read()
    if ret:
        results[n_frames] = {}
    
        # detect cars
        detections = car_model(frame)[0]
        detections_ = []
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicles:
                detections_.append([x1, y1, x2, y2, score])
    
        # track cars
        track_ids = mot_tracker.update(np.asarray(detections_))

        # detect license plates
        license_plates = license_model(frame)[0]
        for plate in license_plates.boxes.data.tolist():

            x1, y1, x2, y2, score, class_id = plate

            # assign each license to its car
            x_car1, y_car1, x_car2, y_car2, car_id = get_car(plate, track_ids)

            if car_id != -1:
                # crop license plate
                plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]

                # process license plate
                plate_crop_gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
                _, plate_crop_thr = cv2.threshold(plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)
                # plate_text = process_plate(plate_crop)
                # cv2.imshow('crop', plate_crop)
                # cv2.imshow('thr', plate_crop_thr)

                # cv2.waitKey(0)
                # read license plate
                plate_text, plate_text_score = read_plate(plate_crop_thr)
                if plate_text is not None:
                    results[n_frames][car_id] = {'car':{"bbox": [x_car1, y_car1, x_car2, y_car2]},
                                                'license_plate': {'bbox':[x1, y1, x2, y2],
                                                                'text': plate_text,
                                                                'bbox_score': score,
                                                                'text_score': plate_text_score}}
# write results
write_csv(results, 'test.csv')