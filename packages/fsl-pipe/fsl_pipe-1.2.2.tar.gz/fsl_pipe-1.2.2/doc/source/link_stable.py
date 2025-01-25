import os
import importlib.metadata

build_dir = "doc/build"
assert os.path.isdir(build_dir)

stable = importlib.metadata.version("fsl_pipe")
os.symlink("v" + stable, f"{build_dir}/stable")
os.symlink("main", f"{build_dir}/dev")

with open(f"{build_dir}/index.html", "w") as f:
    f.write('<meta http-equiv="refresh" content="0; url=stable/index.html" />\n')
