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

```Dockerfile
FROM ruby:2.7
...
COPY Gemfile Gemfile.lock /app/
RUN cd /app && gem install bundler && bundle install
```

### Build output

```log
#1 ... -> stage1
------
#2 ... -> stage2
------
...
------
#10 [5/5] RUN cd /app && gem install bundler && bundle install -> stage10
#10 27.78 ERROR:  Error installing bundler:
#10 27.78 	The last version of bundler (>= 0) to support your Ruby & RubyGems was 2.4.22. Try installing it with `gem install bundler -v 2.4.22`
#10 27.78 	bundler requires Ruby version >= 3.0.0. The current ruby version is 2.7.8.225.
#10 ERROR: process "/bin/sh -c cd /app && gem install bundler && bundle install" did not complete successfully: exit code: 1
------
 > [5/5] RUN cd /app && gem install bundler && bundle install:
27.78 ERROR:  Error installing bundler:
27.78 	The last version of bundler (>= 0) to support your Ruby & RubyGems was 2.4.22. Try installing it with `gem install bundler -v 2.4.22`
27.78 	bundler requires Ruby version >= 3.0.0. The current ruby version is 2.7.8.225.
------
Dockerfile:18
--------------------
  16 |     COPY Gemfile Gemfile.lock /app/
  17 |
  18 | >>> RUN cd /app && gem install bundler && bundle install
  19 |
--------------------
ERROR: failed to solve: process "/bin/sh -c cd /app && gem install bundler && bundle install" did not complete successfully: exit code: 1 ->stderr
```
