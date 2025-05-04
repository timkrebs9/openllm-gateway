# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.27.0"
    }
  }
  required_version = ">= 0.14"
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
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
  location = "germanywestcentral"

  tags = {
    environment = "Dev"
  }
}

# ------------------------------------------------------------------------------------------------------
# Deploy Azure DNS Zone
# ------------------------------------------------------------------------------------------------------
resource "azurerm_dns_zone" "openllm-gateway" {
  name                = "azureopengpt.com"
  resource_group_name = azurerm_resource_group.openllm-gateway.name
}

resource "azurerm_key_vault" "gateway" {
  name                            = "${random_pet.prefix.id}-kv"
  location                        = azurerm_resource_group.openllm-gateway.location
  resource_group_name             = azurerm_resource_group.openllm-gateway.name
  tenant_id                       = var.tenant_id
  sku_name                        = "standard"
  purge_protection_enabled        = false
  soft_delete_retention_days      = 7
  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
}

# ------------------------------------------------------------------------------------------------------
# Deploy Azure Key Vault Access Policy
# ------------------------------------------------------------------------------------------------------
resource "azurerm_key_vault_access_policy" "gateway_tls_access" {
  key_vault_id = azurerm_key_vault.gateway.id
  tenant_id    = var.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  certificate_permissions = [
    "Get", "List", "Create", "Delete", "Import", "Update", "ManageContacts", "ManageIssuers", "GetIssuers", "ListIssuers", "SetIssuers", "DeleteIssuers"
  ]

  secret_permissions = [
    "Get", "List", "Set", "Delete"
  ]

  key_permissions = [
    "Get", "Create", "List", "Update", "Delete"
  ]
}

# ------------------------------------------------------------------------------------------------------
# Azure Key Vault + Zertifikat
# ------------------------------------------------------------------------------------------------------
resource "azurerm_key_vault_certificate" "gateway_tls" {
  name         = "tls-cert"
  key_vault_id = azurerm_key_vault.gateway.id

  depends_on = [
    azurerm_key_vault_access_policy.gateway_tls_access
  ]
  certificate_policy {
    issuer_parameters {
      name = "Self"
    }
    key_properties {
      exportable = true
      key_size   = 2048
      key_type   = "RSA"
      reuse_key  = true
    }
    secret_properties {
      content_type = "application/x-pkcs12"
    }
    x509_certificate_properties {
      subject            = "CN=azureopengpt.com"
      validity_in_months = 12

      subject_alternative_names {
        dns_names = ["azureopengpt.com", "www.azureopengpt.com"]
      }

      key_usage = [
        "cRLSign",
        "dataEncipherment",
        "digitalSignature",
        "keyEncipherment",
        "keyAgreement",
        "keyCertSign"
      ]
    }
  }
}

# ------------------------------------------------------------------------------------------------------
# Deploy Azure Front Door
# ------------------------------------------------------------------------------------------------------
resource "azurerm_cdn_frontdoor_profile" "gateway" {
  name                = "${random_pet.prefix.id}-afd"
  resource_group_name = azurerm_resource_group.openllm-gateway.name
  sku_name            = "Premium_AzureFrontDoor"
}

# ------------------------------------------------------------------------------------------------------
# Deploy Azure Front Door Endpoint
# ------------------------------------------------------------------------------------------------------
resource "azurerm_cdn_frontdoor_endpoint" "gateway" {
  name                     = "frontend"
  cdn_frontdoor_profile_id = azurerm_cdn_frontdoor_profile.gateway.id
  enabled                  = true
}

# ------------------------------------------------------------------------------------------------------
# Deploy Azure Front Door Custom Domain
# ------------------------------------------------------------------------------------------------------
resource "azurerm_dns_cname_record" "auth" {
  name                = "auth"
  zone_name           = azurerm_dns_zone.openllm-gateway.name
  resource_group_name = azurerm_resource_group.openllm-gateway.name
  ttl                 = 300
  record              = azurerm_cdn_frontdoor_endpoint.gateway.host_name
}

resource "azurerm_dns_cname_record" "chat" {
  name                = "chat"
  zone_name           = azurerm_dns_zone.openllm-gateway.name
  resource_group_name = azurerm_resource_group.openllm-gateway.name
  ttl                 = 300
  record              = azurerm_cdn_frontdoor_endpoint.gateway.host_name
}

# ------------------------------------------------------------------------------------------------------
# Generate a resource token
# ------------------------------------------------------------------------------------------------------
locals {
  sha            = base64encode(sha256("${azurerm_resource_group.openllm-gateway.tags["environment"]}${azurerm_resource_group.openllm-gateway.location}${data.azurerm_client_config.current.subscription_id}"))
  resource_token = substr(replace(lower(local.sha), "[^A-Za-z0-9_]", ""), 0, 13)
}

# ------------------------------------------------------------------------------------------------------
# Deploy postgresql flexible server
# ------------------------------------------------------------------------------------------------------
#resource "azurerm_postgresql_flexible_server" "openllm-gateway" {
#  administrator_login    = "pgadminuser"
#  administrator_password = var.postgresql_server_password
#  auto_grow_enabled      = false
#  backup_retention_days  = 7
#  #delegated_subnet_id           = "your-delegated-subnet-id" // Replace with a valid subnet ID
#  geo_redundant_backup_enabled = false
#  location                     = "germanywestcentral"#azurerm_resource_group.openllm-gateway.location
#  name                         = "${random_pet.prefix.id}-pg"
#  resource_group_name          = azurerm_resource_group.openllm-gateway.name
#  sku_name                     = "B_Standard_B2s"
#  storage_mb                   = 131072
#  storage_tier                 = "P10"
#  tags                         = {}
#  version                      = "16"
#  authentication {
#    active_directory_auth_enabled = false
#    password_auth_enabled         = true
#    tenant_id                     = var.tenant_id // Replace with a valid UUID
#  }
#}

# ------------------------------------------------------------------------------------------------------
# Deploy Azure Container Registry
# ------------------------------------------------------------------------------------------------------
resource "azurerm_container_registry" "openllm-gateway" {
  name                = "${replace(random_pet.prefix.id, "-", "")}acr"
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
  name                = "${random_pet.prefix.id}-aks"
  location            = "westcentralus" #azurerm_resource_group.openllm-gateway.location
  resource_group_name = azurerm_resource_group.openllm-gateway.name
  dns_prefix          = "${random_pet.prefix.id}-k8s"
  kubernetes_version  = "1.32.0"

  default_node_pool {
    name            = "default"
    node_count      = 2
    vm_size         = "Standard_D2as_v6"
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
  location       = azurerm_resource_group.openllm-gateway.location
  rg_name        = azurerm_resource_group.openllm-gateway.name
  tags           = azurerm_resource_group.openllm-gateway.tags
  resource_token = local.resource_token
}