# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">=3.93.0"
    }
  }
  required_version = ">= 0.14"
}

provider "azurerm" {
  features {}
  #skip_provider_registration = true

  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.appId
  client_secret   = var.password
}

# Declare the missing data source
data "azurerm_client_config" "current" {}

# ------------------------------------------------------------------------------------------------------
# Generate a random prefix for resource names
# ------------------------------------------------------------------------------------------------------
resource "random_pet" "prefix" {}

# ------------------------------------------------------------------------------------------------------
# Deploy Resource Group
# ------------------------------------------------------------------------------------------------------
resource "azurerm_resource_group" "openllm-gateway" {
  name     = "${random_pet.prefix.id}-rg"
  location = "West US 2"

  tags = {
    environment = "Dev"
  }
}

# ------------------------------------------------------------------------------------------------------
# Generate a resource token
# ------------------------------------------------------------------------------------------------------
locals {
  sha                          = base64encode(sha256("${azurerm_resource_group.openllm-gateway.tags["environment"]}${azurerm_resource_group.openllm-gateway.location}${data.azurerm_client_config.current.subscription_id}"))
  resource_token               = substr(replace(lower(local.sha), "[^A-Za-z0-9_]", ""), 0, 13)
}

# ------------------------------------------------------------------------------------------------------
# Deploy postgresql flexible server
# ------------------------------------------------------------------------------------------------------
resource "azurerm_postgresql_flexible_server" "openllm-gateway" {
  administrator_login           = var.postgresql_server_admin
  administrator_password        = var.postgresql_server_password
  auto_grow_enabled             = false
  backup_retention_days         = 7
  #delegated_subnet_id           = "your-delegated-subnet-id" // Replace with a valid subnet ID
  geo_redundant_backup_enabled  = false
  location                      = azurerm_resource_group.openllm-gateway.location
  name                          = "${random_pet.prefix.id}-${var.postgresql_server_name}"
  #private_dns_zone_id           = "your-private-dns-zone-id" // Replace with a valid DNS zone ID
  replication_role              = "None" // Set to a valid value
  resource_group_name           = azurerm_resource_group.openllm-gateway.name
  sku_name                      = "B_Standard_B2s"
  storage_mb                    = 131072
  storage_tier                  = "P10"
  tags                          = {}
  version                       = "16"
  zone                          = "1"
  authentication {
    active_directory_auth_enabled = false
    password_auth_enabled         = true
    tenant_id                     = var.tenant_id // Replace with a valid UUID
  }
}

# ------------------------------------------------------------------------------------------------------
# Deploy Azure Container Registry
# ------------------------------------------------------------------------------------------------------
resource "azurerm_container_registry" "openllm-gateway" {
  name                = "${random_pet.prefix.id}acr" // Remove the hyphen to make it alphanumeric
  resource_group_name = azurerm_resource_group.openllm-gateway.name
  location            = azurerm_resource_group.openllm-gateway.location
  sku                 = "Basic"
  admin_enabled       = false
  tags = {
    environment = "Dev"
  }
}

# ------------------------------------------------------------------------------------------------------
# Deploy AKS cluster
# ------------------------------------------------------------------------------------------------------
resource "azurerm_kubernetes_cluster" "openllm-gateway" {
  name                = "${random_pet.prefix.id}aks" // Remove the hyphen to make it alphanumeric
  location            = "eastus" // Change to a supported location
  resource_group_name = azurerm_resource_group.openllm-gateway.name
  dns_prefix          = "${random_pet.prefix.id}-k8s"
  kubernetes_version  = "1.27.3" // Use a supported Kubernetes version

  default_node_pool {
    name            = "openllm" // Ensure it meets the naming requirements
    node_count      = 3
    vm_size         = "Standard_D2_v2"
    os_disk_size_gb = 30
  }

  service_principal {
    client_id     = var.appId
    client_secret = var.password
  }

  role_based_access_control_enabled = true

  tags = {
    environment = "Dev"
  }
}

# ------------------------------------------------------------------------------------------------------
# Deploy application insights
# ------------------------------------------------------------------------------------------------------
module "applicationinsights" {
  source           = "./modules/applicationinsights"
  location         = azurerm_resource_group.openllm-gateway.location
  rg_name          = azurerm_resource_group.openllm-gateway.name
  environment_name = "${random_pet.prefix.id}-ai"
  workspace_id     = module.loganalytics.LOGANALYTICS_WORKSPACE_ID
  tags             = azurerm_resource_group.openllm-gateway.tags
  resource_token   = local.resource_token
}

# ------------------------------------------------------------------------------------------------------
# Deploy log analytics
# ------------------------------------------------------------------------------------------------------
module "loganalytics" {
  source         = "./modules/loganalytics"
  location         = azurerm_resource_group.openllm-gateway.location
  rg_name          = azurerm_resource_group.openllm-gateway.name
  tags             = azurerm_resource_group.openllm-gateway.tags
  resource_token = local.resource_token
}