import aws_cdk as core
import aws_cdk.assertions as assertions

from run_app_aws.run_app_aws_stack import RunAppAwsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in run_app_aws/run_app_aws_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RunAppAwsStack(app, "run-app-aws")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
