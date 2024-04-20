import string
import easyocr
import re


char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}

# OCR reader
reader = easyocr.Reader(['en'], gpu=False)

def get_car(plate, vehicle_ids):
    x1, y1, x2, y2, score, class_id = plate

    found = False
    for i in range(len(vehicle_ids)):
        x_car1, y_car1, x_car2, y_car2, car_id = vehicle_ids[i]
        if x1 > x_car1 and y1 > y_car1 and x2 < x_car2 and y2 < y_car2:
            return vehicle_ids[i]
    return -1, -1, -1, -1, -1

import re

# Assuming your dictionaries are defined as int_to_char and char_to_int

def license_complies_format(text):
    pattern = r"^([A-Z{dict_int_to_char_keys}])([A-Z{dict_int_to_char_keys}])([0-9]{dict_char_to_int_keys}|[0-9])([0-9]{dict_char_to_int_keys}|[0-9])([A-Z{dict_int_to_char_keys}])([A-Z{dict_int_to_char_keys}])([A-Z{dict_int_to_char_keys}])$".format(dict_int_to_char_keys="|".join(int_to_char.keys()), dict_char_to_int_keys="|".join(char_to_int.keys()))
    match = re.search(pattern, text)
    return bool(match)  # Return True if there's a match, False otherwise


def format_license(text):
    license_plate = ''
    mapping = {0: int_to_char, 1: int_to_char, 4: int_to_char, 5: int_to_char, 6: int_to_char,
            2: char_to_int, 3: char_to_int}
    for j in [0, 1, 2, 3, 4, 5, 6]:
        if text[j] in mapping[j].keys():
            license_plate += mapping[j][text[j]]
        else:
            license_plate += text[j]

    return license_plate


def read_plate(plate):
    detections = reader.readtext(plate)
    for detection in detections:
        bbox, text, score = detection
        text = text.upper().replace(' ', '')
        if license_complies_format(text):
            return format_license(text), score
    return None, None

def write_csv(results, output_path):
    """
    Write the results to a CSV file.

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output CSV file.
    """
    with open(output_path, 'w') as f:
        f.write('{},{},{},{},{},{},{}\n'.format('frame_nmr', 'car_id', 'car_bbox',
                                                'license_plate_bbox', 'license_plate_bbox_score', 'license_number',
                                                'license_number_score'))

        for frame_nmr in results.keys():
            for car_id in results[frame_nmr].keys():
                print(results[frame_nmr][car_id])
                if 'car' in results[frame_nmr][car_id].keys() and \
                'license_plate' in results[frame_nmr][car_id].keys() and \
                'text' in results[frame_nmr][car_id]['license_plate'].keys():
                    f.write('{},{},{},{},{},{},{}\n'.format(frame_nmr,
                                                            car_id,
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['car']['bbox'][0],
                                                                results[frame_nmr][car_id]['car']['bbox'][1],
                                                                results[frame_nmr][car_id]['car']['bbox'][2],
                                                                results[frame_nmr][car_id]['car']['bbox'][3]),
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][0],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][1],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][2],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][3]),
                                                            results[frame_nmr][car_id]['license_plate']['bbox_score'],
                                                            results[frame_nmr][car_id]['license_plate']['text'],
                                                            results[frame_nmr][car_id]['license_plate']['text_score'])
                            )
        f.close()