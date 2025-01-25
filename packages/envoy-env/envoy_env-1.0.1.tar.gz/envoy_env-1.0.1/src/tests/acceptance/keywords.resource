*** Settings ***
Documentation    Resource file for Envoy acceptance tests
Library          KeywordLibrary.py
Library          Process

*** Keywords ***
Run Envoy
    [Documentation]    Runs the envoy program with given arguments
    [Arguments]    ${env_file}    ${example_file}    ${args}
    ${result}=    Run Process
    ...    uv run python -m envoy ${env_file} ${example_file} ${args}
    ...    shell=True
    ...    cwd=../../
    Log    ${result.stdout}
    RETURN    ${result}