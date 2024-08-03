def user_repair_template(dockerfile):
    return f"""
Below is the flaky Dockerfile:

# Dockerfile
{dockerfile}

Your task is to repair the Dockerfile based on Dockerfile provided. To solve the problem, first, you should diagnose which part is causing the flakiness. Anything that can cause a Dockerfile show flaky behaviour during build procedure should be considered. Then, according to the characteristics of that flakiness, repair the Dockerfile. the output Dockerfile must be within five angle brackets:
<<<<<
Dockerfile content 
>>>>>
"""   

def user_repair_template_with_build_info(dockerfile, build_error):
    user_template = f"""
Below is the flaky Dockerfile:

# Dockerfile
```{dockerfile}```

And below is the build error that occurred when trying to build the Dockerfile:
# Build Error
```{build_error}```

"""

    user_template += f"""Your task is to repair the Dockerfile based on the Dockerfile and its build error provided. To solve the problem, first, you should diagnose which part is causing the flakiness and why. Then, according to the characteristics of that flakiness, repair the Dockerfile. the output Dockerfile must be within five angle brackets:
    <<<<<
    Dockerfile content 
    >>>>>
"""
    return user_template


def user_repair_template_and_similar_shots(dockerfile, build_error, shots):
    return f""""""


def user_repair_template_with_build_info_and_similar_shots(dockerfile, build_error, shots):
    user_template = f"""
Below is the flaky Dockerfile:

# Dockerfile
{dockerfile}

And below is the build error that occurred when trying to build the Dockerfile:
# Build Error
{build_error}

Below are a few examples of dockerfiles and their build errors alongside repair/suggestion required. These examples are provided to help you understand the task better.
"""
    for i, shot in enumerate(shots):
        user_template += f"""
# Example {i+1}
## Example Dockerfile
{shot['dockerfile']}

## Example Build Error
{shot['build_error']}

## Example Code Change/Suggestion
"""
        if "suggestion" in shot:
            user_template += f"""
### Suggestion
{shot['suggestion']}
"""
        else:
            num_of_repairs = shot.get("num_of_repairs", 1)
            for r in range(num_of_repairs):
                user_template += f"""
### Repair {r+1}
{shot['repair' + str(r+1)]}
"""

    user_template += f"""Your task is to repair the Dockerfile based on the Dockerfile and its build error provided alongside the examples provided for you for as demonstrations. To solve the problem, first, you should diagnose which part is causing the flakiness and why. Then, according to the characteristics of that flakiness, if you are able to repair the Dockerfile, provide the corrected Dockerfile. Otherwise, if you are not able to repair the Dockerfile due to the nature of the error, suggest a way to repair the Dockerfile. Your suggestion should include a maximum of 120 words describing the possible solutions on and how to fix it.
"""
    return user_template

def user_repair_template_with_build_output_and_similar_shots_and_feedback(dockerfile, build_error, shots, feedbacks):
    user_template = f"""
Below is the flaky Dockerfile:

# Dockerfile
```{dockerfile}```

And below is the build error that occurred when trying to build the Dockerfile:
# Build Error
```{build_error}```

Below are a few examples of dockerfiles and their build errors alongside their repairs. These examples are provided to help you understand the task better.
"""
    for i, shot in enumerate(shots):
        user_template += f"""
# Example {i+1}
## Example Dockerfile
```{shot.dockerfile}```

## Example Build Error
```{shot.build_output}```

## Example Repair
"""
        
        for j, repair in enumerate(shot.repair):
            user_template += f"""
### Repair {j+1}
```{repair}```

"""
    
    if (len(feedbacks) > 0):
        user_template += f"""Below are a few false repairs that an LLM previously made by mistake for the input flaky Dockerfile along with their build outputs as further demonstrations. These examples are provided to help you understand the task better and to avoid making the same mistakes. So, do not generate the exact false repair generated previously, but you can get ideas from them.
"""

        for i, feedback in enumerate(feedbacks):
            user_template += f"""
# False Repair {i+1}
## False Repair Dockerfile
```{feedback.dockerfile}```

## False Repair Build Output
```{feedback.build_output}```

"""

    user_template += f"""Your task is to repair the Dockerfile based on the Dockerfile and its build error provided alongside the examples provided for you for as demonstrations. To solve the problem, and based on the information provided, first, you should diagnose which part is causing the flakiness and why. Then, according to the characteristics of that flakiness, repair the Dockerfile. the output Dockerfile must be within five angle brackets:
    <<<<<
    Dockerfile content 
    >>>>>
"""
    return user_template

def user_repair_template_with_build_output_and_similar_shots_and_feedback(dockerfile, build_error, shots, feedbacks):
    user_template = f"""
Below is the flaky Dockerfile:

# Dockerfile
```{dockerfile}```

And below is the build error that occurred when trying to build the Dockerfile:
# Build Error
```{build_error}```

Below are a few examples of dockerfiles and their build errors alongside their repairs. These examples are provided to help you understand the task better.
"""
    for i, shot in enumerate(shots):
        user_template += f"""
# Example {i+1}
## Example Dockerfile
```{shot.dockerfile}```

## Example Build Error
```{shot.build_output}```

## Example Repair
"""
        
        for j, repair in enumerate(shot.repair):
            user_template += f"""
### Repair {j+1}
```{repair}```

"""
    
    if (len(feedbacks) > 0):
        user_template += f"""Below are a few false repairs that an LLM previously made by mistake for the input flaky Dockerfile along with their build outputs as further demonstrations. These examples are provided to help you understand the task better and to avoid making the same mistakes. So, do not generate the exact false repair generated previously, but you can get ideas from them.
"""

        for i, feedback in enumerate(feedbacks):
            user_template += f"""
# False Repair {i+1}
## False Repair Dockerfile
```{feedback.dockerfile}```

## False Repair Build Output
```{feedback.build_output}```

"""

    user_template += f"""Your task is to repair the Dockerfile based on the Dockerfile and its build error provided alongside the examples provided for you for as demonstrations. To solve the problem, and based on the information provided, first, you should diagnose which part is causing the flakiness and why. Then, according to the characteristics of that flakiness, repair the Dockerfile. the output Dockerfile must be within five angle brackets:
    <<<<<
    Dockerfile content 
    >>>>>
"""
    return user_template