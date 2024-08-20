# Load the reticulate package
if (!requireNamespace("reticulate", quietly = TRUE)) {
  install.packages("reticulate")
}
library(reticulate)
source("R/my_functions.R")

# Main script to create a Python virtual environment and install Java locally
create_python_env(envname = "myenv")  # Create and set up the Python virtual environment
java_home <- install_local_java(java_dir = "~/local/java/jdk-21.0.12.jdk")
set_java_home(java_home)

# Verify the installation and the ability to use JPype with the local JVM
cat("Verifying the JPype setup with the local JVM...\n")
libjli_path <- file.path(java_home, "lib/libjli.dylib")
if (!file.exists(libjli_path)) { 
  stop("The libjli.dylib file was not found. Please check the JDK installation.")
}

size <- '-Xmx2g'
classpath <- 'classpath=["resources/tetrad-current.jar"]'

python_code <- sprintf("
import jpype
try:
    jpype.startJVM('%s', '%s', %s)
    print('JVM started successfully with Java version:', jpype.java.lang.System.getProperty('java.version'))
except OSError as e:
    print('Failed to start JVM:', e)
", libjli_path, size, classpath)

print(python_code)

py_run_string(python_code)
