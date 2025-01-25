import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from Bio import SeqIO
import pysam
import subprocess
import concurrent.futures as cf
import random
from collections import OrderedDict
import subprocess
import os
import sys


def get_cli_output_lines(commands, side_effect = False):
    if side_effect:
        ret = subprocess.call(commands, shell=True)
        return ret
    else:
        output_lines = subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.decode().split("\n")[0:-1]
        return output_lines


def get_file_lines(file):
    with open(file, "rt") as fin:
        lines = [ line.rstrip("\n") for line in fin.readlines() ]
    return lines


def replace_bait_id(genome, bait_path, out_path):
    records = list(SeqIO.parse(bait_path, "fasta"))
    count = 1
    fout = open(out_path, "wt") # genome + "_bait.fa"
    for record in records:
        ID = genome + "_" + str(count) + " [" + record.description + "]"
        count += 1
        print(">" + ID, file=fout)
        print(record.seq, file=fout)
    fout.close()


def get_subseq(ref, start, end, flank=0):
    subseq = ref[start-1:end]
    subseq_flank_start = start-1-flank
    subseq_flank_end = end+flank
    if subseq_flank_start < 0:
        subseq_flank_start = 0
    if subseq_flank_end > len(ref):
        subseq_flank_end = len(ref)
    subseq_flank = ref[subseq_flank_start:subseq_flank_end]
    return subseq, subseq_flank


def rotate_ref_to_non_repeat_region(genome, genome_fasta_path, soft_paths_dict, rotation=False):
    ref_records = list(SeqIO.parse(genome_fasta_path, "fasta"))
    if len(ref_records) != 1:
        print("Error: fasta has more than one record.")
        return
    commands = soft_paths_dict.get("blastn") + " -query " + genome_fasta_path + " -subject " + genome_fasta_path + " -outfmt 6"
    blastn_lines = get_cli_output_lines(commands, side_effect = False)
    repeat_pos_array = np.zeros(len(ref_records[0].seq), dtype=int)
    for line in blastn_lines[1:]: # skip the first line
        fields = line.split("\t")
        q_start = int(fields[6])
        q_end = int(fields[7])
        for i in range(q_start-1, q_end):
            repeat_pos_array[i] += 1
    if rotation:
        non_repeat_region_info = []
        while 0 in repeat_pos_array:
            non_repeat_region_info, repeat_pos_array = find_continous_zeros(non_repeat_region_info, repeat_pos_array)
            # find the largest non-repeat region
        non_repeat_region_info.sort(key=lambda x: x[2], reverse=True)
        non_start = non_repeat_region_info[0][0]
        non_end = non_repeat_region_info[0][1]
        length = non_repeat_region_info[0][2]
        rot_step = (non_end + non_start) // 2
        if length > 5000:
            print("The largest non-repeat region is " + str(length) + " bp long.")
            rotate_fasta(genome_fasta_path, genome + "_rotated_" + str(rot_step) + ".fasta", rot_step)
        else:
            print("The largest non-repeat region is less than 5 kb.")
        return rot_step
    else:
        return 0


def find_continous_zeros(info_list, repeat_pos_array):
    for i in range(0, len(repeat_pos_array)):
        if repeat_pos_array[i] == 0:
            piece_start = i
            piece_end = i
            repeat_pos_array[i] = 1
            break
    for i in range(piece_start+1, len(repeat_pos_array)):
        if repeat_pos_array[i] == 0:
            piece_end = i
            repeat_pos_array[i] = 1
            if i == len(repeat_pos_array) - 1:
                length = piece_end - piece_start + 1
                info_list.append((piece_start, piece_end, length))
                break
        else:
            length = piece_end - piece_start + 1
            info_list.append((piece_start, piece_end, length))
            break
    return info_list, repeat_pos_array


def rotate_fasta(genome_fasta_path, rotated_fasta_path, step):
    ref_records = list(SeqIO.parse(genome_fasta_path, "fasta"))
    if len(ref_records) != 1:
        print("Error: " + genome + "_bait.fa has more than one record.")
        return
    id = ref_records[0].id
    sequence = ref_records[0].seq
    if step > 0 and step < len(sequence):
        subseq_1 = sequence[step:]
        subseq_2 = sequence[0:step]
        rot_seq = subseq_1 + subseq_2
    elif step == 0:
        rot_seq = sequence
    elif step < 0:
        subseq_1 = sequence[:(len(sequence)+step)]
        subseq_2 = sequence[(len(sequence)+step):]
        rot_seq = subseq_2 + subseq_1
    else:
        print("Error: step must be greater than 0 and less than the length of the sequence.")
        return None
    with open(rotated_fasta_path, "wt") as fout:
        print(">" + id + " [rotation=" + str(step) + "]", file=fout)
        print(rot_seq, file=fout)


def get_fastq_stats(prefix, sample_fastq_path, soft_paths_dict, threads):
    # run seqkit stat
    commands = soft_paths_dict.get("seqkit") + " stat -a -T " + sample_fastq_path + " -j " + threads
    output_lines = get_cli_output_lines(commands)
    total_read_number = output_lines[1].split("\t")[3]
    total_bases = output_lines[1].split("\t")[4]
    # run seqkit fx2tab
    commands = soft_paths_dict.get("seqkit") + " fx2tab -j " + threads + " -qlni " + sample_fastq_path
    output_lines = get_cli_output_lines(commands) # ID, length, qual 
    length_list = [ int(line.split("\t")[1]) for line in output_lines ]
    qual_list = [ float(line.split("\t")[2]) for line in output_lines ]
    with open(prefix + "_id_length_qual.txt", "wt") as fout:
        for line in output_lines:
            fout.write(line + "\n")
    return length_list, qual_list, total_read_number, total_bases


def plot_length_qual(prefix, sample_platform, length_list, qual_list, total_read_number, total_bases):
    length_bin_dict = {
        "HiFi": (50000, 500),
        "CLR": (50000, 500),
        "ONT": (50000, 500),
        "ultra-long": (100000, 500),
        "Short": (500, 10),
    }
    # create a new plot
    fig = plt.figure(figsize=(10, 8))
    gs = gridspec.GridSpec(13, 2)
    ax1 = plt.subplot(gs[0:5, :])
    ax2 = plt.subplot(gs[7:12, :])
    axs = [ax1, ax2]
    # plot length distribution
    length_bins = np.arange(0, length_bin_dict.get(sample_platform)[0], length_bin_dict.get(sample_platform)[1])
    # plot in ax1
    axs[0].hist(length_list, bins=length_bins, color="blue", alpha=0.5, edgecolor="black", linewidth=0.5)
    axs[0].axvline(sum(length_list)/len(length_list), color="red", linestyle="--")
    axs[0].set_xlim([0, length_bin_dict.get(sample_platform)[0]])
    axs[0].grid(True, alpha=0.5)
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)
    axs[0].set_xlabel("Read Length")
    axs[0].set_ylabel("Counts")
    axs[0].set_title("total_read_number = " + total_read_number + "; total_bases = " + total_bases)
    axs[1].hist(qual_list, bins=np.arange(0, 100, 1), color="red", alpha=0.5, edgecolor="black", linewidth=0.5)
    axs[1].axvline(sum(qual_list)/len(qual_list), color="red", linestyle="--")
    axs[1].set_xlim([0, 100])
    axs[1].grid(True, alpha=0.5)
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['right'].set_visible(False)
    axs[1].set_xlabel("Read Quality")
    axs[1].set_ylabel("Counts")
    axs[1].set_title("total_read_number = " + total_read_number + "; total_bases = " + total_bases)
    plt.savefig(prefix + "_length_qual_distribution.pdf")


def filt_fastq_records(prefix, fastq_file, filt_length):
    records = list(SeqIO.parse(fastq_file, "fastq"))
    random.shuffle(records) # this is important
    pass_records = [ record for record in records if len(record.seq) >= filt_length ]
    fail_records = [ record for record in records if len(record.seq) < filt_length ]
    with open(prefix + "_fail_" + str(filt_length) + ".fastq", "wt") as fout:
        SeqIO.write(fail_records, fout, "fastq")
    with open("filt_" + str(filt_length) + ".fastq", "wt") as fout:
        SeqIO.write(pass_records, fout, "fastq")
    if os.path.exists("filt_" + str(filt_length) + ".fastq"):
        os.rename("filt_" + str(filt_length) + ".fastq", prefix + ".fastq")
    return


def split_mtpt_reads(sample_index, sample_fastq_path, sample_platform, mito_fa, plastid_fa, soft_paths_dict, threads):
    platform_dict = {
            "HiFi": "map-hifi",
            "CLR": "map-pb",
            "ONT": "map-ont",
            "ultra-long": "map-ont",
        }
    command_1 = soft_paths_dict.get("seqkit") + " seq -ni " + mito_fa + " > mito_ids.txt"
    command_2 = soft_paths_dict.get("seqkit") + " seq -ni " + plastid_fa + " > plastid_ids.txt"
    command_3 = "cat " + mito_fa + " " + plastid_fa + " > mtpt.fa"
    command_4 = soft_paths_dict.get("minimap2") + " -t " + threads + " -ax " + platform_dict.get(sample_platform) + " mtpt.fa " + sample_fastq_path
    command_5 = soft_paths_dict.get("samtools") + " view -Sb -F 4 -@ " + threads + " - "
    command_6 = soft_paths_dict.get("samtools") + " sort -@ " + threads + " - -o reads.sorted.bam"
    command_7 = soft_paths_dict.get("samtools") + " index reads.sorted.bam"
    command_8 = soft_paths_dict.get("bamtools") + " split -in reads.sorted.bam -reference"
    command_9 = "rm -rf mito.fastq plastid.fastq"
    command_10 = "cat mito_ids.txt | while read ID; do " + soft_paths_dict.get("samtools") + " fastq reads.sorted.REF_${ID}.bam -@ " + threads + " >> " + sample_index + "_mito.fastq; done"
    command_11 = "cat plastid_ids.txt | while read ID; do " + soft_paths_dict.get("samtools") + " fastq reads.sorted.REF_${ID}.bam -@ " + threads + " >> " + sample_index + "_plastid.fastq; done"
    command_12 = "rm -rf mito_ids.txt plastid_ids.txt mtpt.fa reads.sorted.bam reads.sorted.bam.bai reads.sorted.*.bam" 
    commands = command_1 + " ; " + command_2 + " ; " + command_3 + " ; " + command_4 + " | " + command_5 + " | " + command_6 + " && " + command_7 + " && " + command_8 + " ; " + command_9 + " ; " + command_10 + " ; " + command_11 + " ; " + command_12
    ret = get_cli_output_lines(commands, side_effect = True)
    return


def replace_reads_id(reads_file, new_reads_file):
    with open(reads_file, "rt") as fin:
        reads = list(SeqIO.parse(fin, "fasta"))
    with open(new_reads_file, "wt") as fout:
        for read in reads:
            read.id = read.id.replace("/", "_") # remove "/" in the reads id
            read.description = ""
            print(read.format("fasta"), file=fout)
    return new_reads_file


class Index_label_alignments():
    def __init__(self, blastn_alignments_lines):
        self.blastn_alignments_lines = blastn_alignments_lines
        self.blastn_index_label_alignments = self.index_label_alignments()
    
    def index_label_alignments(self):
        if len(self.blastn_alignments_lines) == 0:
            return []
        blastn_index_label_alignments = [ [i, 1, ";".join(self.blastn_alignments_lines[i].split("\t"))] for i in range(len(self.blastn_alignments_lines))]
        return blastn_index_label_alignments

    def get_sorted_one_alignments(self):
        one_alignments = []
        for i in range(len(self.blastn_index_label_alignments)):
            if self.blastn_index_label_alignments[i][1] == 1:
                one_alignments.append(self.blastn_index_label_alignments[i])
        one_alignments.sort(key=lambda x: int(x[2].split(";")[6]))
        return one_alignments

    def pop_contained_alignments(self):
        count = 0
        for i in range(len(self.blastn_index_label_alignments)):
            if self.blastn_index_label_alignments[i][1] == 1:
                i_start = int(self.blastn_index_label_alignments[i][2].split(";")[6])
                i_end = int(self.blastn_index_label_alignments[i][2].split(";")[7])
                for j in range(len(self.blastn_index_label_alignments)):
                    if j == i:
                        continue
                    if self.blastn_index_label_alignments[j][1] == 1:
                        j_start = int(self.blastn_index_label_alignments[j][2].split(";")[6])
                        j_end = int(self.blastn_index_label_alignments[j][2].split(";")[7])
                        if i_start <= j_start and j_end <= i_end:
                            self.blastn_index_label_alignments[j][1] = 0
                            count += 1
                        elif j_start <= i_start and i_end <= j_end:
                            self.blastn_index_label_alignments[i][1] = 0
                            count += 1
        return count


def run_blastn_sorter(read_ref_pair):
    soft_paths_dict = read_ref_pair[2]
    with open("tmp_blastn_results/" + read_ref_pair[0].id + ".fasta", "wt") as fout:
        print(read_ref_pair[0].format("fasta"), file=fout)
    q_len = len(read_ref_pair[0].seq)
    ref_records = list(SeqIO.parse(read_ref_pair[1], "fasta"))
    if len(ref_records) > 1:
        print("Warning: multiple records in reference file", file=sys.stderr)
    else:
        ref_length = len(ref_records[0].seq)
    command_1 = soft_paths_dict.get("blastn") + " -query tmp_blastn_results/" + read_ref_pair[0].id + ".fasta -subject " + read_ref_pair[1] + " -outfmt 6"
    blastn_alignments_lines = get_cli_output_lines(command_1, side_effect = False)
    if len(blastn_alignments_lines) == 0:
        with open("reads_with_no_alignments.txt", "at") as fout:
            print(read_ref_pair[0].id, file=fout)
    else:
        query_ref_index_label_alignments = Index_label_alignments(blastn_alignments_lines)
        count = 1
        while count > 0:
            count = query_ref_index_label_alignments.pop_contained_alignments()
        one_alignments = query_ref_index_label_alignments.get_sorted_one_alignments()
        to_print_1 = ""
        to_print_2 = ""
        # 0	1	ERR9808518.1002029;mito_1;98.724;12071;37;111;3;12027;87801;99800;0.0;21329
        # 1	1	ERR9808518.1002029;mito_1;99.269;7384;10;41;5672;13041;339447;332094;0.0;13296
        q_id = one_alignments[0][2].split(";")[0]
        s_id = one_alignments[0][2].split(";")[1]
        num_align = len(one_alignments)
        strand_list = [ "+" for i in range(num_align) ]
        percent_ident_list = [ 100 for i in range(num_align) ]
        qs_list = [ 1 for i in range(num_align) ]
        qe_list = [ 1 for i in range(num_align) ]
        ss_list = [ 1 for i in range(num_align) ]
        se_list = [ 1 for i in range(num_align) ]
        part_len_list = [ 1 for i in range(num_align) ]
        AO_len_list = [ 1 for i in range(num_align) ]
        copy_info_list = [ "" for i in range(num_align) ] # check for multiple mapping
        for i in range(num_align):
            align_info_fields = one_alignments[i][2].split(";")
            percent_ident_list[i] = float(align_info_fields[2])
            qs_list[i] = int(align_info_fields[6])
            qe_list[i] = int(align_info_fields[7])
            ss_list[i] = int(align_info_fields[8])
            se_list[i] = int(align_info_fields[9])
            part_len_list[i] = qe_list[i] - qs_list[i] + 1
            if ss_list[i] > se_list[i]:
                strand_list[i] = "-"
        for i in range(num_align):
            if (i+1) != num_align:
                AO_len_list[i] = qe_list[i] - qs_list[i+1] + 1
            else:
                AO_len_list[i] = "NA"
        percent_total = float((sum(part_len_list) - sum(AO_len_list[:-1])) / q_len * 100)
        # # check if the first and last alignment are cross the end of the reference
        # if strand_list[0] == "+" and strand_list[-1] == "+":
        #     if ss_list[-1] == 1 and se_list[0] == ref_length:
        #         if qe_list[0] + 1 == qs_list[-1]:
        #             AO_len_list[-1] = "cross"
        # elif strand_list[0] == "-" and strand_list[-1] == "-":
        #     if ss_list[-1] == ref_length and se_list[0] == 1:
        #         if qe_list[0] + 1 == qs_list[-1]:
        #             AO_len_list[-1] = "cross" 
        # # gather results
        aln_type = "aln_type=" + str(num_align) + ";"
        for i in range(num_align):
            if AO_len_list[i] == "NA":
                olp_type = "NA"
            # elif AO_len_list[i] == "cross":
            #     olp_type = "cross"
            elif type(AO_len_list[i]) == int:
                if AO_len_list[i] == 0:
                    olp_type = "ref"
                elif AO_len_list[i] > 0:
                    olp_type = "rep"
                elif AO_len_list[i] < 0:
                    olp_type = "ins"
            if i != (num_align - 1):
                aln_type += olp_type + ","
            else:
                aln_type += olp_type
        to_print_1 = "\t".join([q_id, s_id, str(q_len), aln_type, str(percent_total)])
        # check if each part is dual mapping
        for i in range(num_align):
            subseq, _ = get_subseq(read_ref_pair[0].seq, qs_list[i], qe_list[i], flank=0)
            with open("tmp_blastn_results/" + read_ref_pair[0].id + "_part_" + str(i) + ".fasta", "wt") as fout:
                print(">" + read_ref_pair[0].id + "_part_" + str(i), file=fout)
                print(subseq, file=fout)
            command_2 = soft_paths_dict.get("blastn") + " -query " + read_ref_pair[1] + " -subject tmp_blastn_results/" + read_ref_pair[0].id + "_part_" + str(i) + ".fasta -outfmt 6"
            blastn_alignments_lines_reverse = get_cli_output_lines(command_2, side_effect = False)
            ref_query_index_label_alignments = Index_label_alignments(blastn_alignments_lines_reverse)
            count = 1
            while count > 0:
                count = ref_query_index_label_alignments.pop_contained_alignments()
                one_alignments_reverse = ref_query_index_label_alignments.get_sorted_one_alignments()
            copy_num = 0
            for j in range(len(one_alignments_reverse)):
                align_info_fields = one_alignments_reverse[j][2].split(";")
                r_qs = int(align_info_fields[6])
                r_qe = int(align_info_fields[7])
                r_ss = int(align_info_fields[8])
                r_se = int(align_info_fields[9])
                if r_ss > r_se:
                    r_ss, r_se = r_se, r_ss
                offset_s = r_ss - 1
                offset_e = len(subseq) - r_se
                copy_percent = float((r_se - r_ss + 1) / len(subseq) * 100)
                if (copy_percent >= 90) and (offset_s <= 5) and (offset_e <= 5): # use 5 can lead to cn=0, but 0 is not a valid copy number
                    copy_num += 1
                    if copy_info_list[i] == "":
                        copy_info_list[i] = "c" + str(copy_num) + "=" + str(copy_percent) + "," + str(r_qs) + "," + str(r_qe)
                    else:
                        copy_info_list[i] = copy_info_list[i] + ";" + "c" + str(copy_num) + "=" + str(copy_percent) + "," + str(r_qs) + "," + str(r_qe)
            copy_info_list[i] = "cn=" + str(copy_num) + ";" + copy_info_list[i]
            if copy_info_list[i] == "cn=0;": # correct the copy number and copy info
                copy_info_list[i] = "cn=1;c1=" + str(percent_ident_list[i]) + "," + str(ss_list[i]) + "," + str(se_list[i])
            # gather results
            to_print_2 += "\taln=" + str(i+1) + ";len=" + str(part_len_list[i]) + ";olp=" + str(AO_len_list[i]) + ";idt=" + str(percent_ident_list[i]) + ";strand=" + strand_list[i] + ";qs=" + str(qs_list[i]) + ";qe=" + str(qe_list[i]) + ";ss=" + str(ss_list[i]) + ";se=" + str(se_list[i]) + ";" + copy_info_list[i]
        # print(results)
        with open("tmp_blastn_results/" + read_ref_pair[0].id + "_sorted_blastn_alignments.txt", "wt") as fout:
            print(to_print_1 + to_print_2, file=fout)
    command_1 = "rm tmp_blastn_results/" + read_ref_pair[0].id + ".fasta"
    command_2 = "rm tmp_blastn_results/" + read_ref_pair[0].id + "_part_*.fasta"
    command_3 = "cat tmp_blastn_results/" + read_ref_pair[0].id + "_sorted_blastn_alignments.txt >> all_sorted_blastn_alignments.txt"
    command_4 = "rm tmp_blastn_results/" + read_ref_pair[0].id + "_sorted_blastn_alignments.txt"
    commands = command_1 + ";" + command_2 + ";" + command_3 + ";" + command_4
    get_cli_output_lines(commands, side_effect = True)
    return


def get_type_and_subtype(blastn_info_file, default_num_types, out_dir="read_group_files"):
    blastn_results = get_file_lines(blastn_info_file)
    default_num_types = 5 # type_1,2,3,4,5 and other
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    for line in blastn_results:
        fields = line.split("\t")
        type_info = fields[3]
        aln_type, aln_subtype = type_info.split(";") # aln_type=4;rep,rep,rep,NA
        num_align = int(aln_type.split("=")[1])
        if num_align > default_num_types:
            with open(out_dir + "/other_blastn_results.txt", "at") as fout:
                print(line, file=fout)
        else:
            subtype = "_".join(aln_subtype.split(","))
            out_file = out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_blastn_results.txt"
            with open(out_file, "at") as fout:
                print(line, file=fout)


def check_FL_and_multi(blastn_info_file, default_num_types, out_dir="FL_read_group_files", id_dir="IDs", report_dir="Reports"):
    blastn_df = pd.read_table(blastn_info_file, header=None)
    # get the type and subtype
    type_info_list = list(set(blastn_df.iloc[:,3]))
    if len(type_info_list) == 1:
        type_info = type_info_list[0] # aln_type=1;NA
        aln_type, aln_subtype = type_info.split(";") # aln_type=4;rep,rep,rep,NA
        num_align = int(aln_type.split("=")[1])
        subtype = "_".join(aln_subtype.split(",")) # rep_rep_rep_NA
    else:
        print("Error: more than one type info in blastn file")
        for type_info in type_info_list:
            print(type_info)
        sys.exit(1)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    if not os.path.exists(id_dir):
        os.mkdir(id_dir)
    if not os.path.exists(report_dir):
        os.mkdir(report_dir)
    if num_align > default_num_types: # only check for type_1,2,3,4,5
        return
    count_FL = 0
    count_FL_multi = 0
    count_partial = 0
    for i in range(len(blastn_df)):
        read_id = blastn_df.iloc[i,0]
        percent_total = blastn_df.iloc[i,4]
        align_info_list_of_dict = list()
        for j in range(0,num_align):
            tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
            tmp_od = OrderedDict()
            for tmp_aln_info in tmp_aln_info_list:
                tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                tmp_od[tmp_aln_info_key] = tmp_aln_info_value
            align_info_list_of_dict.append(tmp_od)
        # check if the read is full length
        if percent_total >= 98: # get IDs of full length reads (98%) and partial reads
            with open(id_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_FL_ids.txt", "at") as fout:
                print(read_id, file=fout)
                count_FL += 1
            multi_flag = False
            for j in range(0,num_align):
                if int(align_info_list_of_dict[j]["cn"]) > 1:
                    multi_flag = True
                    break
            if multi_flag:
                with open(id_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_FL_multi_ids.txt", "at") as fout:
                    print(read_id, file=fout)
                    count_FL_multi += 1
        else:
            with open(id_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_partial_ids.txt", "at") as fout:
                print(read_id, file=fout)
                count_partial += 1
    # report the number of reads in each group
    with open(report_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_report.txt", "wt") as fout:
        print("FL", count_FL, sep="\t", file=fout)
        print("multiple mapping", count_FL_multi, sep="\t", file=fout)
        print("partial", count_partial, sep="\t", file=fout)
    # get the blastn info of full length reads from the original blastn file
    blastn_results = get_file_lines(blastn_info_file)
    with open(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_FL_blastn_results.txt", "wt") as fout:
        for i in range(len(blastn_results)):
            if float(blastn_results[i].split("\t")[4]) > 98:
                print(blastn_results[i], file=fout)


def get_next_groups(groups):
    next_groups = list()
    tmp_groups_ins = [["ins"] + group for group in groups]
    tmp_groups_ref = [["ref"] + group for group in groups]
    tmp_groups_rep = [["rep"] + group for group in groups]
    next_groups = tmp_groups_ins + tmp_groups_ref + tmp_groups_rep
    return next_groups


def match_se1_ss2(old_index, num_align, subtype, SE1, SS2, blastn_df, ID_subgroup_dir="ID_subgroup"):
    subgroup_df = pd.DataFrame(columns=["read_id", "olp_1", "strand_1", "ss_1", "se_1", "cn_1", "olp_2", "strand_2", "ss_2", "se_2", "cn_2"])
    subgroup_count = 0
    for i in range(len(blastn_df)):
        # parse the info
        read_id = blastn_df.iloc[i,0]
        align_info_list_of_dict = list()
        for j in range(0, num_align):
            tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
            tmp_od = OrderedDict()
            for tmp_aln_info in tmp_aln_info_list:
                tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                tmp_od[tmp_aln_info_key] = tmp_aln_info_value
            align_info_list_of_dict.append(tmp_od)
        # extract the info
        aln_len_1 = int(align_info_list_of_dict[0]["len"])
        olp_1 = align_info_list_of_dict[0]["olp"]
        idt_1 = float(align_info_list_of_dict[0]["idt"])
        strand_1 = align_info_list_of_dict[0]["strand"]
        ss_1 = int(align_info_list_of_dict[0]["ss"])
        se_1 = int(align_info_list_of_dict[0]["se"])
        cn_1 = int(align_info_list_of_dict[0]["cn"])
        aln_len_2 = int(align_info_list_of_dict[1]["len"])
        olp_2 = align_info_list_of_dict[1]["olp"] # NA
        idt_2 = float(align_info_list_of_dict[1]["idt"])
        strand_2 = align_info_list_of_dict[1]["strand"]
        ss_2 = int(align_info_list_of_dict[1]["ss"])
        se_2 = int(align_info_list_of_dict[1]["se"])
        cn_2 = int(align_info_list_of_dict[1]["cn"])
        # generate a new dataframe with columns: read_id, olp_1, ss_1, se_1, cn_1, olp_2, ss_2, se_2, cn_2 
        if se_1 == SE1 and ss_2 == SS2: # update the dataframe when se_1 == SE1 and ss_2 == SS2
            subgroup_df.loc[subgroup_count] = [read_id, olp_1, strand_1, ss_1, se_1, cn_1, olp_2, strand_2, ss_2, se_2, cn_2]
            subgroup_count += 1
    # analyze the dataframe, and write the info to a line in a combined summary dataframe
    fout_1 = open(ID_subgroup_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_subgroup_" + str(old_index) + "_FL_ids.txt", "wt")
    fout_2 = open(ID_subgroup_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_subgroup_" + str(old_index) + "_FL_multi_ids.txt", "wt")
    min_olp_1 = int(subgroup_df.iloc[0,1])
    mid_olp_1 = float(subgroup_df.iloc[0,1])
    max_olp_1 = int(subgroup_df.iloc[0,1])
    subgroup_count = len(subgroup_df)
    subgroup_multi_count = 0
    for i in range(len(subgroup_df)):
        # [read_id, olp_1, strand_1, ss_1, se_1, cn_1, olp_2, strand_2, ss_2, se_2, cn_2]
        read_id = subgroup_df.iloc[i,0]
        olp_1 = int(subgroup_df.iloc[i,1])
        strand_1 = subgroup_df.iloc[i,2]
        ss_1 = subgroup_df.iloc[i,3]
        se_1 = subgroup_df.iloc[i,4]
        cn_1 = subgroup_df.iloc[i,5]
        olp_2 = subgroup_df.iloc[i,6]
        strand_2 = subgroup_df.iloc[i,7]
        ss_2 = subgroup_df.iloc[i,8]
        se_2 = subgroup_df.iloc[i,9]
        cn_2 = subgroup_df.iloc[i,10]
        if olp_1 < min_olp_1:
            min_olp_1 = olp_1
        if olp_1 > max_olp_1:
            max_olp_1 = olp_1
        print(read_id, file=fout_1)
        if cn_1 > 1 or cn_2 > 1:
            subgroup_multi_count += 1
            print(read_id, file=fout_2)
    fout_1.close()
    fout_2.close()
    mid_olp_1 = (min_olp_1 + max_olp_1) / 2
    strand_1_most = subgroup_df["strand_1"].mode()[0]
    strand_2_most = subgroup_df["strand_2"].mode()[0]
    return min_olp_1, mid_olp_1, max_olp_1, strand_1_most, strand_2_most, subgroup_count, subgroup_multi_count


def match_se1_ss2_se2_ss3(old_index, num_align, subtype, SE1, SS2, SE2, SS3, blastn_df, ID_subgroup_dir="ID_subgroup"):
    subgroup_df = pd.DataFrame(columns=["read_id", "olp_1", "strand_1", "ss_1", "se_1", "cn_1", "olp_2", "strand_2", "ss_2", "se_2", "cn_2", "olp_3", "strand_3", "ss_3", "se_3", "cn_3"])
    subgroup_count = 0
    for i in range(len(blastn_df)):
        # parse the info
        read_id = blastn_df.iloc[i,0]
        align_info_list_of_dict = list()
        for j in range(0, num_align):
            tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
            tmp_od = OrderedDict()
            for tmp_aln_info in tmp_aln_info_list:
                tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                tmp_od[tmp_aln_info_key] = tmp_aln_info_value
            align_info_list_of_dict.append(tmp_od)
        # extract the info
        aln_len_1 = int(align_info_list_of_dict[0]["len"])
        olp_1 = align_info_list_of_dict[0]["olp"]
        idt_1 = float(align_info_list_of_dict[0]["idt"])
        strand_1 = align_info_list_of_dict[0]["strand"]
        ss_1 = int(align_info_list_of_dict[0]["ss"])
        se_1 = int(align_info_list_of_dict[0]["se"])
        cn_1 = int(align_info_list_of_dict[0]["cn"])
        aln_len_2 = int(align_info_list_of_dict[1]["len"])
        olp_2 = align_info_list_of_dict[1]["olp"] # NA
        idt_2 = float(align_info_list_of_dict[1]["idt"])
        strand_2 = align_info_list_of_dict[1]["strand"]
        ss_2 = int(align_info_list_of_dict[1]["ss"])
        se_2 = int(align_info_list_of_dict[1]["se"])
        cn_2 = int(align_info_list_of_dict[1]["cn"])
        aln_len_3 = int(align_info_list_of_dict[2]["len"])
        olp_3 = align_info_list_of_dict[2]["olp"]
        idt_3 = float(align_info_list_of_dict[2]["idt"])
        strand_3 = align_info_list_of_dict[2]["strand"]
        ss_3 = int(align_info_list_of_dict[2]["ss"])
        se_3 = int(align_info_list_of_dict[2]["se"])
        cn_3 = int(align_info_list_of_dict[2]["cn"])
        if se_1 == SE1 and ss_2 == SS2 and se_2 == SE2 and ss_3 == SS3: # update the dataframe when se_1 == SE1 and ss_2 == SS2 and se_2 == SE2 and ss_3 == SS3
            subgroup_df.loc[subgroup_count] = [read_id, olp_1, strand_1, ss_1, se_1, cn_1, olp_2, strand_2, ss_2, se_2, cn_2, olp_3, strand_3, ss_3, se_3, cn_3]
            subgroup_count += 1
    # analyze the dataframe, and write the info to a line in a combined summary dataframe
    fout_1 = open(ID_subgroup_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_subgroup_" + str(old_index) + "_FL_ids.txt", "wt")
    fout_2 = open(ID_subgroup_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_subgroup_" + str(old_index) + "_FL_multi_ids.txt", "wt")
    min_olp_1 = int(subgroup_df.iloc[0,1])
    mid_olp_1 = float(subgroup_df.iloc[0,1])
    max_olp_1 = int(subgroup_df.iloc[0,1])
    min_olp_2 = int(subgroup_df.iloc[0,5])
    mid_olp_2 = float(subgroup_df.iloc[0,5])
    max_olp_2 = int(subgroup_df.iloc[0,5])
    # ["read_id", "olp_1", "ss_1", "se_1", "cn_1", "olp_2", "ss_2", "se_2", "cn_2", "olp_3", "ss_3", "se_3", "cn_3"]
    subgroup_count = len(subgroup_df)
    subgroup_multi_count = 0
    for i in range(len(subgroup_df)):
        read_id = subgroup_df.iloc[i,0]
        olp_1 = int(subgroup_df.iloc[i,1])
        strand_1 = subgroup_df.iloc[i,2]
        ss_1 = subgroup_df.iloc[i,3]
        se_1 = subgroup_df.iloc[i,4]
        cn_1 = subgroup_df.iloc[i,5]
        olp_2 = int(subgroup_df.iloc[i,6])
        strand_2 = subgroup_df.iloc[i,7]
        ss_2 = subgroup_df.iloc[i,8]
        se_2 = subgroup_df.iloc[i,9]
        cn_2 = subgroup_df.iloc[i,10]
        olp_3 = subgroup_df.iloc[i,11]
        strand_3 = subgroup_df.iloc[i,12]
        ss_3 = subgroup_df.iloc[i,13]
        se_3 = subgroup_df.iloc[i,14]
        cn_3 = subgroup_df.iloc[i,15]
        if olp_1 < min_olp_1:
            min_olp_1 = olp_1
        if olp_1 > max_olp_1:
            max_olp_1 = olp_1
        if olp_2 < min_olp_2:
            min_olp_2 = olp_2
        if olp_2 > max_olp_2:
            max_olp_2 = olp_2
        print(read_id, file=fout_1)
        if cn_1 > 1 or cn_2 > 1 or cn_3 > 1:
            subgroup_multi_count += 1
            print(read_id, file=fout_2)
    fout_1.close()
    fout_2.close()
    mid_olp_1 = (min_olp_1 + max_olp_1) / 2
    mid_olp_2 = (min_olp_2 + max_olp_2) / 2
    strand_1_most = subgroup_df["strand_1"].mode()[0]
    strand_2_most = subgroup_df["strand_2"].mode()[0]
    strand_3_most = subgroup_df["strand_3"].mode()[0]
    return min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, strand_1_most, strand_2_most, strand_3_most, subgroup_count, subgroup_multi_count


def match_se1_ss2_se2_ss3_se3_ss4(old_index, num_align, subtype, SE1, SS2, SE2, SS3, SE3, SS4, blastn_df, ID_subgroup_dir="ID_subgroup"):
    subgroup_df = pd.DataFrame(columns=["read_id", "olp_1", "strand_1", "ss_1", "se_1", "cn_1", "olp_2", "strand_2", "ss_2", "se_2", "cn_2", "olp_3", "strand_3", "ss_3", "se_3", "cn_3", "olp_4", "strand_4", "ss_4", "se_4", "cn_4"])
    subgroup_count = 0
    for i in range(len(blastn_df)):
        # parse the info
        read_id = blastn_df.iloc[i,0]
        align_info_list_of_dict = list()
        for j in range(0, num_align):
            tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
            tmp_od = OrderedDict()
            for tmp_aln_info in tmp_aln_info_list:
                tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                tmp_od[tmp_aln_info_key] = tmp_aln_info_value
            align_info_list_of_dict.append(tmp_od)
        # extract the info
        aln_len_1 = int(align_info_list_of_dict[0]["len"])
        olp_1 = align_info_list_of_dict[0]["olp"]
        idt_1 = float(align_info_list_of_dict[0]["idt"])
        strand_1 = align_info_list_of_dict[0]["strand"]
        ss_1 = int(align_info_list_of_dict[0]["ss"])
        se_1 = int(align_info_list_of_dict[0]["se"])
        cn_1 = int(align_info_list_of_dict[0]["cn"])
        aln_len_2 = int(align_info_list_of_dict[1]["len"])
        olp_2 = align_info_list_of_dict[1]["olp"] # NA
        idt_2 = float(align_info_list_of_dict[1]["idt"])
        strand_2 = align_info_list_of_dict[1]["strand"]
        ss_2 = int(align_info_list_of_dict[1]["ss"])
        se_2 = int(align_info_list_of_dict[1]["se"])
        cn_2 = int(align_info_list_of_dict[1]["cn"])
        aln_len_3 = int(align_info_list_of_dict[2]["len"])
        olp_3 = align_info_list_of_dict[2]["olp"]
        idt_3 = float(align_info_list_of_dict[2]["idt"])
        strand_3 = align_info_list_of_dict[2]["strand"]
        ss_3 = int(align_info_list_of_dict[2]["ss"])
        se_3 = int(align_info_list_of_dict[2]["se"])
        cn_3 = int(align_info_list_of_dict[2]["cn"])
        aln_len_4 = int(align_info_list_of_dict[3]["len"])
        olp_4 = align_info_list_of_dict[3]["olp"]
        idt_4 = float(align_info_list_of_dict[3]["idt"])
        strand_4 = align_info_list_of_dict[3]["strand"]
        ss_4 = int(align_info_list_of_dict[3]["ss"])
        se_4 = int(align_info_list_of_dict[3]["se"])
        cn_4 = int(align_info_list_of_dict[3]["cn"])
        if se_1 == SE1 and ss_2 == SS2 and se_2 == SE2 and ss_3 == SS3 and se_3 == SE3 and ss_4 == SS4: # update the dataframe when se_1 == SE1 and ss_2 == SS2 and se_2 == SE2 and ss_3 == SS3 and se_3 == SE3 and ss_4 == SS4
            subgroup_df.loc[subgroup_count] = [read_id, olp_1, strand_1, ss_1, se_1, cn_1, olp_2, strand_2, ss_2, se_2, cn_2, olp_3, strand_3, ss_3, se_3, cn_3, olp_4, strand_4, ss_4, se_4, cn_4]
            subgroup_count += 1
    # analyze the dataframe, and write the info to a line in a combined summary dataframe
    fout_1 = open(ID_subgroup_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_subgroup_" + str(old_index) + "_FL_ids.txt", "wt")
    fout_2 = open(ID_subgroup_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_subgroup_" + str(old_index) + "_FL_multi_ids.txt", "wt")
    min_olp_1 = int(subgroup_df.iloc[0,1])
    mid_olp_1 = float(subgroup_df.iloc[0,1])
    max_olp_1 = int(subgroup_df.iloc[0,1])
    min_olp_2 = int(subgroup_df.iloc[0,5])
    mid_olp_2 = float(subgroup_df.iloc[0,5])
    max_olp_2 = int(subgroup_df.iloc[0,5])
    min_olp_3 = int(subgroup_df.iloc[0,9])
    mid_olp_3 = float(subgroup_df.iloc[0,9])
    max_olp_3 = int(subgroup_df.iloc[0,9])
    # ["read_id", "olp_1", "ss_1", "se_1", "cn_1", "olp_2", "ss_2", "se_2", "cn_2", "olp_3", "ss_3", "se_3", "cn_3", "olp_4", "ss_4", "se_4", "cn_4"]
    subgroup_count = len(subgroup_df)
    subgroup_multi_count = 0
    for i in range(len(subgroup_df)):
        read_id = subgroup_df.iloc[i,0]
        olp_1 = int(subgroup_df.iloc[i,1])
        strand_1 = subgroup_df.iloc[i,2]
        ss_1 = subgroup_df.iloc[i,3]
        se_1 = subgroup_df.iloc[i,4]
        cn_1 = subgroup_df.iloc[i,5]
        olp_2 = int(subgroup_df.iloc[i,6])
        strand_2 = subgroup_df.iloc[i,7]
        ss_2 = subgroup_df.iloc[i,8]
        se_2 = subgroup_df.iloc[i,9]
        cn_2 = subgroup_df.iloc[i,10]
        olp_3 = int(subgroup_df.iloc[i,11])
        strand_3 = subgroup_df.iloc[i,12]
        ss_3 = subgroup_df.iloc[i,13]
        se_3 = subgroup_df.iloc[i,14]
        cn_3 = subgroup_df.iloc[i,15]
        olp_4 = subgroup_df.iloc[i,16]
        strand_4 = subgroup_df.iloc[i,17]
        ss_4 = subgroup_df.iloc[i,18]
        se_4 = subgroup_df.iloc[i,19]
        cn_4 = subgroup_df.iloc[i,20]
        if olp_1 < min_olp_1:
            min_olp_1 = olp_1
        if olp_1 > max_olp_1:
            max_olp_1 = olp_1
        if olp_2 < min_olp_2:
            min_olp_2 = olp_2
        if olp_2 > max_olp_2:
            max_olp_2 = olp_2
        if olp_3 < min_olp_3:
            min_olp_3 = olp_3
        if olp_3 > max_olp_3:
            max_olp_3 = olp_3
        print(read_id, file=fout_1)
        if cn_1 > 1 or cn_2 > 1 or cn_3 > 1 or cn_4 > 1:
            subgroup_multi_count += 1
            print(read_id, file=fout_2)
    fout_1.close()
    fout_2.close()
    mid_olp_1 = (min_olp_1 + max_olp_1) / 2
    mid_olp_2 = (min_olp_2 + max_olp_2) / 2
    mid_olp_3 = (min_olp_3 + max_olp_3) / 2
    strand_1_most = subgroup_df["strand_1"].mode()[0]
    strand_2_most = subgroup_df["strand_2"].mode()[0]
    strand_3_most = subgroup_df["strand_3"].mode()[0]
    strand_4_most = subgroup_df["strand_4"].mode()[0]
    return min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, min_olp_3, mid_olp_3, max_olp_3, strand_1_most, strand_2_most, strand_3_most, strand_4_most, subgroup_count, subgroup_multi_count


def match_se1_ss2_se2_ss3_se3_ss4_se4_ss5(old_index, num_align, subtype, SE1, SS2, SE2, SS3, SE3, SS4, SE4, SS5, blastn_df, ID_subgroup_dir="ID_subgroup"):
    subgroup_df = pd.DataFrame(columns=["read_id", "olp_1", "strand_1", "ss_1", "se_1", "cn_1", "olp_2", "strand_2", "ss_2", "se_2", "cn_2", "olp_3", "strand_3", "ss_3", "se_3", "cn_3", "olp_4", "strand_4", "ss_4", "se_4", "cn_4", "olp_5", "strand_5", "ss_5", "se_5", "cn_5"])
    subgroup_count = 0
    for i in range(len(blastn_df)):
        # parse the info
        read_id = blastn_df.iloc[i,0]
        align_info_list_of_dict = list()
        for j in range(0, num_align):
            tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
            tmp_od = OrderedDict()
            for tmp_aln_info in tmp_aln_info_list:
                tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                tmp_od[tmp_aln_info_key] = tmp_aln_info_value
            align_info_list_of_dict.append(tmp_od)
        # extract the info
        aln_len_1 = int(align_info_list_of_dict[0]["len"])
        olp_1 = align_info_list_of_dict[0]["olp"]
        idt_1 = float(align_info_list_of_dict[0]["idt"])
        strand_1 = align_info_list_of_dict[0]["strand"]
        ss_1 = int(align_info_list_of_dict[0]["ss"])
        se_1 = int(align_info_list_of_dict[0]["se"])
        cn_1 = int(align_info_list_of_dict[0]["cn"])
        aln_len_2 = int(align_info_list_of_dict[1]["len"])
        olp_2 = align_info_list_of_dict[1]["olp"] # NA
        idt_2 = float(align_info_list_of_dict[1]["idt"])
        strand_2 = align_info_list_of_dict[1]["strand"]
        ss_2 = int(align_info_list_of_dict[1]["ss"])
        se_2 = int(align_info_list_of_dict[1]["se"])
        cn_2 = int(align_info_list_of_dict[1]["cn"])
        aln_len_3 = int(align_info_list_of_dict[2]["len"])
        olp_3 = align_info_list_of_dict[2]["olp"]
        idt_3 = float(align_info_list_of_dict[2]["idt"])
        strand_3 = align_info_list_of_dict[2]["strand"]
        ss_3 = int(align_info_list_of_dict[2]["ss"])
        se_3 = int(align_info_list_of_dict[2]["se"])
        cn_3 = int(align_info_list_of_dict[2]["cn"])
        aln_len_4 = int(align_info_list_of_dict[3]["len"])
        olp_4 = align_info_list_of_dict[3]["olp"]
        idt_4 = float(align_info_list_of_dict[3]["idt"])
        strand_4 = align_info_list_of_dict[3]["strand"]
        ss_4 = int(align_info_list_of_dict[3]["ss"])
        se_4 = int(align_info_list_of_dict[3]["se"])
        cn_4 = int(align_info_list_of_dict[3]["cn"])
        aln_len_5 = int(align_info_list_of_dict[4]["len"])
        olp_5 = align_info_list_of_dict[4]["olp"]
        idt_5 = float(align_info_list_of_dict[4]["idt"])
        strand_5 = align_info_list_of_dict[4]["strand"]
        ss_5 = int(align_info_list_of_dict[4]["ss"])
        se_5 = int(align_info_list_of_dict[4]["se"])
        cn_5 = int(align_info_list_of_dict[4]["cn"])
        if se_1 == SE1 and ss_2 == SS2 and se_2 == SE2 and ss_3 == SS3 and se_3 == SE3 and ss_4 == SS4 and se_4 == SE4 and ss_5 == SS5: # update the dataframe when se_1 == SE1 and ss_2 == SS2 and se_2 == SE2 and ss_3 == SS3 and se_3 == SE3 and ss_4 == SS4 and se_4 == SE4 and ss_5 == SS5
            subgroup_df.loc[subgroup_count] = [read_id, olp_1, strand_1, ss_1, se_1, cn_1, olp_2, strand_2, ss_2, se_2, cn_2, olp_3, strand_3, ss_3, se_3, cn_3, olp_4, strand_4, ss_4, se_4, cn_4, olp_5, strand_5, ss_5, se_5, cn_5]
            subgroup_count += 1
    # analyze the dataframe, and write the info to a line in a combined summary dataframe
    fout_1 = open(ID_subgroup_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_subgroup_" + str(old_index) + "_FL_ids.txt", "wt")
    fout_2 = open(ID_subgroup_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_subgroup_" + str(old_index) + "_FL_multi_ids.txt", "wt")
    min_olp_1 = int(subgroup_df.iloc[0,1])
    mid_olp_1 = float(subgroup_df.iloc[0,1])
    max_olp_1 = int(subgroup_df.iloc[0,1])
    min_olp_2 = int(subgroup_df.iloc[0,5])
    mid_olp_2 = float(subgroup_df.iloc[0,5])
    max_olp_2 = int(subgroup_df.iloc[0,5])
    min_olp_3 = int(subgroup_df.iloc[0,9])
    mid_olp_3 = float(subgroup_df.iloc[0,9])
    max_olp_3 = int(subgroup_df.iloc[0,9])
    min_olp_4 = int(subgroup_df.iloc[0,13])
    mid_olp_4 = float(subgroup_df.iloc[0,13])
    max_olp_4 = int(subgroup_df.iloc[0,13])
    # ["read_id", "olp_1", "ss_1", "se_1", "cn_1", "olp_2", "ss_2", "se_2", "cn_2", "olp_3", "ss_3", "se_3", "cn_3", "olp_4", "ss_4", "se_4", "cn_4", "olp_5", "ss_5", "se_5", "cn_5"]
    subgroup_count = len(subgroup_df)
    subgroup_multi_count = 0
    for i in range(len(subgroup_df)):
        read_id = subgroup_df.iloc[i,0]
        olp_1 = int(subgroup_df.iloc[i,1])
        strand_1 = subgroup_df.iloc[i,2]
        ss_1 = subgroup_df.iloc[i,3]
        se_1 = subgroup_df.iloc[i,4]
        cn_1 = subgroup_df.iloc[i,5]
        olp_2 = int(subgroup_df.iloc[i,6])
        strand_2 = subgroup_df.iloc[i,7]
        ss_2 = subgroup_df.iloc[i,8]
        se_2 = subgroup_df.iloc[i,9]
        cn_2 = subgroup_df.iloc[i,10]
        olp_3 = int(subgroup_df.iloc[i,11])
        strand_3 = subgroup_df.iloc[i,12]
        ss_3 = subgroup_df.iloc[i,13]
        se_3 = subgroup_df.iloc[i,14]
        cn_3 = subgroup_df.iloc[i,15]
        olp_4 = int(subgroup_df.iloc[i,16])
        strand_4 = subgroup_df.iloc[i,17]
        ss_4 = subgroup_df.iloc[i,18]
        se_4 = subgroup_df.iloc[i,19]
        cn_4 = subgroup_df.iloc[i,20]
        olp_5 = subgroup_df.iloc[i,21]
        strand_5 = subgroup_df.iloc[i,22]
        ss_5 = subgroup_df.iloc[i,23]
        se_5 = subgroup_df.iloc[i,24]
        cn_5 = subgroup_df.iloc[i,25]
        if olp_1 < min_olp_1:
            min_olp_1 = olp_1
        if olp_1 > max_olp_1:
            max_olp_1 = olp_1
        if olp_2 < min_olp_2:
            min_olp_2 = olp_2
        if olp_2 > max_olp_2:
            max_olp_2 = olp_2
        if olp_3 < min_olp_3:
            min_olp_3 = olp_3
        if olp_3 > max_olp_3:
            max_olp_3 = olp_3
        if olp_4 < min_olp_4:
            min_olp_4 = olp_4
        if olp_4 > max_olp_4:
            max_olp_4 = olp_4
        print(read_id, file=fout_1)
        if cn_1 > 1 or cn_2 > 1 or cn_3 > 1 or cn_4 > 1 or cn_5 > 1:
            subgroup_multi_count += 1
            print(read_id, file=fout_2)
    fout_1.close()
    fout_2.close()
    mid_olp_1 = (min_olp_1 + max_olp_1) / 2
    mid_olp_2 = (min_olp_2 + max_olp_2) / 2
    mid_olp_3 = (min_olp_3 + max_olp_3) / 2
    mid_olp_4 = (min_olp_4 + max_olp_4) / 2
    strand_1_most = subgroup_df["strand_1"].mode()[0]
    strand_2_most = subgroup_df["strand_2"].mode()[0]
    strand_3_most = subgroup_df["strand_3"].mode()[0]
    strand_4_most = subgroup_df["strand_4"].mode()[0]
    strand_5_most = subgroup_df["strand_5"].mode()[0]
    return min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, min_olp_3, mid_olp_3, max_olp_3, min_olp_4, mid_olp_4, max_olp_4, strand_1_most, strand_2_most, strand_3_most, strand_4_most, strand_5_most, subgroup_count, subgroup_multi_count


def get_subgroups(groups, num_align, input_dir="FL_read_group_files", out_dir="combined_excel", ID_subgroup_dir="ID_subgroup"):
    if not os.path.exists(ID_subgroup_dir):
        os.mkdir(ID_subgroup_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    for group in groups:
        subtype = "_".join(group)
        blastn_info_file = input_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_FL_blastn_results.txt"
        if os.path.exists(blastn_info_file) and os.path.getsize(blastn_info_file) > 0:
            blastn_df = pd.read_table(blastn_info_file, header=None)
            if num_align == 2:
                combine_df = pd.DataFrame(columns=["old_index", "(se1, ss2)", "strand_str", "min_olp_1", "mid_olp_1", "max_olp_1", "subgroup_count", "subgroup_multi_count"])
                all_se1_ss2 = set()
                for i in range(len(blastn_df)):
                    align_info_list_of_dict = list()
                    for j in range(0,num_align):
                        tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
                        tmp_od = OrderedDict()
                        for tmp_aln_info in tmp_aln_info_list:
                            tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                            tmp_od[tmp_aln_info_key] = tmp_aln_info_value
                        align_info_list_of_dict.append(tmp_od)
                    all_se1_ss2.add((int(align_info_list_of_dict[0]["se"]), int(align_info_list_of_dict[1]["ss"])))
                all_se1_ss2_list = list(all_se1_ss2)
                all_se1_ss2_list.sort(key=lambda x:x[0]) # sort by se1
                indexed_all_se1_ss2 = [ (i+1, se1_ss2) for i, se1_ss2 in enumerate(all_se1_ss2_list)]
                for item in indexed_all_se1_ss2: # (1, (89162, 73154))
                    old_index = item[0]
                    SE1 = item[1][0] # a int
                    SS2 = item[1][1]
                    min_olp_1, mid_olp_1, max_olp_1, strand_1_most, strand_2_most, subgroup_count, subgroup_multi_count = match_se1_ss2(old_index, num_align, subtype, SE1, SS2, blastn_df, ID_subgroup_dir="ID_subgroup")
                    # ["new_index", (se1, ss2), min_olp_1, mid_olp_1, max_olp_1, "subgroup_count", "subgroup_multi_count"]
                    # update the combined summary dataframe, pay attention to datatypes
                    strand_str = strand_1_most + "," + strand_2_most
                    combine_df.loc[old_index-1] = [old_index, item[1], strand_str, min_olp_1, mid_olp_1, max_olp_1, subgroup_count, subgroup_multi_count]
                combine_df.sort_values(by="mid_olp_1", ascending=False, inplace=True) # sort combine_df by mid_olp_1
                # write the combined summary dataframe to a excel file
                combine_df.to_excel(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_summary_anno.xlsx", index=False)
                combine_df.to_excel(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_summary_backup.xlsx", index=False)
            elif num_align == 3:
                # get all (se1, ss2, se2, ss3)
                combine_df = pd.DataFrame(columns=["old_index", "(se1, ss2, se2, ss3)", "strand_str", "min_olp_1", "mid_olp_1", "max_olp_1", "min_olp_2", "mid_olp_2", "max_olp_2", "subgroup_count", "subgroup_multi_count"])
                all_se1_ss2_se2_ss3 = set()
                for i in range(len(blastn_df)):
                    align_info_list_of_dict = list()
                    for j in range(0,num_align):
                        tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
                        tmp_od = OrderedDict()
                        for tmp_aln_info in tmp_aln_info_list:
                            tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                            tmp_od[tmp_aln_info_key] = tmp_aln_info_value
                        align_info_list_of_dict.append(tmp_od)
                    all_se1_ss2_se2_ss3.add((int(align_info_list_of_dict[0]["se"]), int(align_info_list_of_dict[1]["ss"]), int(align_info_list_of_dict[1]["se"]), int(align_info_list_of_dict[2]["ss"])))
                all_se1_ss2_se2_ss3_list = list(all_se1_ss2_se2_ss3)
                all_se1_ss2_se2_ss3_list.sort(key=lambda x:x[0]) # sort by se1
                indexed_all_se1_ss2_se2_ss3 = [ (i+1, se1_ss2_se2_ss3) for i, se1_ss2_se2_ss3 in enumerate(all_se1_ss2_se2_ss3_list)]
                for item in indexed_all_se1_ss2_se2_ss3: # (1, (89162, 73154, 89162, 73154))
                    old_index = item[0]
                    SE1 = item[1][0] # a int
                    SS2 = item[1][1]
                    SE2 = item[1][2]
                    SS3 = item[1][3]
                    min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, strand_1_most, strand_2_most, strand_3_most, subgroup_count, subgroup_multi_count = match_se1_ss2_se2_ss3(old_index, num_align, subtype, SE1, SS2, SE2, SS3, blastn_df, ID_subgroup_dir="ID_subgroup")
                    # update the combined summary dataframe, pay attention to datatypes
                    strand_str = strand_1_most + "," + strand_2_most + "," + strand_3_most
                    combine_df.loc[old_index-1] = [old_index, item[1], strand_str, min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, subgroup_count, subgroup_multi_count]
                combine_df.sort_values(by=["mid_olp_1", "mid_olp_2"], ascending=False, inplace=True) # sort combine_df by mid_olp_1 and mid_olp_2
                # write the combined summary dataframe to a excel file
                combine_df.to_excel(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_summary_anno.xlsx", index=False)
                combine_df.to_excel(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_summary_backup.xlsx", index=False)
            elif num_align == 4:
                # get all (se1, ss2, se2, ss3, se3, ss4)
                combine_df = pd.DataFrame(columns=["old_index", "(se1, ss2, se2, ss3)", "strand_str", "min_olp_1", "mid_olp_1", "max_olp_1", "min_olp_2", "mid_olp_2", "max_olp_2", "min_olp_3", "mid_olp_3", "max_olp_3", "subgroup_count", "subgroup_multi_count"])
                all_se1_ss2_se2_ss3_se3_ss4 = set()
                for i in range(len(blastn_df)):
                    align_info_list_of_dict = list()
                    for j in range(0,num_align):
                        tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
                        tmp_od = OrderedDict()
                        for tmp_aln_info in tmp_aln_info_list:
                            tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                            tmp_od[tmp_aln_info_key] = tmp_aln_info_value
                        align_info_list_of_dict.append(tmp_od)
                    all_se1_ss2_se2_ss3_se3_ss4.add((int(align_info_list_of_dict[0]["se"]), int(align_info_list_of_dict[1]["ss"]), int(align_info_list_of_dict[1]["se"]), int(align_info_list_of_dict[2]["ss"]), int(align_info_list_of_dict[2]["se"]), int(align_info_list_of_dict[3]["ss"])))
                all_se1_ss2_se2_ss3_se3_ss4_list = list(all_se1_ss2_se2_ss3_se3_ss4)
                all_se1_ss2_se2_ss3_se3_ss4_list.sort(key=lambda x:x[0]) # sort by se1
                indexed_all_se1_ss2_se2_ss3_se3_ss4 = [ (i+1, se1_ss2_se2_ss3_se3_ss4) for i, se1_ss2_se2_ss3_se3_ss4 in enumerate(all_se1_ss2_se2_ss3_se3_ss4_list)]
                for item in indexed_all_se1_ss2_se2_ss3_se3_ss4: # (1, (89162, 73154, 89162, 73154, 89162, 73154))
                    old_index = item[0]
                    SE1 = item[1][0] # a int
                    SS2 = item[1][1]
                    SE2 = item[1][2]
                    SS3 = item[1][3]
                    SE3 = item[1][4]
                    SS4 = item[1][5]
                    min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, min_olp_3, mid_olp_3, max_olp_3, strand_1_most, strand_2_most,strand_3_most, strand_4_most, subgroup_count, subgroup_multi_count = match_se1_ss2_se2_ss3_se3_ss4(old_index, num_align, subtype, SE1, SS2, SE2, SS3, SE3, SS4, blastn_df, ID_subgroup_dir="ID_subgroup")
                    # update the combined summary dataframe, pay attention to datatypes
                    strand_str = strand_1_most + "," + strand_2_most + "," + strand_3_most + "," + strand_4_most
                    combine_df.loc[old_index-1] = [old_index, item[1], strand_str, min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, min_olp_3, mid_olp_3, max_olp_3, subgroup_count, subgroup_multi_count]
                combine_df.sort_values(by=["mid_olp_1", "mid_olp_2", "mid_olp_3"], ascending=False, inplace=True) # sort combine_df by mid_olp_1 and mid_olp_2 and mid_olp_3
                # write the combined summary dataframe to a excel file
                combine_df.to_excel(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_summary_anno.xlsx", index=False)
                combine_df.to_excel(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_summary_backup.xlsx", index=False)
            elif num_align == 5:
                # get all (se1, ss2, se2, ss3, se3, ss4, se4, ss5)
                combine_df = pd.DataFrame(columns=["old_index", "(se1, ss2, se2, ss3)", "strand_str", "min_olp_1", "mid_olp_1", "max_olp_1", "min_olp_2", "mid_olp_2", "max_olp_2", "min_olp_3", "mid_olp_3", "max_olp_3", "min_olp_4", "mid_olp_4", "max_olp_4", "subgroup_count", "subgroup_multi_count"])
                all_se1_ss2_se2_ss3_se3_ss4_se4_ss5 = set()
                for i in range(len(blastn_df)):
                    align_info_list_of_dict = list()
                    for j in range(0,num_align):
                        tmp_aln_info_list = blastn_df.iloc[i,5+j].split(";") # ['aln=1', 'len=16011', 'olp=NA', 'idt=99.975', 'strand=+', 'qs=1', 'qe=16011', 'ss=73154', 'se=89162', 'cn=1', 'c1=100.0,73154,89162']
                        tmp_od = OrderedDict()
                        for tmp_aln_info in tmp_aln_info_list:
                            tmp_aln_info_key, tmp_aln_info_value = tmp_aln_info.split("=")
                            tmp_od[tmp_aln_info_key] = tmp_aln_info_value
                        align_info_list_of_dict.append(tmp_od)
                    all_se1_ss2_se2_ss3_se3_ss4_se4_ss5.add((int(align_info_list_of_dict[0]["se"]), int(align_info_list_of_dict[1]["ss"]), int(align_info_list_of_dict[1]["se"]), int(align_info_list_of_dict[2]["ss"]), int(align_info_list_of_dict[2]["se"]), int(align_info_list_of_dict[3]["ss"]), int(align_info_list_of_dict[3]["se"]), int(align_info_list_of_dict[4]["ss"])))
                all_se1_ss2_se2_ss3_se3_ss4_se4_ss5_list = list(all_se1_ss2_se2_ss3_se3_ss4_se4_ss5)
                all_se1_ss2_se2_ss3_se3_ss4_se4_ss5_list.sort(key=lambda x:x[0]) # sort by se1
                indexed_all_se1_ss2_se2_ss3_se3_ss4_se4_ss5 = [ (i+1, se1_ss2_se2_ss3_se3_ss4_se4_ss5) for i, se1_ss2_se2_ss3_se3_ss4_se4_ss5 in enumerate(all_se1_ss2_se2_ss3_se3_ss4_se4_ss5_list)]
                for item in indexed_all_se1_ss2_se2_ss3_se3_ss4_se4_ss5: # (1, (89162, 73154, 89162, 73154, 89162, 73154, 89162, 73154))
                    old_index = item[0]
                    SE1 = item[1][0] # a int
                    SS2 = item[1][1]
                    SE2 = item[1][2]
                    SS3 = item[1][3]
                    SE3 = item[1][4]
                    SS4 = item[1][5]
                    SE4 = item[1][6]
                    SS5 = item[1][7]
                    min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, min_olp_3, mid_olp_3, max_olp_3, min_olp_4, mid_olp_4, max_olp_4, strand_1_most, strand_2_most,strand_3_most, strand_4_most, strand_5_most, subgroup_count, subgroup_multi_count = match_se1_ss2_se2_ss3_se3_ss4_se4_ss5(old_index, num_align, subtype, SE1, SS2, SE2, SS3, SE3, SS4, SE4, SS5, blastn_df, ID_subgroup_dir="ID_subgroup")
                    # update the combined summary dataframe, pay attention to datatypes
                    strand_str = strand_1_most + "," + strand_2_most + "," + strand_3_most + "," + strand_4_most + "," + strand_5_most
                    combine_df.loc[old_index-1] = [old_index, item[1], strand_str, min_olp_1, mid_olp_1, max_olp_1, min_olp_2, mid_olp_2, max_olp_2, min_olp_3, mid_olp_3, max_olp_3, min_olp_4, mid_olp_4, max_olp_4, subgroup_count, subgroup_multi_count]
                combine_df.sort_values(by=["mid_olp_1", "mid_olp_2", "mid_olp_3", "mid_olp_4"], ascending=False, inplace=True) # sort combine_df by mid_olp_1 and mid_olp_2 and mid_olp_3 and mid_olp_4
                # write the combined summary dataframe to a excel file
                combine_df.to_excel(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_summary_anno.xlsx", index=False)
                combine_df.to_excel(out_dir + "/type_" + str(num_align) + "_subtype_" + subtype + "_summary_backup.xlsx", index=False)
    return


def plot_bubble_type_2_rep_raw(table_file, IDs_dir, ref_fasta):
    if os.path.exists(table_file):
        df = pd.read_excel(table_file, sheet_name='Sheet1') 
    else:
        return
    FL_ids_files = [IDs_dir + "/" + file for file in os.listdir(IDs_dir) if file.endswith("_FL_ids.txt")]
    FL_count = 0
    for file in FL_ids_files:
        FL_count += len(get_file_lines(file))
    ref_len = len(SeqIO.read(ref_fasta, "fasta").seq) # mito_rotated_flye_polish_1.fasta
    df['subgroup_count_norm'] = df['subgroup_count'] / FL_count * 10000  # normalize to 10000 FL reads
    fig = plt.figure(figsize=(10, 10)) # set figure size with
    df["color"] = df["mid_olp_1"].apply(lambda x: "#FF00FF" if x >= 1000 else "#00FF00" if x >= 300 else "#0016FF" if x >= 200 else "#E8720C" if x >= 100 else "#E6E600" if x >= 50 else "#B0B0B0") # set colors for the bubble plot by the mid_olp_1
    df["se1"] = df["(se1, ss2)"].apply(lambda x: int(x.split(",")[0].lstrip("("))) # (se1, ss2)
    df["ss2"] = df["(se1, ss2)"].apply(lambda x: int(x.split(",")[1].rstrip(")"))) # (se1, ss2)
    size_ratio = 10
    alpha_value = 0.5 # df["alpha"] = 0.5
    if len(df) > 0:
        plt.scatter(df['se1'], df['ss2'], s=df['subgroup_count_norm']*size_ratio, c=df['color'], alpha=alpha_value, linewidths=0)
        plt.grid(True, alpha=0.5)
        plt.xlim(1, ref_len)
        plt.ylim(1, ref_len)
        plt.savefig('bubble_type_2_rep_raw.pdf')
    # clear the plot, plt.clf()


def cal_ID_coverage(prefix, ref_fasta, reads_fasta, soft_paths_dict, threads, tmp_dir="tmp_coverage"):
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    command_1 = soft_paths_dict.get("meryl") + " count k=15 output " + tmp_dir + "/merylDB " + ref_fasta
    command_2 = soft_paths_dict.get("meryl") + " print greater-than distinct=0.9998 " + tmp_dir + "/merylDB > " + tmp_dir + "/repetitive_k15.txt"
    command_3 = soft_paths_dict.get("winnowmap") + " -W " + tmp_dir + "/repetitive_k15.txt -ax map-pb " + ref_fasta + " " + reads_fasta
    command_4 = soft_paths_dict.get("samtools") + " view -Sb -F 0x100 -@ " + threads + " -"
    command_5 = soft_paths_dict.get("samtools") + " sort -@ " + threads + " -o " + tmp_dir + "/" + prefix + ".sorted.bam "
    command_6 = soft_paths_dict.get("samtools") + " index -@ " + threads + " " + tmp_dir + "/" + prefix + ".sorted.bam "
    command_7 = soft_paths_dict.get("samtools") + " depth -a -J -@ " + threads + " " + tmp_dir + "/" + prefix + ".sorted.bam | cut -f2- > " + prefix + "_cov.txt"
    command_8 = "rm -rf " + tmp_dir
    commands = command_1 + " ; " + command_2 + " ; " + command_3 + " | " + command_4 + " | " + command_5 + " ; " + command_6 + " ; " + command_7 + " ; " + command_8
    get_cli_output_lines(commands, side_effect = True)


def plot_coverage(cov_file_1, cov_file_2, cov_file_3, start, end):
    cov_1 = np.loadtxt(cov_file_1, dtype=int)
    cov_2 = np.loadtxt(cov_file_2, dtype=int)
    cov_3 = np.loadtxt(cov_file_3, dtype=int)
    # add the second column of cov_1 and cov_2 to make cov_combine
    cov_combine = np.loadtxt(cov_file_1, dtype=int)
    cov_combine[:,1] = cov_1[:,1] + cov_2[:,1]
    fig = plt.figure(figsize=(12, 3), dpi=600)
    # plot cov_1, cov_2, cov_3 in the same figure
    plt.plot(cov_combine[(start-1):end, 1], color="#EAB13E", label="FL")
    plt.plot(cov_1[(start-1):end, 1], color="#D1D1D1", label="partial")
    plt.fill_between(np.arange(start-1, end), cov_combine[(start-1):end, 1], 1, color="#EAB13E", alpha=1) # run long time
    plt.fill_between(np.arange(start-1, end), cov_1[(start-1):end, 1], 1, color="#D1D1D1", alpha=1)
    plt.plot(cov_3[(start-1):end, 1], color="#5CAB38", label="variant", linewidth=1)
    plt.grid(True, alpha=0.5)
    ax = plt.gca()
    ax.set_xlim([start, end+1])
    max_y = int(np.max(cov_combine[:,1]))
    ax.set_ylim([0, max_y+100])
    plt.savefig('coverage_plot.pdf')
    plt.savefig('coverage_plot.png')


def run_bcftools(indexed_read):
    ref_fasta = indexed_read[2]
    soft_paths_dict = indexed_read[3]
    tmp_dir = indexed_read[4]
    with open(tmp_dir + "/" + str(indexed_read[0]) + "_tmp_read.fasta", "wt") as fout:
        print(indexed_read[1].format("fasta"), file=fout)
    command_1 = soft_paths_dict.get("winnowmap") + " -W " + tmp_dir + "/repetitive_k15.txt -ax map-pb " + ref_fasta + " " + tmp_dir + "/" + str(indexed_read[0]) + "_tmp_read.fasta"
    command_2 = "samtools view -Sb -F 0x100 -@ 1 -"
    command_3 = "samtools sort -@ 1 -o -"
    command_4 = soft_paths_dict.get("bcftools") + " mpileup --indels-2.0 -m 1 -Ou -f " + ref_fasta + " -"
    command_5 = soft_paths_dict.get("bcftools") + " call -mv -P 0.99 -Ov | grep -v '^#' | cut -f2,4,5"
    command_6 = "rm " + tmp_dir + "/" + str(indexed_read[0]) + "_tmp_read.fasta"
    commands = command_1 + " | " + command_2 + " | " + command_3 + " | " + command_4 + " | " + command_5 + " ; " + command_6
    results = get_cli_output_lines(commands, side_effect = False)
    with open("all_variant.vcf", "at") as fout:
        if len(results) > 0:
            for result in results:
                print(indexed_read[1].id + "\t" + result, file=fout)


def get_bcftools_frequency(ref_fasta, reads_fasta, soft_paths_dict, threads, tmp_dir="tmp_variants"):
    # randomize the reads
    records = list(SeqIO.parse(reads_fasta, "fasta"))
    random.shuffle(records) # this is important
    pass_records = [ record for record in records if len(record.seq) >= 1000 ]
    fail_records = [ record for record in records if len(record.seq) < 1000 ]
    with open("variant_fail_1000.fasta", "wt") as fout:
        SeqIO.write(fail_records, fout, "fasta")
    with open("variant_pass_1000.fasta", "wt") as fout:
        SeqIO.write(pass_records, fout, "fasta")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    if os.path.exists("all_variant.vcf"):
        os.remove("all_variant.vcf")
    command_1 = soft_paths_dict.get("meryl") + " count k=15 output " + tmp_dir + "/merylDB " + ref_fasta
    command_2 = soft_paths_dict.get("meryl") + " print greater-than distinct=0.9998 " + tmp_dir + "/merylDB > " + tmp_dir + "/repetitive_k15.txt"
    commands = command_1 + " ; " + command_2
    get_cli_output_lines(commands, side_effect = True)
    indexed_reads = tuple([ (i, pass_records[i], ref_fasta, soft_paths_dict, tmp_dir) for i in range(len(pass_records)) ])
    with cf.ThreadPoolExecutor(int(threads)) as tex:
        tex.map(run_bcftools, indexed_reads)
    get_cli_output_lines("rm -rf " + tmp_dir + " " + ref_fasta + ".fai", side_effect = True) # remove the tmp_dir and ref_fasta.fai
    reads_ids = tuple([read.id for read in pass_records])

    with open("all_variant.vcf", "r", errors='ignore') as fin:
        with open("all_variant_clean.vcf", "wt") as fout:
            for line in fin.readlines():
                try:
                    if (len(line.split("\t")) == 4) and (line.split("\t")[0] in reads_ids) and (str.isdigit(line.split("\t")[1])):
                        print(line.rstrip("\n").encode('utf-8').decode('utf-8'), file=fout)
                except UnicodeDecodeError:
                    continue

    with open("all_variant_clean.vcf", "rt") as fin:
        lines = [line.rstrip("\n") for line in fin.readlines()]
        if os.path.exists("snv_indel.txt"):
            os.remove("snv_indel.txt")
        with open("snv_indel.txt", "at") as fout:
            for line in lines:
                fields = line.split("\t")
                if len(fields[2]) == 1 and len(fields[3]) == 1:
                    print(line + "\t" + "SNV", file=fout)
                else:
                    print(line + "\t" + "InDel", file=fout)

    df = pd.read_table("snv_indel.txt", header=None, dtype={0: str, 1: int, 2: str, 3: str, 4: str})
    all_POS_REF_type = {(int(df[1][i]), df[2][i], df[4][i]) for i in range(len(df))}
    all_list = list(all_POS_REF_type)
    all_list.sort(key=lambda x:x[0])
    reform_dict = dict()
    for i in range(len(df)):
        index_tuple = (df.loc[i, 1], df.loc[i, 2], df.loc[i, 4])
        if reform_dict.get(index_tuple) == None:
            reform_dict[index_tuple] = (df.loc[i, 3], df.loc[i, 0])
        else:
            if not isinstance(df.loc[i, 3], str):
                continue
            try:
                reform_dict[index_tuple] = (",".join((reform_dict.get(index_tuple)[0], df.loc[i, 3])), ",".join((reform_dict.get(index_tuple)[1], df.loc[i, 0])))
            except TypeError:
                continue
    df_reform = pd.DataFrame(columns=["ALT_list", "ID_list", "total_counts"], index=all_list)
    for POS_REF_type in all_list:
        ALT_list_all = reform_dict[POS_REF_type][0]
        ALT_list_unique = list(set(ALT_list_all.split(",")))
        ALT_list_unique.sort()
        df_reform["ALT_list"][POS_REF_type] = ",".join(ALT_list_unique)
        df_reform["ID_list"][POS_REF_type] = reform_dict[POS_REF_type][1]
        df_reform["total_counts"][POS_REF_type] = len(list(set(reform_dict[POS_REF_type][1].split(","))))
    df_reform.to_excel("snv_indel_reformat.xlsx")

    df_reform = pd.read_excel("snv_indel_reformat.xlsx")
    df_reform.rename(columns={"Unnamed: 0":"POS_REF_type"}, inplace=True)
    for i in range(len(df_reform)):
        df_reform.loc[i, "index"] = i + 1
        POS_REF_type_list = df_reform.loc[i, "POS_REF_type"].lstrip("(").rstrip(")").replace(" ", "").replace("'", "").replace('"', "").split(",")
        df_reform.loc[i, "POS"] = POS_REF_type_list[0]
        df_reform.loc[i, "REF"] = POS_REF_type_list[1]
        df_reform.loc[i, "type"] = POS_REF_type_list[2]
    df_reform['index'] = df_reform['index'].astype(int)
    with open("index_ids.txt", "wt") as fout:
        for i in range(len(df_reform)):
            print(df_reform.loc[i, "index"], df_reform.loc[i, "ID_list"], sep="\t", file=fout)
    df_reform.to_excel("snv_indel_reformat.xlsx")

    df_short = df_reform[['index', 'type', 'POS', 'REF', 'ALT_list', "total_counts"]]
    df_cov = pd.read_table("variant_cov.txt", header=None)
    df_cov.columns = ["POS", "samtools_depth"]
    df_cov_dict = df_cov.set_index('POS').T.to_dict('list')
    for i in range(len(df_short)):
        df_short.loc[i, "samtools_depth"] = df_cov_dict[int(df_short.loc[i, "POS"])][0]
        df_short.loc[i, "frequency"] = df_short.loc[i, "total_counts"] / df_short.loc[i, "samtools_depth"]
    df_short.sort_values("frequency", inplace = True, ascending=False)
    df_short.to_excel("variant_frequency_anno.xlsx")
    df_short.to_excel("variant_frequency_backup.xlsx")
    df_short['POS'] = df_short['POS'].astype(int)
    # if frequency >= 0.3
    df_short_filt = df_short[df_short["frequency"] >= 0.3]
    df_short_filt.to_csv("variant_high_frequency.txt", sep="\t", index=False, header=False)
    return df_short


def get_pysam_frequency(df_short, ref_fasta, reads_fasta, soft_paths_dict, threads, top=100, tmp_dir="tmp_pysam"):
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    command_1 = soft_paths_dict.get("meryl") + " count k=15 output " + tmp_dir + "/merylDB " + ref_fasta
    command_2 = soft_paths_dict.get("meryl") + " print greater-than distinct=0.9998 " + tmp_dir + "/merylDB > " + tmp_dir + "/repetitive_k15.txt"
    command_3 = soft_paths_dict.get("winnowmap") + " -W " + tmp_dir + "/repetitive_k15.txt -ax map-pb " + ref_fasta + " " + reads_fasta
    command_4 = soft_paths_dict.get("samtools") + " view -Sb -F 0x100 -@ " + threads + " -"
    command_5 = soft_paths_dict.get("samtools") + " sort -@ " + threads + " -o " + tmp_dir + "/pysam.sorted.bam "
    command_6 = soft_paths_dict.get("samtools") + " index -@ " + threads + " " + tmp_dir + "/pysam.sorted.bam "
    commands = command_1 + " ; " + command_2 + " ; " + command_3 + " | " + command_4 + " | " + command_5 + " ; " + command_6
    get_cli_output_lines(commands, side_effect = True)
    samfile = pysam.AlignmentFile(tmp_dir + "/pysam.sorted.bam", "rb") # mito.sorted.bam, replicate if using multi-threading
    df_indel = df_short[df_short['type'] == "InDel"]
    df_indel_top = df_indel.head(top)
    df_indel_top = df_indel_top.sort_values(by=['POS'], ascending=True)
    # change the type of POS to int
    df_indel_top['POS'] = df_indel_top['POS'].astype(int)
    records = list(SeqIO.parse(ref_fasta, "fasta"))
    if len(records) != 1:
        exit()
    for i in df_indel_top.index:
        POS = df_indel_top.loc[i, 'POS']
        depth = samfile.count(contig=records[0].id, start=POS-1, stop=POS) 
        counts_dict = dict()
        for pc in samfile.pileup(contig=records[0].id, start=POS-1, stop=POS):
            if pc.pos == (POS-1):
                for pr in pc.pileups:
                    if counts_dict.get(pr.indel) == None:
                        counts_dict[pr.indel] = 1
                    else:
                        counts_dict[pr.indel] += 1
        counts_keys = list(counts_dict.keys())
        counts_keys.sort()
        counts_list_info = [ str(item) + ":" + str(counts_dict[item]) for item in counts_keys ]
        df_indel_top.loc[i, 'depth'] = depth
        df_indel_top.loc[i, 'pysam'] = ";".join(counts_list_info)
        if 0 in counts_dict.keys():
            df_indel_top.loc[i, 'ref_freq'] = counts_dict[0] / depth
        else:
            df_indel_top.loc[i, 'ref_freq'] = 0
    df_indel_top = df_indel_top.drop(df_indel_top.columns[0], axis=1)
    df_indel_top = df_indel_top.sort_values(by=['ref_freq'], ascending=True)
    df_indel_top.to_excel("top_" + str(top) + "_indel_pysam.xlsx", index=False)

    df_SNV = df_short[df_short['type'] == "SNV"]
    df_SNV_top = df_SNV.head(top)
    df_SNV_top = df_SNV_top.sort_values(by=['POS'], ascending=True)
    # change the type of POS to int
    df_SNV_top['POS'] = df_SNV_top['POS'].astype(int)
    for i in df_SNV_top.index:
        POS = df_SNV_top.loc[i, 'POS']
        depth = samfile.count(contig=records[0].id, start=POS-1, stop=POS)
        counts_array = samfile.count_coverage(contig=records[0].id, start=POS-1, stop=POS, quality_threshold=0)    # ACGT, N
        counts_str = str(list(counts_array[0])[0]) + "," + str(list(counts_array[1])[0]) + ","+ str(list(counts_array[2])[0]) + "," + str(list(counts_array[3])[0])
        df_SNV_top.loc[i, 'depth'] = depth
        df_SNV_top.loc[i, 'pysam'] = counts_str
        ref_base = df_SNV_top.loc[i, 'REF']
        if ref_base == "A":
            df_SNV_top.loc[i, 'ref_freq'] = list(counts_array[0])[0] / depth
        elif ref_base == "C":
            df_SNV_top.loc[i, 'ref_freq'] = list(counts_array[1])[0] / depth
        elif ref_base == "G":
            df_SNV_top.loc[i, 'ref_freq'] = list(counts_array[2])[0] / depth
        elif ref_base == "T":
            df_SNV_top.loc[i, 'ref_freq'] = list(counts_array[3])[0] / depth
        else:
            df_SNV_top.loc[i, 'ref_freq'] = 0
    df_SNV_top = df_SNV_top.drop(df_SNV_top.columns[0], axis=1)
    df_SNV_top = df_SNV_top.sort_values(by=['ref_freq'], ascending=True)
    df_SNV_top.to_excel("top_" + str(top) + "_SNV_pysam.xlsx", index=False)
    samfile.close()
    get_cli_output_lines("rm -rf " + tmp_dir, side_effect=True)


if __name__ == "__main__":
    pass