# Portfolio AWS Infrastructure - Variables

# ==============================================================================
# PROJECT CONFIGURATION
# ==============================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "portfolio"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

# ==============================================================================
# NETWORK CONFIGURATION
# ==============================================================================

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "enable_nat_gateway" {
  description = "Should be true to provision NAT Gateways for each of your private networks"
  type        = bool
  default     = true
}

# ==============================================================================
# APPLICATION CONFIGURATION
# ==============================================================================

variable "app_port" {
  description = "Port exposed by the docker image to redirect traffic to"
  type        = number
  default     = 8000
}

variable "app_count" {
  description = "Number of docker containers to run"
  type        = number
  default     = 1
}

variable "health_check_path" {
  description = "Health check path for the application"
  type        = string
  default     = "/health"
}

# ==============================================================================
# ECS CONFIGURATION
# ==============================================================================

variable "fargate_cpu" {
  description = "Fargate instance CPU units to provision (1 vCPU = 1024 CPU units)"
  type        = number
  default     = 256
}

variable "fargate_memory" {
  description = "Fargate instance memory to provision (in MiB)"
  type        = number
  default     = 512
}

variable "container_image" {
  description = "Docker image to run in the ECS cluster"
  type        = string
  default     = "nginx:alpine" # Placeholder, will be updated with ECR image
}

# ==============================================================================
# AUTO SCALING CONFIGURATION
# ==============================================================================

variable "autoscaling_min_capacity" {
  description = "Minimum number of tasks to run"
  type        = number
  default     = 1
}

variable "autoscaling_max_capacity" {
  description = "Maximum number of tasks to run"
  type        = number
  default     = 3
}

variable "autoscaling_target_cpu" {
  description = "Target CPU utilization for auto scaling"
  type        = number
  default     = 70
}

variable "autoscaling_target_memory" {
  description = "Target memory utilization for auto scaling"
  type        = number
  default     = 80
}

# ==============================================================================
# MONITORING CONFIGURATION
# ==============================================================================

variable "log_retention_in_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

variable "enable_detailed_monitoring" {
  description = "Enable detailed monitoring for ECS tasks"
  type        = bool
  default     = false
}

# ==============================================================================
# SECURITY CONFIGURATION
# ==============================================================================

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks that can access the ALB"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for ALB"
  type        = bool
  default     = false
}

# ==============================================================================
# COST OPTIMIZATION
# ==============================================================================

variable "enable_cost_optimization" {
  description = "Enable cost optimization features (stop services outside business hours)"
  type        = bool
  default     = false
}

variable "enable_spot_instances" {
  description = "Use Spot instances for cost savings (not recommended for production)"
  type        = bool
  default     = false
}

# ==============================================================================
# FEATURE FLAGS
# ==============================================================================

variable "enable_cloudfront" {
  description = "Enable CloudFront distribution"
  type        = bool
  default     = true
}

variable "enable_auto_scaling" {
  description = "Enable ECS auto scaling"
  type        = bool
  default     = true
}

variable "enable_load_balancer" {
  description = "Enable Application Load Balancer"
  type        = bool
  default     = true
}

variable "create_dynamodb_tables" {
  description = "Create DynamoDB tables"
  type        = bool
  default     = true
}

# ==============================================================================
# DYNAMODB CONFIGURATION
# ==============================================================================

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
  default     = "PAY_PER_REQUEST"

  validation {
    condition     = contains(["PROVISIONED", "PAY_PER_REQUEST"], var.dynamodb_billing_mode)
    error_message = "DynamoDB billing mode must be either PROVISIONED or PAY_PER_REQUEST."
  }
}

variable "enable_dynamodb_point_in_time_recovery" {
  description = "Enable DynamoDB Point-in-time Recovery"
  type        = bool
  default     = true
}

# ==============================================================================
# TAGS
# ==============================================================================

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "Portfolio"
    Environment = "development"
    ManagedBy   = "Terraform"
    Owner       = "Portfolio-Developer"
  }
}

# ==============================================================================
# TERRAFORM STATE CONFIGURATION
# ==============================================================================

variable "terraform_state_bucket" {
  description = "S3 bucket name for storing Terraform state"
  type        = string
  default     = "portfolio-terraform-state-20250823" # Update with your actual bucket name
}

variable "terraform_state_key" {
  description = "S3 key for storing Terraform state"
  type        = string
  default     = "portfolio/terraform.tfstate"
}

variable "terraform_lock_table" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
  default     = "portfolio-terraform-lock"
}