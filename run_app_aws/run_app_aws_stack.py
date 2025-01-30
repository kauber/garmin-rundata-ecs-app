from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput
)
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment
from constructs import Construct

class RunAppAwsStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC with public subnets
        vpc = ec2.Vpc(
            self, "RunApiVpc",
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="PublicSubnet"
                )
            ]
        )

        # Security Group for EC2
        security_group = ec2.SecurityGroup(
            self, "RunApiSecurityGroup",
            vpc=vpc,
            description="Security group for ECS EC2 instance",
            allow_all_outbound=True
        )

        # Inbound rules
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(""), # Update with your IP
            connection=ec2.Port.tcp(8000),
            description="Allow Custom TCP on 8000"
        )
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP access"
        )
        
        # Add SSH access to Security Group
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(""),  # Update with your IP
            connection=ec2.Port.tcp(22),
            description="Allow SSH access"
        )

        # ECS Cluster
        cluster = ecs.Cluster(
            self, "RunApiCluster",
            vpc=vpc,
            cluster_name="runapi-cluster"
        )

        # IAM Role for EC2
        ec2_instance_role = iam.Role(
            self, "RunApiEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
            ]
        )

        # Create an Auto Scaling Group
        asg = autoscaling.AutoScalingGroup(
            self, "RunApiASG",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            vpc=vpc,
            role=ec2_instance_role,
            security_group=security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            desired_capacity=1,  # Number of EC2 instances
            key_name="ec2-run" # beforehand, create a key pair for the EC2 instance and assign it here
        )

        # Attach the Auto Scaling Group to the ECS cluster
        cluster.add_asg_capacity_provider(
            ecs.AsgCapacityProvider(
                self, "AsgCapacityProvider",
                auto_scaling_group=asg
            )
        )

        task_execution_role = iam.Role(
            self, "RunApiTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # Attach permissions inline to the role
        task_execution_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )

        # Optionally, attach a read-only ECR policy
        task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )


        # ECS Task Definition
        task_definition = ecs.Ec2TaskDefinition(
            self, "RunApiTaskDef",
            execution_role=task_execution_role
        )

        container = task_definition.add_container(
            "RunApiContainer",
            image=ecs.ContainerImage.from_registry("767397959554.dkr.ecr.eu-central-1.amazonaws.com/run-api-repo:latest"),
            memory_limit_mib=512,
            cpu=256,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="RunApi")
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=8000, host_port=8000)
        )

        # ECS Service
        ecs_service = ecs.Ec2Service(
            self, "RunApiService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1
        )

        # S3 Bucket for Web UI
        web_ui_bucket = s3.Bucket(
            self, "RunAnalyzeWebUiBucket",
            bucket_name="run-analyze-web-ui",
            public_read_access=True,
            website_index_document="index.html",
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        s3_deployment.BucketDeployment(
            self, "DeployWebUi",
            sources=[s3_deployment.Source.asset("./web-ui")],
            destination_bucket=web_ui_bucket
        )

        CfnOutput(
            self, "WebUiBucketUrl",
            value=web_ui_bucket.bucket_website_url,
            description="URL of the S3 bucket hosting the web UI"
        )
