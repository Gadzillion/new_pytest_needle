import os
import subprocess
from pathlib import Path
from needle.engines.base import EngineBase


class Engine(EngineBase):
    compare_path = "compare"
    compare_command = ("{compare} -metric RMSE -subimage-search -dissimilarity-threshold 1.0 {baseline} "
                       "{new} {diff}")

    def assertSameFiles(self, output_file, baseline_file, threshold=0):
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

        if difference <= threshold:
            par_dif = Path(diff_file)
            filelist = [f for f in os.listdir(par_dif.parent) if f.endswith(".png")]
            for f in filelist:
                os.remove(os.path.join(par_dif.parent, f))
            return

        raise AssertionError(f"The new screenshot did not match the baseline. Diff: {difference}"
                             .format(difference=str(difference*100)))
