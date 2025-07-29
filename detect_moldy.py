# detect_moldy.py

from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import cv2
import os
from datetime import datetime, timedelta

import gui_moldy
from gui_moldy import detections_manager_shared as detections_manager

class DetectMoldy:
    def detect_mold(self, image_path, raw_folder, tagged_folder, photo_date):
        clean_present = False
        mold_present = False
        YOLO_weight = gui_moldy.yolo_weight

        # variables
        imn = os.path.basename(image_path)
        bpr = []
        mld = []

        # resize image
        resized_img = Image.open(image_path)
        resized_img = resized_img.resize((500, 500))

        # perform detection
        YOLO_weight_path = YOLO_weight
        the_yolo = YOLO(YOLO_weight_path)
        mold_detect = the_yolo.predict(source=resized_img, conf=0.25, save=False)

        # save raw detected image
        for result in mold_detect:
            # get the processed image (OpenCV format)
            processed_image = result.plot()  # plot() method provides an annotated image

            # specify the folder and file name where you want to save the image
            raw_filename = f"Raw_{os.path.basename(image_path)}"
            raw_path = f"{raw_folder}/{raw_filename}"
            display_raw_output = raw_path

            # save the image using OpenCV
            cv2.imwrite(raw_path, processed_image)

        # process results
        for result in mold_detect:  # iterate over each detection result
            for box in result.boxes:  # now "result" is an individual result object
                class_id = int(box.cls[0].item())  # class ID from detection
                x, y, w, h = box.xywh[0].tolist()  # convert the tensor to a list of scalars
                x, y, w, h = round(x), round(y), round(w), round(h)  # Round values
                size = w * h  # size calculation
                prob = round(float(box.conf[0].item()), 2)  # confidence probability
                entitas = [class_id, x, y, w, h, size, prob]  # detection entity

                if entitas[0] == 0:  # clean_bread
                    bpr.append(entitas)
                    mld.append(99)  # classify as clean in the mold list
                elif entitas[0] == 1:  # moldy_bread
                    bpr.append(entitas)
                elif entitas[0] == 2 or entitas[0] == 3:  # rhizopus_mucor
                    mld.append(entitas)  # Append to mold list

                #  debugging
                print(entitas)

        for bread in bpr:
            if isinstance(bread, list):
                if bread[0] == 0:  # clean bread
                    clean_present = True
                elif bread[0] in [1, 2]:  # moldy bread
                    mold_present = True

                if clean_present and mold_present:
                    # which should be impossible since this app is meant to check individual bread slices
                    reason_invalid = "Detected contains both clean and moldy bread"
                    # Discontinue checking this image and continue onto the next one without append to detections
                    return(False, reason_invalid, display_raw_output)
                elif len(bpr)> 1:
                    # no more than one bread per image pls
                    reason_invalid = "Detected  more than one bread"
                    return (False, reason_invalid, display_raw_output)
                elif len(bpr) == 0:
                    # no bread? preposterous
                    reason_invalid = "No bread detected"
                    return (False, reason_invalid, display_raw_output)

                if clean_present:
                    for mold in mld:
                        if isinstance(mold, list):
                            if mold[0] in [2, 3]:  # specific mold types (rhizopus_mucor or peni_asper)
                                specific_mold_detected = True
                                if specific_mold_detected:
                                    # clean bread cannot be moldy
                                    reason_invalid = "Detected clean bread but also detected mold"
                                    return (False, reason_invalid, display_raw_output)

                if mold_present:
                    mold_detected = any(isinstance(mold, list) and mold[0] in [2, 3] for mold in mld)
                    if not mold_detected:
                        # moldy bread must have its mold(s) detected
                        reason_invalid = "Detected moldy bread but no mold details were found"
                        return (False, reason_invalid, display_raw_output)

        if len(bpr) == 0:
            # no bread? preposterous
            reason_invalid = "No bread detected"
            return (False, reason_invalid, display_raw_output)

        if bpr[0][0] == 1:
            for mold_entitas in mld:
                if isinstance(mold_entitas, list) and len(
                        mold_entitas) > 5:  # check if mld entry is a list with enough elements
                    # calculate the size ratio of the mold to the bread
                    mold_size = mold_entitas[5] / bpr[0][
                        5]  # mold_entitas[5] is the size of the mold; bpr[5] is the size of the bread
                    mold_entitas.append(mold_size)  # append the size ratio to the mold entry

        detections_manager.add_detection(imn, bpr, mld)

        # generate additional info image
        tagged_output = []
        tagged_input_path = raw_path  # Make sure raw_path is correctly defined or passed to this function
        tagged_input_image = Image.open(tagged_input_path)
        image_width, image_height = tagged_input_image.size

        # create a new image with extended height for additional information
        extended_height = int(image_height * 1.75)
        new_tagged_image = Image.new("RGB", (image_width, extended_height), color=(255, 255, 255))

        # paste the original image onto the new image
        new_tagged_image.paste(tagged_input_image, (0, 0))

        draw = ImageDraw.Draw(new_tagged_image)

        # font type
        font = ImageFont.load_default()

        # initial Y position for the text
        text_y = image_height + 10
        now = datetime.now()
        text_datetime = now.strftime("%Y/%m/%d %H:%M:%S")
        draw.text((10, text_y), f"Date  : {text_datetime}", fill=(0, 0, 0), font=font)
        text_y += 20  # Space after the date

        # draw text for bpr detections
        for entitas in bpr:
            if isinstance(entitas, list):
                class_id, x, y, w, h, size, prob = entitas[:7]
                text = f"Class: {class_id}, Box: ({x}, {y}, {w}, {h}), Confidence: {prob:.0%}"
                draw.text((10, text_y), text, fill=(0, 0, 0), font=font)
                text_y += 15  # Move down for the next line of text

        # draw text for mld detections
        for entitas in mld:
            if isinstance(entitas, list):
                class_id, x, y, w, h, size, prob = entitas[:7]
                text = f"Class: {class_id}, Box: ({x}, {y}, {w}, {h}), Confidence: {prob:.0%}"
                if len(entitas) > 7:  # Check for size ratio to bread
                    size_ratio_to_bread = entitas[7]
                    text += f",\n Ratio to Bread: {size_ratio_to_bread:.5%}"
                draw.text((10, text_y), text, fill=(0, 0, 0), font=font)
                text_y += 30  # Move down for the next line of text

        # save the new image with extended white space and text
        output_filename_tagged = f"{tagged_folder}/tagged_{os.path.basename(image_path)}"
        new_tagged_image.save(output_filename_tagged)

        return(True, True, display_raw_output)
    # ALHAMDULILLAH SELESAI JUGA - 2024/08/29 06.47