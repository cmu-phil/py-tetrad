
# Function to create a Python virtual environment and install necessary packages
create_python_env <- function(envname = "myenv") {
  platform <- .Platform$OS.type
  sysname <- Sys.info()["sysname"]
  
  # Determine the path to Python 3.x depending on the platform
  python_path <- ""
  if (platform == "windows") {
    python_path <- "python"
  } else if (sysname == "Darwin") {
    python_path <- "/usr/local/bin/python3"
  } else if (sysname == "Linux") {
    python_path <- "/usr/bin/python3"
  }
  
  # Create the virtual environment
  virtualenv_create(envname = envname, python = python_path)
  
  # Activate the virtual environment
  use_virtualenv(envname, required = TRUE)
  
  # Install the required packages
  virtualenv_install(envname, packages = c("numpy", "pandas", "JPype1", "pearson", "DiagrammeR"))
}

# Function to install Java JDK 21 locally, considering architecture
install_local_java <- function(java_dir = "~/local/java/jdk-21.0.12.jdk") {
  platform <- .Platform$OS.type
  sysname <- Sys.info()["sysname"]
  arch <- Sys.info()["machine"]
  
  if (platform == "windows") {
    download.file("https://corretto.aws/downloads/latest/amazon-corretto-21-x64-windows-jdk.zip", destfile = "jdk.zip")
    dir.create(java_dir, recursive = TRUE)
    unzip("jdk.zip", exdir = java_dir)
    java_dir <- normalizePath(file.path(java_dir, "amazon-corretto-17-x64-windows-jdk"))
  } else if (sysname == "Darwin") {
    # Check if the architecture is ARM (aarch64) or Intel (x86_64)
    if (arch == "arm64" || arch == "aarch64") {
      download.file("https://corretto.aws/downloads/latest/amazon-corretto-21-aarch64-macos-jdk.tar.gz", destfile = "jdk.tar.gz")
    } else {
      download.file("https://corretto.aws/downloads/latest/amazon-corretto-21-x64-macos-jdk.tar.gz", destfile = "jdk.tar.gz")
    }
    dir.create(java_dir, recursive = TRUE)
    system(paste("tar -xzf jdk.tar.gz -C", java_dir, "--strip-components=1"), wait = TRUE)
    java_dir <- normalizePath(file.path(java_dir, "Contents/Home"))
  } else if (sysname == "Linux") {
    download.file("https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz", destfile = "jdk.tar.gz")
    dir.create(java_dir, recursive = TRUE)
    system(paste("tar -xzf jdk.tar.gz -C", java_dir, "--strip-components=1"), wait = TRUE)
  }
  
  return(java_dir)
}

# Function to set the JAVA_HOME environment variable
set_java_home <- function(java_home) {
  Sys.setenv(JAVA_HOME = java_home)
  Sys.setenv(PATH = paste0(java_home, "/bin:", Sys.getenv("PATH")))
  print(paste("JAVA_HOME is set to:", Sys.getenv("JAVA_HOME")))
}

# Create the variable list (ArrayList<Node>)
create_variables <- function(data) {
  # .jinit()
  vars <- .jnew("java/util/ArrayList")
  
  # Assuming data frame column names represent your variables
  for (name in colnames(data)) {
  variable <- .jnew("edu/cmu/tetrad/data/ContinuousVariable", name)
  node <- .jcast(variable, "edu/cmu/tetrad/graph/Node")
  .jcall(vars, "Z", "add", .jcast(node, "java/lang/Object"))
  }
  
  vars <- .jcast(vars, "java/util/List")
  return(vars)
}