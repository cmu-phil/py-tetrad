# ----- Utility Functions -----

# Constants for Java JDK URLs
WINDOWS_JDK_URL <- "https://corretto.aws/downloads/latest/amazon-corretto-21-x64-windows-jdk.zip"
MAC_JDK_URL_ARM <- "https://corretto.aws/downloads/latest/amazon-corretto-21-aarch64-macos-jdk.tar.gz"
MAC_JDK_URL_X86 <- "https://corretto.aws/downloads/latest/amazon-corretto-21-x64-macos-jdk.tar.gz"
LINUX_JDK_URL <- "https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz"
TETRAD_URL <- "https://s01.oss.sonatype.org/content/repositories/releases/io/github/cmu-phil/tetrad-gui/7.6.5/tetrad-gui-7.6.5-launch.jar"
TETRAD_PATH <- "resources/tetrad-gui-7.6.5-launch.jar"

check_internet_connection <- function() {
  tryCatch({
    url <- "http://www.google.com"
    con <- url(url, "r")
    close(con)
    TRUE
  }, error = function(e) {
    FALSE
  })
}

download_file <- function(url, destfile) {
  if (!check_internet_connection()) {
    stop("No internet connection. Please check your network and try again.")
  }
  
  tryCatch({
    download.file(url, destfile)
    if (!file.exists(destfile)) {
      stop("Failed to download file from ", url)
    }
    cat("Download successful: ", destfile, "\n")
  }, error = function(e) {
    cat("An error occurred during the download: ", e$message, "\n")
    stop("Please check your internet connection or the availability of the file and try again.")
  })
}

# Function to ensure necessary packages are installed
ensure_packages_installed <- function(packages) {
  for (pkg in packages) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      install.packages(pkg)
    }
  }
  lapply(packages, library)#, character.only = TRUE)
}

# # Function to download Java JDK based on platform
# download_file <- function(url, destfile) {
#   download.file(url, destfile)
#   if (!file.exists(destfile)) {
#     stop("Failed to download Java from ", url)
#   }
# }

# Function to install Java JDK 21 locally, considering architecture
#' Install Java JDK locally
#'
#' This function installs Java JDK 21 locally to the specified directory.
#' It handles different platforms and architectures.
#' 
#' @param java_dir Directory to install the JDK.
#' @return The path to the installed JDK.
install_local_java <- function(java_dir = file.path("resources", "jdk-21.0.12.jdk")) {
  cat("Starting Java installation...\n")
  
  if (dir.exists(java_dir)) {
    cat("Java JDK is already installed at:", java_dir, "\n")
    return(java_dir)
  }
  
  tryCatch({
    platform <- .Platform$OS.type
    sysname <- Sys.info()["sysname"]
    arch <- Sys.info()["machine"]
    cat("Detected platform:", platform, ", System name:", sysname, ", Architecture:", arch, "\n")
    
    if (platform == "windows") {
      download_file(WINDOWS_JDK_URL, "resources/jdk.zip")
      dir.create(java_dir, recursive = TRUE)
      unzip("resources/jdk.zip", exdir = java_dir)
      file.remove("resources/jdk.zip")
      
    } else if (sysname == "Darwin") {
      if (arch == "arm64" || arch == "aarch64") {
        download_file(MAC_JDK_URL_ARM, "resources/jdk.tar.gz")
      } else {
        download_file(MAC_JDK_URL_X86, "resources/jdk.tar.gz")
      }
      dir.create(java_dir, recursive = TRUE)
      system(paste("tar -xzf resources/jdk.tar.gz -C", java_dir, "--strip-components=1"), wait = TRUE)
      file.remove("resources/jdk.tar.gz")
      
    } else if (sysname == "Linux") {
      download_file(LINUX_JDK_URL, "resources/jdk.tar.gz")
      dir.create(java_dir, recursive = TRUE)
      system(paste("tar -xzf resources/jdk.tar.gz -C", java_dir, "--strip-components=1"), wait = TRUE)
      file.remove("resources/jdk.tar.gz")
    }
    
    cat("Java JDK installed at:", java_dir, "\n")
  }, error = function(e) {
    cat("An error occurred during Java installation:", e$message, "\n")
    stop("Installation failed. Please check the logs for more details.")
  })
  
  return(java_dir)
}

# Function to set the JAVA_HOME environment variable
#' Set JAVA_HOME environment variable
#'
#' This function sets the JAVA_HOME environment variable and updates the system PATH.
#'
#' @param java_home The path to the Java home directory.
set_java_home <- function(java_home) {
  cat("Setting JAVA_HOME to:", java_home, "\n")
  
  if (!dir.exists(java_home)) {
    stop("The specified JAVA_HOME directory does not exist: ", java_home)
  }
  
  Sys.setenv(JAVA_HOME = java_home)
  Sys.setenv(PATH = paste0(java_home, "/bin:", Sys.getenv("PATH")))
  cat("JAVA_HOME is set to:", Sys.getenv("JAVA_HOME"), "\n")
}

# Function to download Tetrad
#' Download Tetrad JAR file
#'
#' This function downloads the Tetrad JAR file to the resources directory.
download_tetrad <- function() {
  cat("Starting Tetrad download...\n")
  
  if (!dir.exists("resources")) {
    dir.create("resources", recursive = TRUE)
    cat("Created resources directory.\n")
  }
  
  destfile <- TETRAD_PATH
  
  if (file.exists(destfile)) {
    cat("File already exists at:", destfile, "\n")
  } else {
    download_file(TETRAD_URL, destfile)
    cat("File downloaded successfully to:", destfile, "\n")
  }
}

# Function to create the variable list (ArrayList<Node>)
#' Create variable list for Covariance Matrix
#'
#' This function creates an ArrayList of Nodes from the data frame's column names
#' to be used in the Covariance Matrix.
#'
#' @param data The data frame containing the variables.
#' @return A Java List of Nodes.
create_variables <- function(data) {
  cat("Creating variable list from data...\n")
  
  vars <- .jnew("java/util/ArrayList")
  
  for (name in colnames(data)) {
    cat("Adding variable:", name, "to the list.\n")
    variable <- .jnew("edu/cmu/tetrad/data/ContinuousVariable", name)
    node <- .jcast(variable, "edu/cmu/tetrad/graph/Node")
    .jcall(vars, "Z", "add", .jcast(node, "java/lang/Object"))
  }
  
  vars <- .jcast(vars, "java/util/List")
  cat("Variable list creation complete. Number of variables added:", length(vars), "\n")
  
  return(vars)
}

# ----- Dependency Management -----
ensure_packages_installed <- function(packages) {
  for (pkg in packages) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      install.packages(pkg)
    }
  }
  lapply(packages, library, character.only = TRUE)
}

# ----- Tetrad Setup -----
setup_tetrad_environment <- function() {
  source("resources/tetrad_utils.R")
  source("resources/TetradSearch.R")

  java_home <- install_local_java(java_dir = "resources/jdk-21.0.12.jdk")
  set_java_home(java_home)
  
  download_tetrad()
  
  # Initialize Java
  initialize_java()
}

# ----- Initialize Java and Check Version -----
initialize_java <- function() {
  library(rJava)
  
   .jinit()
  # .jinit(parameters = "-verbose:class")
  .jaddClassPath(TETRAD_PATH)

  java_version <- .jcall("java/lang/System", "S", "getProperty", "java.version")
  print(paste("Java version:", java_version))
}

# ----- Graph Visualization -----
visualize_graph <- function(graph) {
  if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
    b <- TRUE
  } else if (Sys.getenv("RSTUDIO") == "1") {
    b <- TRUE
  } else {
    b <- FALSE
  }
  
  if (b) {
    if (!is.null(graph)) {
      dot <- .jcall("edu/cmu/tetrad/graph/GraphSaveLoadUtils", "Ljava/lang/String;", "graphToDot", graph)
      grViz(dot)
    } else {
      cat("No graph generated. Please check the BOSS execution.\n")
    }
  }


}

