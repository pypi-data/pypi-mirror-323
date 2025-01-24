import pyexeggutor as exe
logger = exe.build_logger("testing")
file_1="example.txt"
directory_1="example_directory/"

exe.copy_file(file_1, directory_1, gzip=True, logger=logger)
exe.gzip_file(file_1, "example_directory/example_1-copy.txt.gz")
exe.copy_file(file_1, "example2.txt", logger=logger)
exe.copy_file("example_directory", "example_directory2")

