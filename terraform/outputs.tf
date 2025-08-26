# Portfolio AWS Infrastructure - Outputs

# ==============================================================================
# NETWORK OUTPUTS
# ==============================================================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways"
  value       = var.enable_nat_gateway ? aws_nat_gateway.main[*].id : []
}

# ==============================================================================
# SECURITY OUTPUTS
# ==============================================================================

output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "ID of the ECS security group"
  value       = aws_security_group.ecs.id
}

# ==============================================================================
# LOAD BALANCER OUTPUTS
# ==============================================================================

output "alb_id" {
  description = "ID of the load balancer"
  value       = aws_lb.main.id
}

output "alb_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.app.arn
}

# ==============================================================================
# ECS OUTPUTS
# ==============================================================================

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

# ==============================================================================
# IAM OUTPUTS
# ==============================================================================

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

# ==============================================================================
# DYNAMODB OUTPUTS
# ==============================================================================

output "dynamodb_users_table_name" {
  description = "Name of the DynamoDB users table"
  value       = aws_dynamodb_table.users.name
}

output "dynamodb_users_table_arn" {
  description = "ARN of the DynamoDB users table"
  value       = aws_dynamodb_table.users.arn
}

output "dynamodb_metrics_table_name" {
  description = "Name of the DynamoDB metrics table"
  value       = aws_dynamodb_table.metrics.name
}

output "dynamodb_metrics_table_arn" {
  description = "ARN of the DynamoDB metrics table"
  value       = aws_dynamodb_table.metrics.arn
}

# ==============================================================================
# S3 OUTPUTS
# ==============================================================================

output "s3_bucket_name" {
  description = "Name of the S3 bucket for static website"
  value       = aws_s3_bucket.static_website.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for static website"
  value       = aws_s3_bucket.static_website.arn
}

output "s3_bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.static_website.bucket_domain_name
}

output "s3_bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket"
  value       = aws_s3_bucket.static_website.bucket_regional_domain_name
}

# ==============================================================================
# CLOUDFRONT OUTPUTS
# ==============================================================================

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.id
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.main.domain_name
}

# ==============================================================================
# CLOUDWATCH OUTPUTS
# ==============================================================================

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.arn
}

# ==============================================================================
# ECR OUTPUTS
# ==============================================================================

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.api.repository_url
}

output "ecr_repository_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.api.name
}

output "aws_account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

# ==============================================================================
# APPLICATION URLS
# ==============================================================================

output "application_url" {
  description = "URL of the application load balancer"
  value       = "http://${aws_lb.main.dns_name}"
}

output "static_website_url" {
  description = "URL of the static website via CloudFront"
  value       = "https://${aws_cloudfront_distribution.main.domain_name}"
}

# ==============================================================================
# SUMMARY OUTPUT
# ==============================================================================

output "deployment_summary" {
  description = "Summary of the deployed infrastructure"
  value = {
    project_name           = var.project_name
    environment            = var.environment
    region                 = var.aws_region
    vpc_id                 = aws_vpc.main.id
    application_url        = "http://${aws_lb.main.dns_name}"
    static_website_url     = "https://${aws_cloudfront_distribution.main.domain_name}"
    ecs_cluster_name       = aws_ecs_cluster.main.name
    dynamodb_users_table   = aws_dynamodb_table.users.name
    dynamodb_metrics_table = aws_dynamodb_table.metrics.name
    s3_bucket_name         = aws_s3_bucket.static_website.bucket
    ecr_repository         = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/portfolio-api"
  }
}