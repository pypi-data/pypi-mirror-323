*** Settings ***
Documentation       Acceptance Tests for Envoy Program
Resource            keywords.resource

*** Test Cases ***
Show help output
    [Documentation]    Tests that the help documentation is shown correctly when requested
    ${output}=    Run Envoy   ${EMPTY}    ${EMPTY}    --help 
    Should Contain    ${output.stdout}    Usage: python -m envoy
    Should Be Equal As Integers    ${output.rc}    0

Valid env file
    [Documentation]    Test that an env file that is valid in every way returns no errors
    ${output}=    Run Envoy    tests/assets/001_env_valid.env    tests/assets/001.env.example    --warn-additional-keys --warn-uninitialised-keys
    Should Contain    ${output.stdout}    No additional keys found
    Should Contain    ${output.stdout}    No differences found
    Should Contain    ${output.stdout}    No uninitialised keys found
    Should Contain    ${output.stdout}    Checking complete, no errors found!
    Should Be Equal As Integers    ${output.rc}    0

Uninitialised keys (with flag)
    [Documentation]    Test that uninitialised keys are detected, when the appropriate flag is set
    ${output}=    Run Envoy    tests/assets/001_unset_vars.env    tests/assets/001.env.example    --warn-uninitialised-keys
    Should Contain    ${output.stdout}    No differences found
    Should Contain    ${output.stdout}    Provided env file has uninitialised key 'TEST_1'
    Should Contain    ${output.stdout}    Provided env file has uninitialised key 'TEST_2'
    Should Contain    ${output.stdout}    Checking complete with warnings found
    Should Be Equal As Integers    ${output.rc}    0
 
Uninitialised keys (without flag)
    [Documentation]    Test that uninitialised keys are not detected, when the appropriate flag is unset
    ${output}=    Run Envoy    tests/assets/001_unset_vars.env    tests/assets/001.env.example    ${EMPTY}
    Should Contain    ${output.stdout}    No differences found
    Should Not Contain    ${output.stdout}    Provided env file has uninitialised key 'TEST_1'
    Should Not Contain    ${output.stdout}    Provided env file has uninitialised key 'TEST_2'
    Should Contain    ${output.stdout}    Checking complete, no errors found!
    Should Be Equal As Integers    ${output.rc}    0

Missing keys
    [Documentation]    Test that missing keys are correctly detected
    ${output}=    Run Envoy    tests/assets/001_missing_test_1.env    tests/assets/001.env.example    ${EMPTY}
    Should Not Contain    ${output.stdout}    No differences found
    Should Contain    ${output.stdout}    Provided env file is missing attribute 'TEST_1' which is in the example file
    Should Not Contain    ${output.stdout}    Provided env file is missing attribute 'TEST_2' which is in the example file
    Should Contain    ${output.stdout}    Checking complete with errors found
    Should Be Equal As Integers    ${output.rc}    1

    ${output}=    Run Envoy    tests/assets/001_missing_test_2.env    tests/assets/001.env.example    ${EMPTY}
    Should Not Contain    ${output.stdout}    No differences found
    Should Contain    ${output.stdout}    Provided env file is missing attribute 'TEST_2' which is in the example file
    Should Not Contain    ${output.stdout}    Provided env file is missing attribute 'TEST_1' which is in the example file
    Should Contain    ${output.stdout}    Checking complete with errors found
    Should Be Equal As Integers    ${output.rc}    1

Additional args (with flag)
    [Documentation]    Test that additional args are detected, when the appropriate flag is set
    ${output}=    Run Envoy    tests/assets/001_missing_additional_args.env    tests/assets/001.env.example    --warn-additional-keys
    Should Contain    ${output.stdout}    No differences found
    Should Contain    ${output.stdout}    Provided env file had additional attribute 'TEST_3' which is not in the example file
    Should Contain    ${output.stdout}    Checking complete with warnings found
    Should Be Equal As Integers    ${output.rc}    0

Additional args (without flag)
    [Documentation]    Test that additional args are not detected, when the appropriate flag is unset
    ${output}=    Run Envoy    tests/assets/001_missing_additional_args.env    tests/assets/001.env.example    ${EMPTY}
    Should Contain    ${output.stdout}    No differences found
    Should Not Contain    ${output.stdout}    Provided env file had additional attribute
    Should Contain    ${output.stdout}    Checking complete, no errors found!
    Should Be Equal As Integers    ${output.rc}    0

Env vars in comments
    [Documentation]    Test that env vars listed in comments are not detected
    ${output}=    Run Envoy    tests/assets/001_env_in_comment.env    tests/assets/001.env.example    ${EMPTY}
    Should Contain    ${output.stdout}    No differences found
    Should Contain    ${output.stdout}    Checking complete, no errors found!
    Should Be Equal As Integers    ${output.rc}    0