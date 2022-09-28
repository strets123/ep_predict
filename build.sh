docker build . --progress=plain >> /tmp/build.log  2>&1
python split_output.py