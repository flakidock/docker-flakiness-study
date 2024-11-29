# Build Output Pre-Processing

Our raw build output contains both `STDOUT` and `STDERR`, alongside the line of Dockerfile in which the error triggers.
The first step of our pre-processing phase is splitting the build output into `stages`, each corresponding to an execution step in the Dockerfile. Then for each stage, we extract the lines with error-related keywords, along with adjacent lines sharing the same execution time, to provide additional context for diagnosing failures.

Below is the list of error-related keywords:

```python
ERROR_KEYWORDS = ["Error:", "Error ", "Err:", "E:", "W:", "NameError", "ERR!", "[ERROR]", "Error]", "ParseError", "FetchError", "[Error"]
```

As a running example, we provide a Dockerfile and its build output format.
each line within the build output is denoted with structure:
`#<stage-number> <execution-time> <log_information>`, as an example `#3 2.44 installing dependencies ...` shows stage 3, 2.44 seconds of execution, and log information: installing dependencies ...

### Dockerfile

See [the original Dockerfile](sample-dockerfile), for further information.

```Dockerfile
FROM dreamfactorysoftware/df-base-img:ubuntu-20
...
# Install packages
RUN composer install --no-dev --ignore-platform-reqs && \
    php artisan df:env --db_connection=sqlite --df_install=Docker && \
    chown -R www-data:www-data /opt/dreamfactory && \
    rm /etc/nginx/sites-enabled/default
COPY docker-entrypoint.sh /docker-entrypoint.sh
...
CMD ["/docker-entrypoint.sh"]


```

### Build output

See [the original Build output](sample-build-output), for further information.

```log
#1 ... -> stage 1

#2 ... -> stage 2

... -> stages 3-9

#10 [5/8] RUN composer install --no-dev --ignore-platform-reqs &&     php artisan df:env --db_connection=sqlite --df_install=Docker &&     chown -R www-data:www-data /opt/dreamfactory &&     rm /etc/nginx/sites-enabled/default -> stage 10
#10 2.070 Do not run Composer as root/super user! See https://getcomposer.org/root for details
#10 2.439 Installing dependencies from lock file
#10 2.494 Verifying lock file contents can be installed on current platform.
...
#10 52.90   [ParseError]                                                   
#10 52.90   syntax error, unexpected '|', expecting variable (T_VARIABLE)  
#10 52.90                                                                  
#10 52.90 
#10 52.90 Exception trace:
... 
52.91 install [--prefer-source] [--prefer-dist] [--prefer-install PREFER-INSTALL] [--dry-run] [--dev] [--no-suggest] [--no-dev] [--no-autoloader] [--no-progress] [--no-install] [-v|vv|vvv|--verbose] [-o|--optimize-autoloader] [-a|--classmap-authoritative] [--apcu-autoloader] [--apcu-autoloader-prefix APCU-AUTOLOADER-PREFIX] [--ignore-platform-req IGNORE-PLATFORM-REQ] [--ignore-platform-reqs] [--] [<packages>...]
52.91
------
Dockerfile:15
--------------------
  14 |     # Install packages
  15 | >>> RUN composer install --no-dev --ignore-platform-reqs && \
  16 | >>>     php artisan df:env --db_connection=sqlite --df_install=Docker && \
  17 | >>>     chown -R www-data:www-data /opt/dreamfactory && \
  18 | >>>     rm /etc/nginx/sites-enabled/default
  19 |     COPY docker-entrypoint.sh /docker-entrypoint.sh
--------------------
ERROR: failed to solve: process "/bin/sh -c composer install --no-dev --ignore-platform-reqs &&     php artisan df:env --db_connection=sqlite --df_install=Docker &&     chown -R www-data:www-data /opt/dreamfactory &&     rm /etc/nginx/sites-enabled/default" did not complete successfully: exit code: 1
```

### Pre-processed output
See [the preprocessed build output](sample-pre-processed), for further information.

```
...
In Functions.php line 17:
                                                                 
  [ParseError]                                                   
  syntax error, unexpected '|', expecting variable (T_VARIABLE)  
                                                                 
Exception trace:
    ...
```
