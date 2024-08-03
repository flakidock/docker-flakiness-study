from enum import Enum

CHAT_COMPLETION_FILL_PROMPT_TEMPLATE_ERROR_LINE_ONLY = """
You are an AI assistant specialized in analyzing Dockerfile build errors and extracting debugging information to help troubleshoot these errors.

GOAL: Given a Dockerfile error line (DOCKERFILE_ERROR_LINE) and an error message (ERROR_MESSAGE), your task is to understand the nature of the error and extract the following information:

1. Summary: Summarize the error in no more than 100 words, focusing on the reasons and sources of the error.
2. Label: Based on the information extracted and the summary, provide a label in no more than 10 words that reveals the type of error and what caused it.
3. Error sources: Mention the names of the sources of errors, like packages, Docker environment, etc, in a list.

CONSTRAINTS:
No user assistance

The output (JSON_OUTPUT) should be formatted as JSON. Only provide the JSON output. Below is an example:

# DOCKERFILE_ERROR_LINE:
```
RUN apt-get install -y libmariadb-client-lgpl-dev
```

# ERROR_MESSAGE:
'''
> [ 5/17] RUN apt-get install -y libmariadb-client-lgpl-dev:
Reading state information...
Package libmariadb-client-lgpl-dev is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
However the following packages replace it:
  libmariadb-dev
E: Package 'libmariadb-client-lgpl-dev' has no installation candidate
ERROR: process "/bin/sh -c apt-get install -y libmariadb-client-lgpl-dev" did not complete successfully: exit code: 100
'''

# JSON_OUTPUT:
'''
{
"summary": "The Dockerfile build failed because the package 'libmariadb-client-lgpl-dev' cannot be installed. It is either missing, obsolete, or available from another source. The package 'libmariadb-dev' can be used as a replacement.",
"label": "Package Installation Error",
"sources of error": [ "libmariadb-client-lgpl-dev package"]
}
'''
"""

CHAT_COMPLETION_FILL_PROMPT_WITH_DOCKER_FILE_TEMPLATE = """
You are an AI assistant specialized in analyzing Dockerfile build errors and extracting debugging information to help troubleshoot these errors.

GOAL: Given a Dockerfile (DOCKERFILE) up to the error line, the error line within the Dockerfile (DOCKERFILE_ERROR_LINE), and an associated error message (ERROR_MESSAGE), your task is to understand the nature of the error and extract the following information:

1. Summary: Summarize the error in no more than 100 words, focusing on the reasons and sources of the error.
2. Label: Based on the extracted information and the summary, provide a label in no more than 10 words that reveals the type of error and what caused it.
3. Error sources: Mention the names of the sources of errors, like packages, Docker environment, etc, in a list.

CONSTRAINTS:
No user assistance

The output (JSON_OUTPUT) should be formatted as JSON. Only provide the JSON output. Below is an example:

# DOCKERFILE:
```
FROM rocker/shiny
COPY . /srv/shiny-server

# RUN apt-get update
# RUN apt-get install libmariadb-client-lgpl-dev
# RUN R -e "source('https://bioconductor.org/biocLite.R'); biocLite('Biobase'); biocLite('ComplexHeatmap'); biocLite('circlize'); install.packages('shinyjs'); install.packages('shinyBS'); install.packages('RMySQL'); install.packages('reshape2'); "
RUN apt-get update
RUN apt-get install -y libssl-dev libssh2-1-dev
RUN apt-get install -y libmariadb-client-lgpl-dev
RUN apt-get install -y libxml2-dev libx11-dev
RUN apt-get install -y libglu1-mesa-dev freeglut3-dev mesa-common-dev
```

# DOCKERFILE_ERROR_LINE:
```
RUN apt-get install -y libmariadb-client-lgpl-dev
```

# ERROR_MESSAGE:
'''
> [ 5/17] RUN apt-get install -y libmariadb-client-lgpl-dev:
Reading state information...
Package libmariadb-client-lgpl-dev is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
However the following packages replace it:
  libmariadb-dev
E: Package 'libmariadb-client-lgpl-dev' has no installation candidate
ERROR: process "/bin/sh -c apt-get install -y libmariadb-client-lgpl-dev" did not complete successfully: exit code: 100
'''

# JSON_OUTPUT:
'''
{
"summary": "The Dockerfile build failed because the package 'libmariadb-client-lgpl-dev' cannot be installed. It is either missing, obsolete, or available from another source. The package 'libmariadb-dev' can be used as a replacement.",
"label": "Package Installation Error",
"sources of error": [ "libmariadb-client-lgpl-dev package"]
}
'''
"""

CHAT_COMPLETION_FILL_PROMPT_WITH_FULL_DOCKER_FILE_TEMPLATE = """
You are an AI assistant specialized in analyzing Dockerfile build errors and extracting debugging information to help troubleshoot these errors.

GOAL: Given a Dockerfile (DOCKERFILE), an error line within the Dockerfile (DOCKERFILE_ERROR_LINE), and an associated error message (ERROR_MESSAGE), your task is to understand the nature of the error and extract the following information:

1. Summary: Summarize the error in no more than 100 words, focusing on the reasons and sources of the error.
2. Label: Based on the summary, provide a label in no more than 10 words that reveals the type of error and what caused it.
3. Error Sources: Mention the names of the sources of errors, like packages, Docker environment, etc, in a list.

CONSTRAINTS:
No user assistance

The output (JSON_OUTPUT) should be formatted as JSON. Only provide the JSON output. Below is an example:

# DOCKERFILE:
```
FROM rocker/shiny
COPY . /srv/shiny-server

# RUN apt-get update
# RUN apt-get install libmariadb-client-lgpl-dev
# RUN R -e "source('https://bioconductor.org/biocLite.R'); biocLite('Biobase'); biocLite('ComplexHeatmap'); biocLite('circlize'); install.packages('shinyjs'); install.packages('shinyBS'); install.packages('RMySQL'); install.packages('reshape2'); "
RUN apt-get update
RUN apt-get install -y libssl-dev libssh2-1-dev
RUN apt-get install -y libmariadb-client-lgpl-dev
RUN apt-get install -y libxml2-dev libx11-dev
RUN apt-get install -y libglu1-mesa-dev freeglut3-dev mesa-common-dev

RUN R -e "source('https://bioconductor.org/biocLite.R'); biocLite('Biobase'); biocLite('ComplexHeatmap'); biocLite('RNASeqPower'); biocLite('rols'); biocLite('rhdf5');"
RUN R -e "source('https://bioconductor.org/biocLite.R'); biocLite('circlize'); biocLite('edgeR'); biocLite('DESeq2'); biocLite('limma');"
RUN R -e "install.packages(c('shinyjs', 'shinyBS', 'RMySQL', 'shinycssloaders'), repos = 'http://cran.us.r-project.org');"

RUN R -e "install.packages(c('devtools', 'rsconnect', 'httr', 'dplyr'), repos = 'http://cran.us.r-project.org');"
RUN R -e "install.packages(c('shinyRGL', 'rgl', 'rglwidget', 'Rtsne'), repos = 'http://cran.us.r-project.org');"
RUN R -e "install.packages(c('RColorBrewer', 'pairsD3'), repos = 'http://cran.us.r-project.org');"
RUN R -e "install.packages(c('locfit', 'feather', 'data.table'), repos = 'http://cran.us.r-project.org');"
RUN R -e "install.packages(c('ggplot2', 'plotly', 'reshape2'), repos = 'http://cran.us.r-project.org');"
RUN R -e "devtools::install_github('ropensci/iheatmapr');"
RUN R -e "devtools::install_github('rstudio/DT');"
```

# DOCKERFILE_ERROR_LINE:
```
RUN apt-get install -y libmariadb-client-lgpl-dev
```

# ERROR_MESSAGE:
'''
> [ 5/17] RUN apt-get install -y libmariadb-client-lgpl-dev:
Reading state information...
Package libmariadb-client-lgpl-dev is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
However the following packages replace it:
  libmariadb-dev
E: Package 'libmariadb-client-lgpl-dev' has no installation candidate
ERROR: process "/bin/sh -c apt-get install -y libmariadb-client-lgpl-dev" did not complete successfully: exit code: 100
'''

# JSON_OUTPUT:
'''
{
"summary": "The Dockerfile build failed because the package 'libmariadb-client-lgpl-dev' cannot be installed. It is either missing, obsolete, or available from another source. The package 'libmariadb-dev' can be used as a replacement.",
"label": "Package Installation Error",
"sources of error": [ "libmariadb-client-lgpl-dev package"]
}
'''
"""

CHAT_COMPLETION_FILL_PROMPT_WITH_FULL_METADATA = """
You are an AI assistant specialized in analyzing Dockerfile build errors and extracting debugging information to help troubleshoot these errors.

GOAL: Given a Dockerfile (DOCKERFILE) up to the error line, an error line within the Dockerfile (DOCKERFILE_ERROR_LINE), an associated error message (ERROR_MESSAGE), and the exit code which is usually a number or a short description (EXIT_CODE). your task is to understand the nature of the error and extract the following information:

1. Summary: Summarize the error in no more than 100 words, focusing on the reasons and sources of the error.
2. Label: Based on the summary, provide a label in no more than 10 words that reveals the type of error and what caused it.
3. Error Sources: Mention the names of the sources of errors, like packages, Docker environment, etc, in a list.

CONSTRAINTS:
No user assistance

The output (JSON_OUTPUT) should be formatted as JSON. Only provide the JSON output. Below is an example:

# DOCKERFILE:
```
FROM rocker/shiny
COPY . /srv/shiny-server

# RUN apt-get update
# RUN apt-get install libmariadb-client-lgpl-dev
# RUN R -e "source('https://bioconductor.org/biocLite.R'); biocLite('Biobase'); biocLite('ComplexHeatmap'); biocLite('circlize'); install.packages('shinyjs'); install.packages('shinyBS'); install.packages('RMySQL'); install.packages('reshape2'); "
RUN apt-get update
RUN apt-get install -y libssl-dev libssh2-1-dev
RUN apt-get install -y libmariadb-client-lgpl-dev
RUN apt-get install -y libxml2-dev libx11-dev
RUN apt-get install -y libglu1-mesa-dev freeglut3-dev mesa-common-dev
```

# DOCKERFILE_ERROR_LINE:
```
RUN apt-get install -y libmariadb-client-lgpl-dev
```

# ERROR_MESSAGE:
'''
> [ 5/17] RUN apt-get install -y libmariadb-client-lgpl-dev:
Reading state information...
Package libmariadb-client-lgpl-dev is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
However the following packages replace it:
  libmariadb-dev
E: Package 'libmariadb-client-lgpl-dev' has no installation candidate
ERROR: process "/bin/sh -c apt-get install -y libmariadb-client-lgpl-dev" did not complete successfully: exit code: 100
'''

# EXIT_CODE:
'''
100
'''

# JSON_OUTPUT:
'''
{
"summary": "The Dockerfile build failed because the package 'libmariadb-client-lgpl-dev' cannot be installed. It is either missing, obsolete, or available from another source. The package 'libmariadb-dev' can be used as a replacement.",
"label": "Package Installation Error",
"sources of error": [ "libmariadb-client-lgpl-dev package"]
}
'''
"""

USER_PROMPT_WITH_FULL_DOCKERFILE = """
# DOCKERFILE:
```
```

# DOCKERFILE_ERROR_LINE:
```
```
            
# ERROR_MESSAGE:
'''
'''

Parse this docker build error in the specified format. Don't explain your process, just give the JSON output. Make sure your output can be parsed by json.loads.
"""

CLUSTER_ERRORS_WITH_INITIAL_LABELS = """
You are an AI assistant specialized in categorizing errors into meaningful groups. Each category should only contain errors that matches exactly or almost exactly according to their meaning. The goal is to categorize the errors into meaningful groups based on the error messages.

GOAL: Given a list of intial error labels (ERROR_LABELS), your task is to understand the errors and categorize them into rational groups. You should provide a list of clusters, where each cluster is a list of error labels that are similar to each other. For each cluster, you should also provide a label (CLUSTER_LABEL) that represent the errors in the cluster.

CONSTRAINTS:
No user assistance

The output (JSON_OUTPUT) should be formatted as JSON. Only provide the JSON output. Below is an example:

# ERROR_LABELS:
'''
NPM Package Fetch Error
Incompatible Bundler Version Error
Network Error
Bundler Version Error
AttributeError in Poetry Installation
Python Package Installation Error
Package Installation Error
Dependency Installation Error
ReferenceError in npm build
Network Timeout Error
Package Fetch Error
Package Download Error
Network Connectivity Error
Dependency retrieval error
Package Repository Error
Repository Not Found Error
Dependency Error
Dependency Resolution Error
Download Error
Certificate Verification Error
'''

# JSON_OUTPUT:
'''
{
"clusters": [
    {
        "label": "Package Installation Error",
        "errors": [
            "NPM Package Fetch Error",
            "Package Fetch Error",
            "Package Download Error",
            "Package Repository Error",
            "Python Package Installation Error",
            "Dependency Installation Error",
        ]
    },
    {
        "label": "Network Error",
        "errors": [
            "Network Connectivity Error",
            "Network Error",
            "Network Timeout Error"
        ]
    },
    {
        "label": "Dependency Error",
        "errors": [
            "Dependency Error",
            "Dependency retrieval error",
            "Dependency Resolution Error"
        ]
    },
    {
        "label": "Bundler Version Error",
        "errors": [
            "Incompatible Bundler Version Error",
            "Bundler Version Error"
        ]
    },
    {
        "label": "Repository Not Found Error",
        "errors": [
            "Repository Not Found Error"
        ]
    },
    {
        "label": "Certificate Verification Error",
        "errors": [
            "Certificate Verification Error"
        ]
    },
    {
        "label": "AttributeError in Poetry Installation",
        "errors": [
            "AttributeError in Poetry Installation",
        ]
    },
    {
        "label": "ReferenceError in npm build",
        "errors": [
            "ReferenceError in npm build"
        ]
    },
    {
        "label": "Download Error",
        "errors": [
            "Download Error"
        ]
    }
]
}
'''
"""

GENERATE_LABEL_FROM_SUBITEMS = """
You are an AI assistant and your goal is to generate a label for a group of errors based on the errors in the group. If the list includes only one error, the label should be the same as the error. If the list includes multiple errors, the label should be a representative label that captures the essence of the errors in the list.

GOAL: Given a list of intial error labels (ERROR_LABELS), your task is to understand the errors and generate a label (CLUSTER_LABEL) that represent the errors in the list.

CONSTRAINTS:
No user assistance

The output (OUTPUT) should be a string that represents the label for the group of errors. Below is an example:

# ERROR_LABELS:
'''
"Package Installation Failure",
"Package Installation TypeError",
"Package Installation Error",
"Local Package Installation Error",
"Python Package Installation Error",
"Python Module Installation Error",
"Package Setup Error",
"Package Installation and Command Error"
'''

# OUTPUT:
'''
Package Installation Error
''' 
"""