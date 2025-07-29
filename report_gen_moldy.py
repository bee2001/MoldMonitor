# report_gen_moldy.py

from fpdf import FPDF
from gui_moldy import detections_manager_shared as detections_manager
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class GeneReport:
    def generate_report(self, result_folder, numbers_array, mfg_date, exp_date, photo_date, curr_date):
        pdf = FPDF()
        pdf.add_page()

        # variables
        detected_images = numbers_array[1]
        clean_breads = numbers_array[2]
        moldy_breads = numbers_array[3]
        rhizo_muc = numbers_array[4]
        pen_asper = numbers_array[5]
        both_groups = numbers_array[6]
        invalid_scans = numbers_array[7]

        now_date1 = curr_date.strftime("%Y/%m/%d %H:%M:%S")
        now_date2 = curr_date.strftime("%Y_%m_%d_%H_%M_%S")
        str_mfg_date = mfg_date.strftime("%Y/%m/%d")
        str_exp_date = exp_date.strftime("%Y/%m/%d")
        str_pho_date = photo_date.strftime("%Y/%m/%d")

        # report Title
        pdf.set_font("Courier", size=12)
        pdf.cell(200, 10, txt="Bread Mold Detection and Analysis Report Summary", ln=True, align="C")
        pdf.cell(200, 10, txt=f"{now_date1}", ln=True, align="C")

        # summary Information
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Manufacture Date\t: {str_mfg_date}", ln=True)
        pdf.cell(200, 10, txt=f"Expiry Date\t\t: {str_exp_date}", ln=True)
        pdf.cell(200, 10, txt=f"Photo Taken Date\t: {str_pho_date}", ln=True)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Clean Bread Count\t: {clean_breads}", ln=True)
        pdf.cell(200, 10, txt=f"Moldy Bread Count\t: {moldy_breads}", ln=True)
        pdf.cell(200, 10, txt=f"Total Bread Count\t: {detected_images - invalid_scans}", ln=True)

        # add a pie chart for moldy vs clean bread
        if clean_breads > 0:
            self.generate_pie_chart_breads(clean_breads, moldy_breads)
            pdf.image("moldy_vs_clean.png", x=10, y=None, w=100)

        # more detailed information regarding molds
        pdf.add_page()
        pdf.ln(10)
        if both_groups > 0:
            first_growth1 = photo_date - timedelta(days=7)
            first_growth2 = first_growth1.strftime("%Y-%m-%d")
            pdf.cell(200, 10, txt=f"Detected Genus Groups and Amounts:", ln=True)
            pdf.cell(200, 10, txt=f"    - Rhizopus/Mucor         : {rhizo_muc}", ln=True)
            pdf.cell(200, 10, txt=f"    - Penicillium/Aspergillus: {pen_asper}", ln=True)
            pdf.cell(200, 10, txt=f"    - Both                   : {both_groups}", ln=True)

            self.generate_pie_chart_both(rhizo_muc, pen_asper, both_groups)
            self.generate_ratio_chart_both()
            self.generate_ratio_chart_rm()
            self.generate_ratio_chart_pa()

            # retrieve all ratios using the updated method
            all_ratios = detections_manager.get_all_ratios()

            # prepare to aggregate mold ratios by mold type
            both_ratios = {2: [], 3: []}  # dictionary to store ratios for mold types 2 and 3
            for result in all_ratios:
                image_name = result[0]
                cleanOrMoldy = result[1]
                mold_data = result[2:]
                # only consider results if the bread is moldy (class not equal to 0)
                if cleanOrMoldy != 0:
                    for mold_type, total_ratio in mold_data:
                        if mold_type in both_ratios:
                            # to turn it into a more easily understandable percentage
                            both_ratios[mold_type].append(total_ratio * 100)
            # flatten the lists of ratios for each mold type
            both_ratios_flat = [ratio for ratios in both_ratios.values() for ratio in ratios]
            both_ratios_flat_max = max(both_ratios_flat)
            both_ratios_flat_min = min(both_ratios_flat)
            both_ratios_flat_avg = sum(both_ratios_flat) / len(both_ratios_flat)

            rm_ratio = []  # List to store ratios for Rhizopus/Mucor (mold type 2)
            for result in all_ratios:
                cleanOrMoldy = result[1]
                mold_data = result[2:]
                # only consider results if the bread is moldy (class not equal to 0)
                if cleanOrMoldy != 0:
                    for mold_type, total_ratio in mold_data:
                        if mold_type == 2:  # only process rhizopus-mucor
                            # to turn it into a more easily understandable percentage
                            rm_ratio.append(total_ratio * 100)
            rm_ratio_max = max(rm_ratio)
            rm_ratio_min = min(rm_ratio)
            rm_ratio_avg = sum(rm_ratio) / len (rm_ratio)

            pa_ratio = []  # list to store ratios for Rhizopus/Mucor (mold type 2)
            for result in all_ratios:
                cleanOrMoldy = result[1]
                mold_data = result[2:]
                # only consider results if the bread is moldy (class not equal to 0)
                if cleanOrMoldy != 0:
                    for mold_type, total_ratio in mold_data:
                        if mold_type == 3:  # only process penicillium-aspergillus
                            # to turn it into a more easily understandable percentage
                            pa_ratio.append(total_ratio * 100)
            pa_ratio_max = max(pa_ratio)
            pa_ratio_min = min(pa_ratio)
            pa_ratio_avg = sum(pa_ratio) / len(pa_ratio)

            pdf.image("rhizo_muc_vs_pen_asper.png", x=10, y=None, w=100)
            pdf.ln(10)

            pdf.add_page()
            pdf.image("mold_ratios_histogram.png", x=20, y=None, w=140)
            if len(both_ratios_flat) > 1:
                pdf.cell(200, 10, txt=f"        Largest Ratio   = {both_ratios_flat_max:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"        Smallest Ratio  = {both_ratios_flat_min:.2f}%", ln=True)
                if len(both_ratios_flat) > 2:
                    pdf.cell(200, 10, txt=f"        Average Ratio   = {both_ratios_flat_avg:.2f}%", ln=True)
            else:
                pdf.cell(200, 10, txt=f"        Ratio   = {both_ratios_flat_max:.2f}%", ln=True)
            pdf.add_page()
            pdf.image("rm_ratios_histogram.png", x=20, y=None, w=140)
            if len(rm_ratio) > 1:
                pdf.cell(200, 10, txt=f"        Largest Ratio   = {rm_ratio_max:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"        Smallest Ratio  = {rm_ratio_min:.2f}%", ln=True)
                if len(rm_ratio) > 2:
                    pdf.cell(200, 10, txt=f"        Average Ratio   = {rm_ratio_avg:.2f}%", ln=True)
            else:
                pdf.cell(200, 10, txt=f"        Ratio   = {rm_ratio_max:.2f}%", ln=True)
            pdf.add_page()
            pdf.image("pa_ratios_histogram.png", x=20, y=None, w=140)
            if len(pa_ratio) > 1:
                pdf.cell(200, 10, txt=f"        Largest Ratio   = {pa_ratio_max:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"        Smallest Ratio  = {pa_ratio_min:.2f}%", ln=True)
                if len(pa_ratio) > 2:
                    pdf.cell(200, 10, txt=f"        Average Ratio   = {pa_ratio_avg:.2f}%", ln=True)
            else:
                pdf.cell(200, 10, txt=f"        Ratio   = {pa_ratio_max:.2f}%", ln=True)

        elif rhizo_muc and pen_asper > 0:
            first_growth1 = photo_date - timedelta(days=7)
            first_growth2 = first_growth1.strftime("%Y-%m-%d")
            pdf.cell(200, 10, txt=f"Detected Genus Groups and Amounts:", ln=True)
            pdf.cell(200, 10, txt=f"    - Rhizopus/Mucor         : {rhizo_muc}", ln=True)
            pdf.cell(200, 10, txt=f"    - Penicillium/Aspergillus: {pen_asper}", ln=True)
            self.generate_pie_chart_both_but_separate(rhizo_muc, pen_asper)
            self.generate_ratio_chart_both()
            self.generate_ratio_chart_rm()
            self.generate_ratio_chart_pa()

            pdf.image("rhizo_muc_vs_pen_asper.png", x=10, y=None, w=100)
            pdf.ln(10)

            # retrieve all ratios using the updated method
            all_ratios = detections_manager.get_all_ratios()

            # prepare to aggregate mold ratios by mold type
            both_ratios = {2: [], 3: []}  # dictionary to store ratios for mold types 2 and 3
            for result in all_ratios:
                image_name = result[0]
                cleanOrMoldy = result[1]
                mold_data = result[2:]
                # only consider results if the bread is moldy (class not equal to 0)
                if cleanOrMoldy != 0:
                    for mold_type, total_ratio in mold_data:
                        if mold_type in both_ratios:
                            # to turn it into a more easily understandable percentage
                            both_ratios[mold_type].append(total_ratio * 100)
            # flatten the lists of ratios for each mold type
            both_ratios_flat = [ratio for ratios in both_ratios.values() for ratio in ratios]
            both_ratios_flat_max = max(both_ratios_flat)
            both_ratios_flat_min = min(both_ratios_flat)
            both_ratios_flat_avg = sum(both_ratios_flat) / len(both_ratios_flat)

            rm_ratio = []  # List to store ratios for Rhizopus/Mucor (mold type 2)
            for result in all_ratios:
                cleanOrMoldy = result[1]
                mold_data = result[2:]
                # only consider results if the bread is moldy (class not equal to 0)
                if cleanOrMoldy != 0:
                    for mold_type, total_ratio in mold_data:
                        if mold_type == 2:  # only process rhizopus-mucor
                            # to turn it into a more easily understandable percentage
                            rm_ratio.append(total_ratio * 100)
            rm_ratio_max = max(rm_ratio)
            rm_ratio_min = min(rm_ratio)
            rm_ratio_avg = sum(rm_ratio) / len(rm_ratio)

            pa_ratio = []  # list to store ratios for Rhizopus/Mucor (mold type 2)
            for result in all_ratios:
                cleanOrMoldy = result[1]
                mold_data = result[2:]
                # only consider results if the bread is moldy (class not equal to 0)
                if cleanOrMoldy != 0:
                    for mold_type, total_ratio in mold_data:
                        if mold_type == 3:  # only process penicillium-aspergillus
                            # to turn it into a more easily understandable percentage
                            pa_ratio.append(total_ratio * 100)
            pa_ratio_max = max(pa_ratio)
            pa_ratio_min = min(pa_ratio)
            pa_ratio_avg = sum(pa_ratio) / len(pa_ratio)

            pdf.add_page()
            pdf.image("mold_ratios_histogram.png", x=20, y=None, w=140)
            if len(both_ratios_flat) > 1:
                pdf.cell(200, 10, txt=f"        Largest Ratio   = {both_ratios_flat_max:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"        Smallest Ratio  = {both_ratios_flat_min:.2f}%", ln=True)
                if len(both_ratios_flat) > 2:
                    pdf.cell(200, 10, txt=f"        Average Ratio   = {both_ratios_flat_avg:.2f}%", ln=True)
            else:
                pdf.cell(200, 10, txt=f"        Ratio   = {both_ratios_flat_max:.2f}%", ln=True)
            pdf.add_page()
            pdf.image("rm_ratios_histogram.png", x=20, y=None, w=140)
            if len(rm_ratio) > 1:
                pdf.cell(200, 10, txt=f"        Largest Ratio   = {rm_ratio_max:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"        Smallest Ratio  = {rm_ratio_min:.2f}%", ln=True)
                if len(rm_ratio) > 2:
                    pdf.cell(200, 10, txt=f"        Average Ratio   = {rm_ratio_avg:.2f}%", ln=True)
            else:
                pdf.cell(200, 10, txt=f"        Ratio   = {rm_ratio_max:.2f}%", ln=True)
            pdf.add_page()
            pdf.image("pa_ratios_histogram.png", x=20, y=None, w=140)
            if len(pa_ratio) > 1:
                pdf.cell(200, 10, txt=f"        Largest Ratio   = {pa_ratio_max:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"        Smallest Ratio  = {pa_ratio_min:.2f}%", ln=True)
                if len(pa_ratio) > 2:
                    pdf.cell(200, 10, txt=f"        Average Ratio   = {pa_ratio_avg:.2f}%", ln=True)
            else:
                pdf.cell(200, 10, txt=f"        Ratio   = {pa_ratio_max:.2f}%", ln=True)

        elif rhizo_muc > 0:
            first_growth1 = photo_date - timedelta(days=3)
            first_growth2 = first_growth1.strftime("%Y-%m-%d")
            pdf.cell(200, 10, txt=f"Detected Genus Group and Amount:", ln=True)
            pdf.cell(200, 10, txt=f"    - Rhizopus/Mucor            : {rhizo_muc}", ln=True)
            self.generate_ratio_chart_rm()
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Initial Growth Start: {first_growth2}", ln=True)

            # retrieve all ratios using the updated method
            all_ratios = detections_manager.get_all_ratios()

            rm_ratio = []  # List to store ratios for Rhizopus/Mucor (mold type 2)
            for result in all_ratios:
                cleanOrMoldy = result[1]
                mold_data = result[2:]
                # only consider results if the bread is moldy (class not equal to 0)
                if cleanOrMoldy != 0:
                    for mold_type, total_ratio in mold_data:
                        if mold_type == 2:  # only process rhizopus-mucor
                            # to turn it into a more easily understandable percentage
                            rm_ratio.append(total_ratio * 100)
            rm_ratio_max = max(rm_ratio)
            rm_ratio_min = min(rm_ratio)
            rm_ratio_avg = sum(rm_ratio) / len(rm_ratio)

            pdf.add_page()
            pdf.image("rm_ratios_histogram.png", x=20, y=None, w=140)
            if len(rm_ratio) > 1:
                pdf.cell(200, 10, txt=f"        Largest Ratio   = {rm_ratio_max:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"        Smallest Ratio  = {rm_ratio_min:.2f}%", ln=True)
                if len(rm_ratio) > 2:
                    pdf.cell(200, 10, txt=f"        Average Ratio   = {rm_ratio_avg:.2f}%", ln=True)
            else:
                pdf.cell(200, 10, txt=f"        Ratio   = {rm_ratio_max:.2f}%", ln=True)
        elif pen_asper > 0:
            first_growth1 = photo_date - timedelta(days=7)
            first_growth2 = first_growth1.strftime("%Y-%m-%d")
            pdf.cell(200, 10, txt=f"Detected Genus Group and Amount:", ln=True)
            pdf.cell(200, 10, txt=f"    - Penicillium/Aspergillus   : {pen_asper}", ln=True)
            self.generate_ratio_chart_pa()
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Initial Growth Start: {first_growth2}", ln=True)

            all_ratios = detections_manager.get_all_ratios()

            pa_ratio = []  # list to store ratios for Rhizopus/Mucor (mold type 2)
            for result in all_ratios:
                cleanOrMoldy = result[1]
                mold_data = result[2:]
                # only consider results if the bread is moldy (class not equal to 0)
                if cleanOrMoldy != 0:
                    for mold_type, total_ratio in mold_data:
                        if mold_type == 3:  # only process penicillium-aspergillus
                            # to turn it into a more easily understandable percentage
                            pa_ratio.append(total_ratio * 100)
            pa_ratio_max = max(pa_ratio)
            pa_ratio_min = min(pa_ratio)
            pa_ratio_avg = sum(pa_ratio) / len(pa_ratio)

            pdf.add_page()
            pdf.image("pa_ratios_histogram.png", x=20, y=None, w=140)
            if len(pa_ratio) > 1:
                pdf.cell(200, 10, txt=f"        Largest Ratio   = {pa_ratio_max:.2f}%", ln=True)
                pdf.cell(200, 10, txt=f"        Smallest Ratio  = {pa_ratio_min:.2f}%", ln=True)
                if len(pa_ratio) > 2:
                    pdf.cell(200, 10, txt=f"        Average Ratio   = {pa_ratio_avg:.2f}%", ln=True)
            else:
                pdf.cell(200, 10, txt=f"        Ratio   = {pa_ratio_max:.2f}%", ln=True)
        else:
            pdf.cell(200, 10, txt=f"If you are seeing this then there's an error in the mold count :[", ln=True)

        # generate and include ratio charts
        # pdf.add_page()
        # generate_ratio_chart_both()
        # pdf.image("mold_ratio_distribution.png", x=10, y=None, w=100)

        # save the pdf
        pdf_output_path = f"{result_folder}/ReportSummary_{now_date2}.pdf"
        pdf.output(pdf_output_path)
        return pdf_output_path


    def generate_pie_chart_breads(self, clean_breads, moldy_breads):
        labels = "Clean Bread", "Moldy Bread"
        sizes = [clean_breads, moldy_breads]
        colors = ["pink", "violet"]
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
        plt.axis("equal")
        plt.savefig("moldy_vs_clean.png")


    def generate_pie_chart_both(self, rhizo_muc, pen_asper, both_groups):
        if both_groups > 0:
            labels = "Rhizopus/Mucor", "Penicillium/Aspergillus", "Both Genus Groups"
            sizes = [rhizo_muc, pen_asper, both_groups]
            colors = ["aqua", "springgreen", "navajowhite"]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
            plt.axis("equal")
            plt.savefig("rhizo_muc_vs_pen_asper.png")
        else:
            labels = "Rhizopus/Mucor", "Penicillium/Aspergillus"
            sizes = [rhizo_muc, pen_asper]
            colors = ["aqua", "springgreen"]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
            plt.axis("equal")
            plt.savefig("rhizo_muc_vs_pen_asper.png")


    def generate_pie_chart_both_but_separate(self, rhizo_muc, pen_asper):
        labels = "Rhizopus/Mucor", "Penicillium/Aspergillus"
        sizes = [rhizo_muc, pen_asper]
        colors = ["aqua", "springgreen"]
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
        plt.axis("equal")
        plt.savefig("rhizo_muc_vs_pen_asper.png")


    def generate_ratio_chart_both(self):
        # retrieve all ratios using the updated method
        all_ratios = detections_manager.get_all_ratios()

        # prepare to aggregate mold ratios by mold type
        mold_ratios = {2: [], 3: []}  # dictionary to store ratios for mold types 2 and 3

        for result in all_ratios:
            image_name = result[0]
            cleanOrMoldy = result[1]
            mold_data = result[2:]

            # only consider results if the bread is moldy (class not equal to 0)
            if cleanOrMoldy != 0:
                for mold_type, total_ratio in mold_data:
                    if mold_type in mold_ratios:
                        # to turn it into a more easily understandable percentage
                        mold_ratios[mold_type].append(total_ratio * 100)

        # flatten the lists of ratios for each mold type
        mold_ratios_flat = [ratio for ratios in mold_ratios.values() for ratio in ratios]

        # generate histogram with bins ranging from 0 to 1 in increments of 0.1
        plt.figure(figsize=(6, 10))
        plt.hist(mold_ratios_flat, bins=range(0, 101, 1), edgecolor="black", orientation="horizontal")  # Bins from 0 to 1 in increments of 0.1
        plt.xlabel("Frequency")
        plt.ylabel("Mold Size to Bread Ratio")
        plt.title("Histogram of Mold Size Ratios for Both Genus Groups")
        plt.grid(True)
        plt.tight_layout()

        # save the histogram as an image
        plt.savefig("mold_ratios_histogram.png")
        plt.close()



    def generate_ratio_chart_rm(self):
        # retrieve all ratios using the updated method
        all_ratios = detections_manager.get_all_ratios()

        # prepare to aggregate mold ratios specifically for Rhizopus/Mucor (class ID 2)
        rm_ratios = []  # List to store ratios for Rhizopus/Mucor (mold type 2)

        for result in all_ratios:
            image_name = result[0]
            cleanOrMoldy = result[1]
            mold_data = result[2:]

            # only consider results if the bread is moldy (class not equal to 0)
            if cleanOrMoldy != 0:
                for mold_type, total_ratio in mold_data:
                    if mold_type == 2:  # only process rhizopus-mucor
                        # to turn it into a more easily understandable percentage
                        rm_ratios.append(total_ratio * 100)

        # generate histogram with bins ranging from 0 to 1 in increments of 0.1
        plt.figure(figsize=(6, 10))
        # bins from 0 to 1 in increments of 0.1
        plt.hist(rm_ratios, bins=range(0, 101, 1), edgecolor="black", orientation="horizontal")
        plt.xlabel("Frequency")
        plt.ylabel("Mold Size to Bread Ratio")
        plt.title("Histogram of Mold Size Ratios for Rhizopus/Mucor")
        plt.grid(True)
        plt.tight_layout()

        # save the histogram as an image
        plt.savefig("rm_ratios_histogram.png")
        plt.close()


    def generate_ratio_chart_pa(self):
        # retrieve all ratios using the updated method
        all_ratios = detections_manager.get_all_ratios()

        # prepare to aggregate mold ratios specifically for penicillium-aspergillus (class ID 2)
        pa_ratios = []  # list to store ratios for Rhizopus/Mucor (mold type 2)

        for result in all_ratios:
            image_name = result[0]
            cleanOrMoldy = result[1]
            mold_data = result[2:]

            # only consider results if the bread is moldy (class not equal to 0)
            if cleanOrMoldy != 0:
                for mold_type, total_ratio in mold_data:
                    if mold_type == 3:  # only process penicillium-aspergillus
                        # to turn it into a more easily understandable percentage
                        pa_ratios.append(total_ratio * 100)

        # generate histogram with bins ranging from 0 to 1 in increments of 0.1
        plt.figure(figsize=(6, 10))
        # bins from 0 to 1 in increments of 0.1
        plt.hist(pa_ratios, bins=range(0, 101, 1), edgecolor="black", orientation="horizontal")
        plt.xlabel("Frequency")
        plt.ylabel("Mold Size to Bread Ratio")
        plt.title("Histogram of Mold Size Ratios for Penicillium/Aspergillus")
        plt.grid(True)
        plt.tight_layout()

        # save the histogram as an image
        plt.savefig("pa_ratios_histogram.png")
        plt.close()

