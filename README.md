<!--
Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-plantuml-icons/blob/main/LICENSE)
-->

# AWS Icons for PlantUML

PlantUML sprites, macros, and other includes for Amazon Web Services (AWS) services and resources. Used to create PlantUML diagrams with AWS components. All elements are generated from the official [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) and when combined with [PlantUML](http://plantuml.com/) and the [C4 model](https://c4model.com/), are a great way to communicate your design, deployment, and topology as code.

Besides usage as custom sprites on PlantUML components, different types of diagrams can quickly and easily be created with the icons.

This repository is based on the [Azure-PlantUML](https://github.com/RicardoNiepel/Azure-PlantUML) repository for creating patterns used in quality diagrams. Thanks Ricardo!

## Table of Contents

<!-- toc -->

- [Getting Started](#getting-started)
  - [Hello World](#hello-world)
- [Examples](#examples)
  - [Basic Usage](#basic-usage)
  - [Raw Sprites](#raw-sprites)
  - [Simplified View](#simplified-view)
  - [Sequence Diagrams](#sequence-diagrams)
- [Distribution "Dist" Details](#distribution-dist-details)
- [Advanced Examples](#advanced-examples)
- [Customized Builds](#customized-builds)
- [Contributing](#contributing)
- [License Summary](#license-summary)
- [Acknowledgements](#acknowledgements)

<!-- tocstop -->

## Getting Started

In order to incorporate and use the _AWS Icons for PlantUML_ resources, `!include` statements are added to your diagrams. A common include file/URL defines the base colors, styles, and characteristics for the diagram. Then additional configuration files can be added to further customize the diagram, followed by the elements used in the diagram.

To get started, include the `AWSCommon.puml` file from the `dist` directory in each `.puml` file or PlantUML diagram. This can be referenced by a URL directly to this repository, or by including the file locally. To use this repository, use the following:

<pre><code>!includeurl https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/<b>v10.0</b>/dist/AWSCommon.puml
</code></pre>

or this if defining the URL:

<pre><code>!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/<b>v10.0</b>/dist
</code></pre>

This references the latest _GitHub release_ version of the referenced file from GitHub when an Internet connection is available. It is recommended _not_ to use the `main` branch, but instead a specific release version. The examples below reference the current _v10.0_ release.

All examples reference _main_ and are designed with the most recent files. For consistency of UML diagrams when referencing the files directly via GitHub and not generated locally, it is recommended to use a specific release version.

For local access use `!include` instead of `!includeurl` and include the path to the file's location:

```bash
!include path/to/AWSCommon.puml
```

:exclamation: The `!includeurl` is deprecated in recent versions of PlantUML. Now `!include` can be used with local file paths _or_ URLs. Please see the [Preprocessing](http://plantuml.com/preprocessing) notes for usage.

After inclusion of the `AWSCommon.puml` file, there are two different ways to reference resources:

1. **Use individual include files** - Use one file per service or setting. For example:

   `!include AWSPuml/Storage/AmazonSimpleStorageService.puml`

1. **Use category include file** - Single include that contains all services and resources for that category. For example:

   `!include AWSPuml/BusinessApplications/all.puml`

All of the services can be found in the `dist/` directory, which includes the service or product categories and the corresponding `puml` files.

For example, including these files from the repository (URL), the includes would look like this:

```bash
' Define the main location (URL or local file path)
!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v10.0/dist
' Include main AWSCommon and then sprite files
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/BusinessApplications/all.puml
!includeurl AWSPuml/Storage/SimpleStorageServiceS3.puml
```

This defines the macro `AWSPuml` to point to the root of the `dist/` directory, which reduces the size of the include statements. Next the `AWSCommon.puml` file is loaded, and then the actual resource files. In this example, all of the entities in the _BusinessApplications_ directory are added, and then only the _AmazonSimpleStorageServiceS3_ entity from the _Storage_ directory.

:exclamation: All examples reference the main _branch_ of this repository. It is recommended that one of the release tags be used for documents. New releases will be created when AWS updates the AWS Architecture Icons. The release tag will be similar to the release date from AWS.

### Hello World

This is the [`examples/HelloWorld.puml`](examples/HelloWorld.puml) diagram code:

```plantuml
@startuml Hello World

!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v10.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/EndUserComputing/all.puml
!includeurl AWSPuml/Storage/SimpleStorageService.puml

actor "Person" as personAlias
WorkDocs(desktopAlias, "Label", "Technology", "Optional Description")
SimpleStorageService(storageAlias, "Label", "Technology", "Optional Description")

personAlias --> desktopAlias
desktopAlias --> storageAlias

@enduml
```

This code generates the following diagram:

![](http://www.plantuml.com/plantuml/proxy?idx=0&src=https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v10.0/examples/HelloWorld.puml)

## Examples

Below are some sample diagrams that demonstrate the uses of this repository by using different styles. The images are generated from the source diagram in the `examples` directory, which reference the PUML files in the `dist` directory of the main branch of this repository..

Consider these as starting points for how to use the resources in your own documents and diagrams. You may wish to use the sprites (images) in your UML diagrams, use the rectangle entities, or create large and complex C4 model diagrams.

### Basic Usage

This example shows AWS IoT processing of messages via the Rules Engine with an error action. It utilizes AWS service entities to show a simple architecture workflow. Each entity has a unique entity name and icon (`<<foo..>>`), name of function, and additional details or constraints.

```bash
@startuml Basic Usage - AWS IoT Rules Engine

!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v10.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/InternetOfThings/IoTRule.puml
!includeurl AWSPuml/Analytics/KinesisDataStreams.puml
!includeurl AWSPuml/ApplicationIntegration/SimpleQueueService.puml

left to right direction

agent "Published Event" as event #fff

IoTRule(iotRule, "Action Error Rule", "error if Kinesis fails")
KinesisDataStreams(eventStream, "IoT Events", "2 shards")
SimpleQueueService(errorQueue, "Rule Error Queue", "failed Rule actions")

event --> iotRule : JSON message
iotRule --> eventStream : messages
iotRule --> errorQueue : Failed action message

@enduml
```

This code generates the following diagram:

![](http://www.plantuml.com/plantuml/proxy?idx=0&src=https%3A%2F%2Fraw.githubusercontent.com%2Fawslabs%2Faws-icons-for-plantuml%2Fv10.0%2Fexamples%2FBasic%2520Usage.puml)

### Raw Sprites

The individual icon sprites (complete list [here](AWSSymbols.md)) can be included in all diagrams. Here are few examples showing sprite usage on different entities (component, database, and AWS PlantUML).

```bash
@startuml Raw usage - Sprites

!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v10.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/MachineLearning/SageMakerModel.puml
!includeurl AWSPuml/Robotics/RoboMaker.puml

component "<color:green><$SageMakerModel></color>" as myMLModel
database "<color:#232F3E><$RoboMaker></color>" as myRoboticService
RoboMaker(mySecondFunction, "Reinforcement Learning", "Gazebo")

rectangle "<color:AWS_SYMBOL_COLOR><$SageMakerModel></color>" as mySecondML

myMLModel --> myRoboticService
mySecondFunction --> mySecondML

@enduml
```

This code generates the following diagram:

![](http://www.plantuml.com/plantuml/proxy?idx=0&src=https%3A%2F%2Fraw.githubusercontent.com%2Fawslabs%2Faws-icons-for-plantuml%2Fv10.0%2Fexamples%2FRaw%2520Sprite%2520Usage.puml)

### Simplified View

In some cases, PlantUML diagrams may contain too much information, but are still usable for executive or higher level conversations. Using the `AWSSimplified.puml` file filters out a lot of the technical details, while keeping the interactions between entities. Here is an example of a technical view and simplified view. To generate the simplified view, uncomment the `!includeurl` statement and regenerate the image.

```bash
@startuml Two Modes - Technical View

!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v10.0/dist
!includeurl AWSPuml/AWSCommon.puml

' Uncomment the following line to create simplified view
' !includeurl AWSPuml/AWSSimplified.puml

!includeurl AWSPuml/General/Users.puml
!includeurl AWSPuml/ApplicationIntegration/APIGateway.puml
!includeurl AWSPuml/SecurityIdentityCompliance/Cognito.puml
!includeurl AWSPuml/Compute/Lambda.puml
!includeurl AWSPuml/Database/DynamoDB.puml

left to right direction

Users(sources, "Events", "millions of users")
APIGateway(votingAPI, "Voting API", "user votes")
Cognito(userAuth, "User Authentication", "jwt to submit votes")
Lambda(generateToken, "User Credentials", "return jwt")
Lambda(recordVote, "Record Vote", "enter or update vote per user")
DynamoDB(voteDb, "Vote Database", "one entry per user")

sources --> userAuth
sources --> votingAPI
userAuth <--> generateToken
votingAPI --> recordVote
recordVote --> voteDb

@enduml
```

This code generates the following diagram:

![](http://www.plantuml.com/plantuml/proxy?idx=0&src=https%3A%2F%2Fraw.githubusercontent.com%2Fawslabs%2Faws-icons-for-plantuml%2Fv10.0%2Fexamples%2FTwo%2520Modes%2520-%2520Technical%2520View.puml)

And if the `!includeurl AWSPuml/AWSSimplified.puml`is uncommented, this simplified view is created:

![](http://www.plantuml.com/plantuml/proxy?idx=0&src=https%3A%2F%2Fraw.githubusercontent.com%2Fawslabs%2Faws-icons-for-plantuml%2Fv10.0%2Fexamples%2FTwo%2520Modes%2520-%2520Simple%2520View.puml)

### Sequence Diagrams

Icons can also be used in UML sequence diagrams, either in full stereotype or by just using sprites and formatting via `participant` description. Here are examples of both.

```bash
@startuml Sequence Diagram - Spots and stereotypes

!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v10.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/Compute/all.puml
!includeurl AWSPuml/ApplicationIntegration/APIGateway.puml
!includeurl AWSPuml/General/Internetalt1.puml
!includeurl AWSPuml/Database/DynamoDB.puml

actor User as user
APIGatewayParticipant(api, Credit Card System, All methods are POST)
LambdaParticipant(lambda,AuthorizeCard,)
DynamoDBParticipant(db, PaymentTransactions, sortkey=transaction_id+token)
Internetalt1Participant(processor, Authorizer, Returns status and token)

user -> api: Process transaction\nPOST /prod/process
api -> lambda: Invokes lambda with cardholder details
lambda -> processor: Submit via API token\ncard number, expiry, CID
processor -> processor: Validate and create token
processor -> lambda: Returns status code and token
lambda -> db: PUT transaction id, token
lambda -> api: Returns\nstatus code, transaction id
api -> user: Returns status code

@enduml
```

This code generates the fully detailed diagram with stereotypes. The participants follow the spot letter and stereotype formatting, with the icon to the left of the description.

![Technical View Sequence Diagram](http://www.plantuml.com/plantuml/proxy?idx=0&src=https%3A%2F%2Fraw.githubusercontent.com%2Fawslabs%2Faws-icons-for-plantuml%2Fv10.0%2Fexamples%2FSequence%2520-%2520Technical.puml)

```bash
@startuml Sequence Diagram - Sprites

!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v10.0/dist
!includeurl AWSPuml/AWSCommon.puml
!includeurl AWSPuml/Compute/all.puml
!includeurl AWSPuml/ApplicationIntegration/APIGateway.puml
!includeurl AWSPuml/General/Internetalt1.puml
!includeurl AWSPuml/Database/DynamoDB.puml

'Comment out to use default PlantUML sequence formatting
skinparam participant {
    BackgroundColor AWS_BG_COLOR
    BorderColor AWS_BORDER_COLOR
}
'Hide the bottom boxes
hide footbox

actor User as user
'Instead of using ...Participant(), native sprites can be used in monochrome
participant "<$APIGateway>\nCredit Card System\nAll methods are POST" as api
'Or skinned with colors (pulled from each sprite file) and with different layout of sprite to text
participant "<color:#D86613><$Lambda></color>\nAuthorizeCard\nReturns status" as lambda
participant "PaymentTransactions\n<color:#3B48CC><$DynamoDB></color>\nsortkey=transaction_id+token" as db
participant "Authorizer\nReturns status and token\n<color:#232F3E><$Internetalt1></color>" as processor

user -> api: Process transaction\nPOST /prod/process
api -> lambda: Invokes lambda with cardholder details
lambda -> processor: Submit via API token\ncard number, expiry, CID
processor -> processor: Validate and create token
processor -> lambda: Returns status code and token
lambda -> db: PUT transaction id, token
lambda -> api: Returns\nstatus code, transaction id
api -> user: Returns status code

@enduml
```

This code generates the same sequence diagram demonstrating how text and icon (sprite) positioning can be modified.

![Sprite View Sequence Diagram](http://www.plantuml.com/plantuml/proxy?idx=0&src=https%3A%2F%2Fraw.githubusercontent.com%2Fawslabs%2Faws-icons-for-plantuml%2Fv10.0%2Fexamples%2FSequence%2520-%2520Sprites.puml)

## Distribution "Dist" Details

All images, filenames, and content are provided from Amazon Web Services (AWS).

To reduce the length of the filename and ultimately the PUML file details, the leading _Amazon_ or _AWS_ have been removed from the product or service icon.

Beyond that, starting with the _v10.0_ release, all filenames now follow the original icon names provided by AWS. While this makes the [AWS Symbols](AWSSymbols.md) more difficult to view, this will reduce curation of new releases. It is recommended to use a versions release tag when referencing this repository instead of the `main` branch.

## Advanced Examples

This section will contain examples that map [AWS References Architectures](https://aws.amazon.com/architecture/#AWS_reference_architectures) from the [AWS Architecture Center](https://aws.amazon.com/architecture/). Focus will be on providing examples that not only describe the different components, but also how to use containers for referencing items such as VPCs, subnets, or groups of EC2 instances.

Other examples will focus on using the [Plant-UML C4 model](https://github.com/RicardoNiepel/C4-PlantUML) for expressing solution architectures.

Stay tuned!

## Customized Builds

It is also possible to customize the creation of the `dist/` PUML and PNG files. All details can be found in the [Generating the _PlantUML Icons for AWS_ distribution documentation](scripts/README.md).

## Contributing

Please see the `CONTRIBUTING.md` file for details on how to contribute.

The following, in alphabetical order by name or GitHub username, have contributed to this repository:

- [jack-burridge-tp](https://github.com/jack-burridge-tp) - Added support for Sequence Diagrams

## License Summary

The icons provided in this package are made available to you under the terms of the CC-BY-ND 2.0 license, available in the `LICENSE` file. Code is made available under the MIT license in `LICENSE-CODE`.

## Acknowledgements

- [PlantUML](http://plantuml.com/index) - Thank you for the ability to create technical diagrams by writing lines of code/text.
- [AWS-PlantUML](https://github.com/milo-minderbinder/AWS-PlantUML) - Thank you for the base structure and understanding how to incorporate new sprites into Plant-UML.
- [Azure-PlantUML](https://github.com/RicardoNiepel/Azure-PlantUML) - Thank you Ricardo for the elegant look and feel of the repository, diagrams, and the C4 Model.
- [C4 Model](https://c4model.com/) - Thanks you for an approach to document solutions without the specificity of UML.
