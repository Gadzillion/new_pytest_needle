import os
import subprocess
from pathlib import Path
from new_pytest_needle.engines.base import EngineBase


class Engine(EngineBase):
    compare_path = "magick compare"
    compare_command = (
        "{compare} -metric rmse -subimage-search -dissimilarity-threshold 1 {baseline} {new} {diff}"
    )

    def assertSameFiles(self, output_file, baseline_file, threshold=0):
        try:
            diff_file = output_file.replace('.png', '.diff.png')
            compare_cmd = self.compare_command.format(
                compare=self.compare_path,
                baseline=baseline_file,
                new=output_file,
                diff=diff_file)
            process = subprocess.Popen(compare_cmd, shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            compare_stdout, compare_stderr = process.communicate()
            difference = float(compare_stderr.split()[1][1:-1])
            return difference
        except:
            return compare_stderr
