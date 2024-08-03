## Check stats for docker error parser

```
python docker_error_parser_stats.py
```

Output should be something like this:

```
token_count_file_name_stats...
count    12964.000000
mean        33.017973
std          2.708822
min         27.000000
25%         31.000000
50%         33.000000
75%         35.000000
max         46.000000
dtype: float64
............................................
token_count_error_segment_stats...
count    12964.000000
mean       591.448087
std        740.352352
min          0.000000
25%        256.000000
50%        410.000000
75%        601.000000
max      11647.000000
dtype: float64
............................................
token_count_dockerfile_error_line_stats...
count    12964.000000
mean        82.427646
std        180.614139
min          0.000000
25%         11.000000
50%         25.000000
75%         82.000000
max       3918.000000
dtype: float64
............................................
token_count_dockerfile_segment_stats...
count    1684.000000
mean      231.004751
std       428.138861
min         4.000000
25%        24.000000
50%        95.500000
75%       247.250000
max      5213.000000
dtype: float64
............................................
token_count_stderr_stats...
count    12964.000000
mean        96.995372
std        163.860143
min          0.000000
25%         29.000000
50%         46.000000
75%         96.000000
max       3696.000000
dtype: float64
............................................
token_count_exit_code_stats...
count    12964.000000
mean         1.494678
std          2.892753
min          0.000000
25%          1.000000
50%          1.000000
75%          1.000000
max         94.000000
dtype: float64
............................................
token_count_stats for the complete error json file...
count    12964.000000
mean       872.111694
std       1008.040464
min         88.000000
25%        418.000000
50%        591.000000
75%        949.500000
max      19100.000000
dtype: float64
............................................
An example of token usage:
Tokens Used: 894
	Prompt Tokens: 790
	Completion Tokens: 104
Successful Requests: 1
Total Cost (USD): $0.0013930000000000001
```
