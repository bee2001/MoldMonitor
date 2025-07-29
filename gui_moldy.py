# gui_moldy.py

import tkinter as tk
from tkinter import filedialog, messagebox
import tkcalendar as tkc
from PIL import Image, ImageTk
from ultralytics import YOLO
import os
import time
import threading
from datetime import datetime, timedelta
from detections_manager_moldy import DetectionsManager
detections_manager_shared = DetectionsManager()  # main detections manager instance to be used by the whole app
from detect_moldy import DetectMoldy
dtm = DetectMoldy()
from report_gen_moldy import GeneReport
grp = GeneReport()

# time from GUI opened
now = datetime.now()
now2 = now.strftime("%Y/%m/%d %H:%M:%S")
date1 = now.strftime("%Y%m%d")
date2 = now.strftime("%Y_%m_%d_%H_%M_%S")

# variables
yolo_weight = "20240828_0100_best.pt"
main_results_folder = f"Results"
results_folder = ""
report_summary = ""
raw_folder = ""
tagged_folder = ""
images_amount = 0
detected_images = 0
clean_breads = 0
moldy_breads = 0
rhizo_muc = 0
pen_asper = 0
both_groups = 0
failed_scans = 0
numbers_list = []


class MoldyApp:
    def check_yolo_weight(self):
        # checks if the weight has the required classes
        yolo_classes = {0: "clean_bread", 1: "moldy_bread", 2: "rhizopus_mucor", 3: "peni_asper"}
        if YOLO(yolo_weight).names == yolo_classes:
            messagebox.showinfo(title="YOLO Weight Check", message="YOLO weight classes are valid.")
        else:
            messagebox.showerror(title="Error",
                                 message=f"The YOLO weight is missing classes. Contact the developer for "
                                         f"assistance.\n\nCurrent weight contains the following classes:"
                                         f"\n{YOLO(yolo_weight).names}"
                                         f"\n\nWeight must contain the following classes:"
                                         f"\n{yolo_classes}")
            exit()

    def make_main_results_folder(self):
        # makes the main folder for all results
        if not os.path.exists(main_results_folder):
            messagebox.showinfo("Info",
                                f"Creating main folder for all detection result folders.\nFolder name: "
                                f"{main_results_folder}")
            os.makedirs(main_results_folder)

    def make_results_folder(self):
        # folder to store report summary and folders of the scanned images
        results_folder_plus = f"{main_results_folder}/Moldy_{date2}"
        global results_folder
        results_folder = results_folder_plus
        if not os.path.exists(results_folder):
            messagebox.showinfo("Info",
                                f"Creating folder for detection results.\nFolder name: {results_folder}")
            os.makedirs(results_folder)

    def make_scanned_folders(self):
        # folders to store scanned images from the detection part
        rawraw_folder = f"{results_folder}/raw"
        rawtagged_folder = f"{results_folder}/tagged"
        global raw_folder
        global tagged_folder
        raw_folder = rawraw_folder
        tagged_folder = rawtagged_folder
        if not os.path.exists(raw_folder):
            os.makedirs(raw_folder)
            if not os.path.exists(tagged_folder):
                os.makedirs(tagged_folder)

    def __init__(self, root):
        # the GUI itself
        self.list_image_paths = []
        self.report_folder_path = tk.StringVar()
        self.image_path = tk.StringVar()
        self.image_folder_path = None
        self.mfg_date = None
        self.exp_date = None
        self.photo_date = None

        self.detections_manager = detections_manager_shared
        self.gp = grp
        self.root = root
        self.root.title("MoldMonitor")
        self.root.geometry("950x650")
        self.root.configure(background="gray17")
        self.root.iconbitmap("icon_ICO.ico")

        # GUI elements (buttons, labels, etc.)
        # title
        self.root.labelTitle = tk.Label(root, bg="gray17", fg="white", text="MoldMonitor", font=("BahnSchrift", 20))
        self.root.labelTitle.grid(row=1, column=2, padx=20, pady=10)

        # image displays + information box
        self.root.inputImgDis = tk.Canvas(root, bg="black", borderwidth=3, relief="groove", width=250, height=250)
        self.root.inputImgDis.grid(row=2, column=1, padx=10, pady=10)

        self.root.outputImgDis = tk.Canvas(root, bg="black", borderwidth=3, relief="groove", width=250, height=250)
        self.root.outputImgDis.grid(row=2, column=2, padx=10, pady=10)

        self.root.Informasi = tk.Text(root, height=13, width=40, bg="light grey", font=("Noto Mono", 11))
        self.root.Informasi.insert("1.0", "Awaiting images")
        self.root.Informasi.configure(state="disabled")
        self.root.Informasi.grid(row=2, column=3, padx=10, pady=10)

        # column 1
        self.root.imgSelect = tk.Button(root, text="Select Image(s)", command=self.load_images, bg="light grey",
                                        font=("BahnSchrift", 12), width=20)
        self.root.imgSelect.grid(row=3, column=1, padx=10, pady=10)

        self.root.imgFoldSelect = tk.Button(root, text="Select Image Folder", command=self.load_image_folder,
                                            bg="light grey",
                                            font=("BahnSchrift", 12), width=20)
        self.root.imgFoldSelect.grid(row=4, column=1, padx=10, pady=10)

        # column 2
        self.root.mfgDateSel = tk.Label(root, text="Manufacture Date", bg="light grey", font=("BahnSchrift", 12),
                                        width=20)
        self.root.mfgDateSel.grid(sticky="E", row=3, column=2, padx=10, pady=10)

        self.root.expDateSel = tk.Label(root, text="Expiry Date", bg="light grey", font=("BahnSchrift", 12), width=20)
        self.root.expDateSel.grid(sticky="E", row=4, column=2, padx=10, pady=10)

        self.root.takeDateSel = tk.Label(root, text="Date of Photo(s)", bg="light grey", font=("BahnSchrift", 12),
                                         width=20)
        self.root.takeDateSel.grid(sticky="E", row=5, column=2, padx=10, pady=10)

        self.root.detection = tk.Button(root, text="Start Detecting", command=self.gui_start_detect, bg="light grey",
                                        font=("BahnSchrift", 12), width=20)
        self.root.detection.grid(sticky="E", row=6, column=2, padx=10, pady=10)

        self.root.reset = tk.Button(root, text="Reset", command=self.reset_app, bg="light grey",
                                    font=("BahnSchrift", 12), width=20)
        self.root.reset.grid(sticky="E", row=7, column=2, padx=10, pady=10)

        # column 3
        self.root.mfgDateView = tkc.DateEntry(root, date_pattern="y-mm-dd", font=("BahnSchrift", 12), width=20)
        self.root.mfgDateView.grid(sticky="W", row=3, column=3, padx=10, pady=10)

        self.root.expDateView = tkc.DateEntry(root, date_pattern="y-mm-dd", font=("BahnSchrift", 12), width=20)
        self.root.expDateView.grid(sticky="W", row=4, column=3, padx=10, pady=10)

        self.root.photoDateView = tkc.DateEntry(root, date_pattern="y-mm-dd", font=("BahnSchrift", 12), width=20)
        self.root.photoDateView.grid(sticky="W", row=5, column=3, padx=10, pady=10)

        self.root.open_PDF = tk.Button(root, text="Open Report Summary", command=self.view_report, bg="light grey",
                                       font=("BahnSchrift", 12), width=20, state="disabled")
        self.root.open_PDF.grid(sticky="W", row=6, column=3, padx=10, pady=10)

        self.root.openRepFld = tk.Button(root, text="Open Results Folder", command=self.open_current_result_folder,
                                         bg="light grey",
                                         font=("BahnSchrift", 12), width=20)
        self.root.openRepFld.grid(sticky="W", row=7, column=3, padx=10, pady=10)

        # checkers
        self.check_yolo_weight()

        # make results folder
        self.make_main_results_folder()
        self.make_results_folder()
        self.make_scanned_folders()

    def load_images(self):
        # loading images by themselves
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        self.list_image_paths = list(file_paths)
        image_files = [f for f in self.list_image_paths]
        global images_amount
        images_amount = len(image_files)

        # update the Informasi widget with info about the images
        self.root.Informasi.configure(state="normal")
        if image_files:
            self.root.Informasi.insert("end", "\nImages found:\n")
            for image in image_files:
                self.root.Informasi.insert("end", f"- {image}\n")
        else:
            self.root.Informasi.insert("end", "No valid images found in the selected folder.\n")

        self.root.Informasi.configure(state="disabled")

    def load_image_folder(self):
        # loading images per folder
        self.image_folder_path = filedialog.askdirectory()
        if self.image_folder_path:
            # filter files in the selected folder for valid image types
            valid_extensions = (".jpg", ".jpeg", ".png")
            image_files = [f for f in os.listdir(self.image_folder_path) if f.lower().endswith(valid_extensions)]
            global images_amount
            images_amount = len(image_files)

            # update the Informasi widget with info about the loaded folder and its images
            self.root.Informasi.configure(state="normal")
            self.root.Informasi.insert("end", f"\nImage folder loaded: {self.image_folder_path}\n")

            if image_files:
                self.root.Informasi.insert("end", "Images found:\n")
                for image in image_files:
                    self.root.Informasi.insert("end", f"- {image}\n")
            else:
                self.root.Informasi.insert("end", "No valid images found in the selected folder.\n")

            self.root.Informasi.configure(state="disabled")

    def gui_start_detect(self):
        self.root.detection.configure(state="disabled")
        self.root.reset.configure(state="disabled")

        if not self.list_image_paths:
            if not self.image_folder_path:
                messagebox.showerror(title="Error", message="Please select an image first.")
                self.root.detection.configure(state="normal")
                self.root.reset.configure(state="normal")
                return

        self.root.Informasi.configure(state="normal")
        self.root.Informasi.delete("1.0", "end")
        self.root.Informasi.insert("end", "Starting Detection Run")
        self.root.Informasi.configure(state="disabled")

        # collecting input dates from GUI
        self.mfg_date = self.root.mfgDateView.get_date()
        self.exp_date = self.root.expDateView.get_date()
        self.photo_date = self.root.photoDateView.get_date()

        # validate dates
        if self.mfg_date > self.exp_date:
            messagebox.showerror(title="Error", message="Manufacture date cannot be later than expiration date")
            self.root.detection.configure(state="normal")
            self.root.reset.configure(state="normal")
            return

        if self.mfg_date == self.exp_date:
            messagebox.showerror(title="Error", message="Manufacture date cannot be the same as expiration date")
            self.root.detection.configure(state="normal")
            self.root.reset.configure(state="normal")
            return

        if self.exp_date > self.photo_date:
            messagebox.showerror(title="Error", message="Expiry date cannot be later than photo date")
            self.root.detection.configure(state="normal")
            self.root.reset.configure(state="normal")
            return

        if self.mfg_date > self.photo_date:
            messagebox.showerror(title="Error", message="Manufacture date cannot be later than photo date")
            self.root.detection.configure(state="normal")
            self.root.reset.configure(state="normal")
            return

        # run the detection in a separate thread
        detection_thread = threading.Thread(target=self.run_detections)
        detection_thread.start()

    def run_detections(self):
        global detected_images
        global clean_breads
        global moldy_breads
        global rhizo_muc
        global pen_asper
        global both_groups
        global failed_scans

        # load images to process
        images_to_process = []
        if self.list_image_paths:
            images_to_process = self.list_image_paths
        elif self.image_folder_path:
            # load all images in the folder
            images_to_process = [os.path.join(self.image_folder_path, img) for img in os.listdir(self.image_folder_path)
                                 if img.endswith(("jpg", "jpeg", "png"))]

        # process each image
        for image in images_to_process:
            self.display_image(image, self.root.inputImgDis)
            self.root.outputImgDis.delete("all")
            self.dm = dtm
            the_output = self.dm.detect_mold(image, raw_folder, tagged_folder, self.photo_date)

            is_valid, return_result, result_image = the_output

            if not is_valid:
                self.display_image(result_image, self.root.outputImgDis)
                detected_images += 1
                failed_scans += 1
                self.root.Informasi.configure(state="normal")
                self.root.Informasi.delete("1.0", "end")
                self.root.Informasi.insert("end", f"{detected_images} image(s) processed out of {images_amount}")
                self.root.Informasi.insert("end", f"\n\n{return_result}")
                self.root.Informasi.insert("end", f"\n\nImage:\n{image}")
                self.root.Informasi.configure(state="disabled")
                time.sleep(2)  # to let user see the info comfortably
                continue
            else:
                self.display_image(result_image, self.root.outputImgDis)
                detected_images += 1
                imn = os.path.basename(image)
                index = self.detections_manager.get_detection_index(imn)

                if index != -1:  # ensure that the detection is found
                    detection = self.detections_manager.get_detection(index)  # get the detection object

                    # retrieve breadprmtr (bpr) and molds (mld) from the detection object
                    bpr = detection.get_breadprmtr()
                    mld = detection.get_molds()
                    bpr_class = bpr[0][0]
                    # check if mld is a list of lists
                    if isinstance(mld, list) and all(isinstance(sublist, list) for sublist in mld):
                        # create a set of the first elements from each sublist in mld
                        mld_first_elements = {sublist[0] for sublist in mld}
                    elif isinstance(mld, int):
                        # if mld is an integer, create a set with just that integer
                        mld_first_elements = {mld}
                    else:
                        # handle unexpected types
                        mld_first_elements = set()
                        self.root.Informasi.configure(state="normal")
                        self.root.Informasi.delete("1.0", "end")
                        self.root.Informasi.insert("end", f"Unexpected mold genus type: {mld}")
                        self.root.Informasi.insert("end", f"\n\nThis not normal")
                        self.root.Informasi.insert("end", f"\nContact the developer for assistance")
                        self.root.Informasi.configure(state="disabled")

                    if bpr_class == 0:
                        clean_breads += 1
                    elif bpr_class == 1:
                        moldy_breads += 1
                        if 2 in mld_first_elements and 3 in mld_first_elements:
                            both_groups += 1
                        elif 2 in mld_first_elements:
                            rhizo_muc += 1
                        else:
                            pen_asper += 1
                    else:
                        self.root.Informasi.configure(state="normal")
                        self.root.Informasi.delete("1.0", "end")
                        self.root.Informasi.insert("end", f"clean or moldy class returns {bpr_class}")
                        self.root.Informasi.insert("end", f"\n\nThis not normal")
                        self.root.Informasi.insert("end", f"\nContact the developer for assistance")
                        self.root.Informasi.configure(state="disabled")

                self.root.Informasi.configure(state="normal")
                self.root.Informasi.delete("1.0", "end")
                self.root.Informasi.insert("end", f"{detected_images} image(s) processed out of {images_amount}")
                if bpr_class == 1:
                    self.root.Informasi.insert("end", f"\n\nClean or Moldy?: Moldy\n\nMolds: {mld_first_elements}")
                    self.root.Informasi.insert("end", f"\n\nMold Genus Group 2: Rhizopus/Mucor")
                    self.root.Informasi.insert("end", f"\nMold Genus Group 3: Penicillium/Aspergillus")
                else:
                    self.root.Informasi.insert("end", f"\n\nClean or Moldy?: Clean")
                self.root.Informasi.configure(state="disabled")
                time.sleep(2)  # to let user see the info comfortably

        # inform user and re-enable the detection button after processing is complete
        self.root.Informasi.configure(state="normal")
        self.root.Informasi.delete("1.0", "end")
        self.root.Informasi.insert("end", f"Detection run completed\n")
        self.root.Informasi.insert("end", f"\nClean Breads      = {clean_breads}")
        self.root.Informasi.insert("end", f"\nMoldy Breads      = {moldy_breads}")
        self.root.Informasi.insert("end", f"\nRhizopus/Mucor    = {rhizo_muc}")
        self.root.Informasi.insert("end", f"\nPenicillium/Asper = {pen_asper}")
        self.root.Informasi.insert("end", f"\nBoth Groups       = {both_groups}")
        self.root.Informasi.insert("end", f"\nValid Scans       = {detected_images - failed_scans}")
        self.root.Informasi.insert("end", f"\nInvalid Scans     = {failed_scans}")
        self.root.Informasi.insert("end", f"\nTotal             = {detected_images}")
        self.root.Informasi.insert("end", f"\n\nMaking Report Summary")
        self.init_report_summary()
        self.root.Informasi.configure(state="disabled")

    def display_image(self, image_path, canvas):
        try:
            resized_img = Image.open(image_path)
            resized_img = resized_img.resize((250, 250))
            tk_img = ImageTk.PhotoImage(resized_img)

            # clear the existing canvas content
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img  # Keep a reference to avoid garbage collection
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load image: {str(e)}")

    def init_report_summary(self):
        # to initialize the thread where the report generator is made
        report_thread = threading.Thread(target=self.make_report_summary)
        report_thread.start()

    def make_report_summary(self):
        global report_summary
        numbers_list.append(images_amount)  # 0
        numbers_list.append(detected_images)  # 1
        numbers_list.append(clean_breads)  # 2
        numbers_list.append(moldy_breads)  # 3
        numbers_list.append(rhizo_muc)  # 4
        numbers_list.append(pen_asper)  # 5
        numbers_list.append(both_groups)  # 6
        numbers_list.append(failed_scans)  # 7
        # array will be in that order

        # generate_report(results_folder, numbers_list, mfg_date, exp_date, photo_date, curr_date)
        makeReport = self.gp.generate_report(results_folder, numbers_list, self.mfg_date, self.exp_date, self.photo_date, now)
        report_summary = makeReport
        if report_summary:
            self.root.Informasi.configure(state="normal")
            self.root.Informasi.delete("12.0", "12.end")
            self.root.Informasi.insert("end", "Report Summary Ready")
            self.root.Informasi.configure(state="disabled")
            self.root.open_PDF.configure(state="normal")
            self.root.reset.configure(state="normal")
            self.root.detection.configure(state="normal")

    def view_report(self):
        os.startfile(f"{os.path.abspath(report_summary)}")

    def open_current_result_folder(self):
        os.startfile(f"{os.path.abspath(results_folder)}")

    def reset_app(self):
        # reset the application's state including making new results folder
        global now, now2, date1, date2, detected_images, clean_breads, moldy_breads, rhizo_muc, pen_asper,\
            both_groups, failed_scans, images_amount, report_summary, numbers_list
        now = datetime.now()
        now2 = now.strftime("%Y/%m/%d %H:%M:%S")
        date1 = now.strftime("%Y%m%d")
        date2 = now.strftime("%Y_%m_%d_%H_%M_%S")
        images_amount = 0
        detected_images = 0
        clean_breads = 0
        moldy_breads = 0
        rhizo_muc = 0
        pen_asper = 0
        both_groups = 0
        failed_scans = 0
        numbers_list = []
        report_summary = ""
        self.list_image_paths = []
        self.report_folder_path = tk.StringVar()
        self.image_path = tk.StringVar()
        self.mfg_date = None
        self.exp_date = None
        self.photo_date = None
        self.detections_manager.delete_detections()
        self.report_folder_path.set("")
        self.image_path.set("")
        self.root.inputImgDis.delete("all")
        self.root.outputImgDis.delete("all")
        self.root.Informasi.configure(state="normal")
        self.root.Informasi.delete("1.0", "end")
        self.root.Informasi.insert("end", "App has been reset\n")
        self.root.Informasi.insert("end", "Awaiting images")
        self.root.Informasi.configure(state="disabled")
        self.root.detection.configure(state="normal")
        self.root.open_PDF.configure(state="disabled")
        self.make_results_folder()
        self.make_scanned_folders()

def create_gui():
    root = tk.Tk()
    app = MoldyApp(root)
    return root