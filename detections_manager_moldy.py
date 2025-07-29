# detections_manager_moldy.py

from detections_moldy import Detections

class DetectionsManager:
    def __init__(self):
        self.obj_detections = []

    def add_detection(self, imn, bpr, mld):
        detection = Detections(imn, bpr, mld)
        self.obj_detections.append(detection)

    def delete_detections(self):
        self.obj_detections.clear()

    def get_detection_index(self, imn):
        for index, detection in enumerate(self.obj_detections):
            if detection.get_imgname() == imn:
                return index
        return -1

    def get_detection(self, index):
        return self.obj_detections[index]

    def get_all_ratios(self):
        all_ratios = []

        for detection in self.obj_detections:
            image_name = detection.get_imgname()
            cleanOrMoldy = detection.get_breadprmtr()
            molds = detection.get_molds()

            mold_sums = {}
            for mold in molds:
                if isinstance(mold, list) and len(mold) >= 2:
                    mold_type = mold[0]  # get mold type (2 or 3)
                    mold_ratio = mold[-1]  # last value is the ratio

                    # sum the ratios for each mold type
                    if mold_type in mold_sums:
                        mold_sums[mold_type] += mold_ratio
                    else:
                        mold_sums[mold_type] = mold_ratio

            # prepare the consolidated result for this image
            result = [image_name, cleanOrMoldy[0][0]]
            for mold_type, total_ratio in mold_sums.items():
                result.append([mold_type, total_ratio])

            all_ratios.append(result)

        return all_ratios


