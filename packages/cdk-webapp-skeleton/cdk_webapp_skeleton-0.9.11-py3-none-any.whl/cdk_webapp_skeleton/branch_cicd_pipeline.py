import aws_cdk as cdk
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codestarnotifications as codestarnotifications
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subscriptions
from aws_cdk import pipelines as pipelines
from constructs import Construct

from .branch_config import BranchConfig


class BranchCICDPipeline(Construct):
    def __init__(self, scope: Construct, branch_config: BranchConfig):
        super().__init__(scope, "BranchCICDPipeline")

        cache_bucket = s3.Bucket(
            scope,
            "CacheBucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        artifact_bucket = s3.Bucket(
            scope,
            "ArtifactBucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        synth_step = pipelines.CodeBuildStep(
            "Synth",
            input=branch_config.source,
            commands=["./synth.sh"],
            env={
                "BRANCH": branch_config.branch_name,
            },
            role_policy_statements=[
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=["*"],
                    conditions={
                        "StringEquals": {
                            "iam:ResourceTag/aws-cdk:bootstrap-role": "lookup"
                        }
                    },
                ),
                iam.PolicyStatement(
                    actions=["elasticloadbalancing:DescribeRules"],
                    resources=["*"],
                ),
            ],
        )

        self.cdk_pipeline = pipelines.CodePipeline(
            scope,
            "Pipeline",  # Pipeline name gets the stack name prepended
            synth=synth_step,
            artifact_bucket=artifact_bucket,
            docker_credentials=[
                pipelines.DockerCredential.ecr(
                    [
                        ecr.Repository.from_repository_arn(
                            self,
                            "Repo",
                            # TODO: generalize
                            "arn:aws:ecr:us-east-1:819618805794:repository/docker-hub/ilyanekhay/poetry",
                        )
                    ]
                )
            ],
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    compute_type=codebuild.ComputeType.SMALL,
                    build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                ),
                cache=codebuild.Cache.bucket(cache_bucket),
                role_policy=[
                    iam.PolicyStatement(
                        actions=[
                            "ecr:GetAuthorizationToken",
                            "ecr:BatchGetImage",
                            "ecr:BatchCheckLayerAvailability",
                            "ecr:GetDownloadUrlForLayer",
                            "ecr:DescribeRepositories",
                            "ecr:GetRepositoryPolicy",
                            "ecr:ListImages",
                            "ecr:DescribeImages",
                            "ecr:BatchImportUpstreamImage",
                        ],
                        resources=["*"],
                    )
                ],
            ),
            cross_account_keys=False,
            publish_assets_in_parallel=True,
        )

        self.alarm_topic = sns.Topic(scope, "AlarmTopic")
        if branch_config.notify_email is not None:
            self.alarm_topic.add_subscription(
                subscriptions.EmailSubscription(branch_config.notify_email)
            )

    def add_stage(self, stage: cdk.Stage) -> pipelines.StageDeployment:
        return self.cdk_pipeline.add_stage(stage)

    def build_pipeline(self) -> None:
        self.cdk_pipeline.build_pipeline()

        self.cdk_pipeline.pipeline.notify_on_execution_state_change(
            "PipelineNotify",
            self.alarm_topic,
            detail_type=codestarnotifications.DetailType.FULL,
        )
