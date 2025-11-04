#!/usr/bin/env python3
"""
Test configuration loading and AWS connectivity.

Usage:
    python scripts/test_config.py
"""

import sys
from pathlib import Path

# Add src to path so we can import from it
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.config.logger import get_logger

logger = get_logger(__name__)


def test_config_loading():
    """Test that configuration loads correctly."""
    print("\n" + "=" * 60)
    print("Testing Configuration Loading")
    print("=" * 60)

    print(f"✅ Environment: {settings.environment}")
    print(f"✅ Log Level: {settings.log_level}")
    print(f"✅ AWS Region: {settings.aws_region}")

    if settings.aws_profile:
        print(f"✅ AWS Profile: {settings.aws_profile} (SSO)")
    elif settings.aws_access_key_id:
        print(f"✅ AWS Access Key: {settings.aws_access_key_id[:8]}... (traditional)")
    else:
        print("⚠️  No AWS credentials configured yet")

    print(f"✅ DynamoDB Table: {settings.dynamodb_state_table}")

    # Check optional settings
    optional_checks = [
        ("Anthropic API Key", settings.anthropic_api_key),
        ("Bedrock KB ID", settings.bedrock_kb_id),
        ("Blog RSS URL", settings.blog_rss_url),
        ("Letta Base URL", settings.letta_base_url),
    ]

    print("\nOptional Settings:")
    for name, value in optional_checks:
        if value:
            display = value if "http" in str(value) else f"{str(value)[:8]}..."
            print(f"  ✅ {name}: {display}")
        else:
            print(f"  ⚪ {name}: Not set (will be needed later)")

    return True


def test_aws_connectivity():
    """Test AWS credentials and connectivity."""
    print("\n" + "=" * 60)
    print("Testing AWS Connectivity")
    print("=" * 60)

    try:
        import boto3

        # Test STS (Security Token Service) - works with both SSO and keys
        print("Testing AWS credentials...")
        sts = boto3.client("sts", region_name=settings.aws_region)
        identity = sts.get_caller_identity()

        print(f"✅ AWS Account ID: {identity['Account']}")
        print(f"✅ User ARN: {identity['Arn']}")
        print(f"✅ User ID: {identity['UserId']}")

        # Test if we can list S3 buckets (basic permission check)
        print("\nTesting AWS permissions (S3 list)...")
        s3 = boto3.client("s3", region_name=settings.aws_region)
        response = s3.list_buckets()
        bucket_count = len(response.get("Buckets", []))
        print(f"✅ Can access S3: {bucket_count} buckets visible")

        return True

    except Exception as e:
        print(f"\n❌ AWS connectivity failed: {str(e)}")
        print("\nPossible solutions:")
        print("  1. If using AWS SSO:")
        print("     - Run: aws sso login --profile <your-profile-name>")
        print("     - Make sure AWS_PROFILE is set in your .env file")
        print("  2. If using access keys:")
        print("     - Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")
        print("  3. Check that AWS_REGION is correct")
        return False


def main():
    """Run all configuration tests."""
    print("\n🚀 Rumi Configuration Test")
    print("Testing environment configuration and AWS connectivity\n")

    # Test 1: Configuration loading
    try:
        config_ok = test_config_loading()
    except Exception as e:
        print(f"\n❌ Configuration loading failed: {str(e)}")
        print("\nMake sure you have a .env file with required settings.")
        sys.exit(1)

    # Test 2: AWS connectivity
    aws_ok = test_aws_connectivity()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"AWS Connectivity: {'✅ PASS' if aws_ok else '❌ FAIL'}")

    if config_ok and aws_ok:
        print("\n🎉 All tests passed! Configuration is ready.")
        sys.exit(0)
    elif config_ok and not aws_ok:
        print("\n⚠️  Configuration loaded but AWS not accessible.")
        print("This is OK for now - we'll set up AWS access when needed.")
        sys.exit(0)
    else:
        print("\n❌ Configuration issues found. Please fix and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
