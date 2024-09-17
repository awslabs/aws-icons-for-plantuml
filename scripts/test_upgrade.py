from upgrade import process_include, process_line, SUPPORTED_VERSIONS

# pylint: disable=C0116,C0103

def test_process_include_no_match():
    line = "!include https://example.com/icons.puml\n"
    result = process_include(line, SUPPORTED_VERSIONS)
    assert result is None

def test_process_include_MigrationTransfer_renamed():
    before = "!include AWSPuml/MigrationTransfer/all.puml\n"
    after  = "!include AWSPuml/MigrationModernization/all.puml\n"

    result = process_include(before, SUPPORTED_VERSIONS)
    assert result == after

def test_process_include_VRAR_removed():
    """
    v13.0 ARVR category was replaced by VRAR
    v16.0 VRAR category was removed
    """
    before = "!include AWSPuml/ARVR/all.puml\n"
    after  = "' !include AWSPuml/VRAR/all.puml ' removed in v16.0\n"

    result = process_include(before, SUPPORTED_VERSIONS)
    assert result == after

def test_process_include_APIGateway_moved():
    before = "!include AWSPuml/ApplicationIntegration/APIGateway.puml\n"
    after  = "!include AWSPuml/NetworkingContentDelivery/APIGateway.puml\n"

    result = process_include(before, SUPPORTED_VERSIONS)
    assert result == after

def test_process_include_WorkSpaces_moved():
    """
    v14.0 WorkSpacesWorkSpacesWeb was replaced by WorkSpacesWeb
    v15.0 WorkSpacesWeb was replaced by WorkSpacesFamilyAmazonWorkSpacesWeb
    v19.0 WorkSpacesFamilyAmazonWorkSpacesWeb was replaced by WorkSpacesFamilyAmazonWorkSpacesSecureBrowser
    """
    before = "!include AWSPuml/EndUserComputing/WorkSpacesWorkSpacesWeb.puml\n"
    after  = "!include AWSPuml/EndUserComputing/WorkSpacesFamilyAmazonWorkSpacesSecureBrowser.puml\n"

    result = process_include(before, SUPPORTED_VERSIONS)
    assert result == after


def test_process_line_SimpleStorageServiceBucketIMG_renamed():
    before = """participant "$SimpleStorageServiceBucketIMG()\nAmazon S3\nbucket" as s3"""
    after  = """participant "$SimpleStorageServiceGeneralpurposebucketIMG()\nAmazon S3\nbucket" as s3"""

    result = process_line(before, SUPPORTED_VERSIONS)
    assert result == after

def test_process_line_SimpleStorageServiceBucket_renamed():
    before = """$AWSIcon(SimpleStorageServiceBucket, "Bucket", "Amazon S3") as s3 <<Multi-Tenant>>"""
    after  = """$AWSIcon(SimpleStorageServiceGeneralpurposebucket, "Bucket", "Amazon S3") as s3 <<Multi-Tenant>>"""

    result = process_line(before, SUPPORTED_VERSIONS)
    assert result == after

def test_process_line_AWS_COLOR_PURPLE_renamed():
    before = """    activate cf AWS_COLOR_PURPLE"""
    after  = """    activate cf $AWS_COLOR_GALAXY"""

    result = process_line(before, SUPPORTED_VERSIONS)
    assert result == after

def test_process_line_AWS_BG_COLOR_renamed():
    before = """    BackgroundColor AWS_BG_COLOR"""
    after  = """    BackgroundColor $AWS_BG_COLOR"""

    result = process_line(before, SUPPORTED_VERSIONS)
    assert result == after

def test_process_line_AWS_BG_COLOR_not_renamed():
    before = """    BackgroundColor $AWS_BG_COLOR"""

    result = process_line(before, SUPPORTED_VERSIONS)
    assert result is None