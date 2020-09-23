import subprocess
from new_pytest_needle.engines.base import EngineBase
from PIL import Image


class Engine(EngineBase):
    compare_path = "magick compare"
    compare_command = (
        "{compare} -metric rmse -subimage-search -dissimilarity-threshold 1 {baseline} {new} {diff}"
    )

    def assertSameFiles(self, output_file, baseline_file, threshold=0):

        output_img = Image.open(output_file)
        baseline_img = Image.open(baseline_file)
        output_width, output_height = output_img.size
        baseline_width, baseline_height = baseline_img.size

        if baseline_width > output_width:
            baseline_file = baseline_file
            output_file = output_file
        else:
            baseline_file = output_file
            output_file = baseline_file

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
            return difference, output_width, output_height, baseline_width, baseline_height
        except:
            return compare_stderr, output_width, output_height, baseline_width, baseline_height
