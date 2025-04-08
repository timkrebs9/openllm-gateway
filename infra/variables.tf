# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

variable "appId" {
  description = "Azure Kubernetes Service Cluster service principal"
}

variable "password" {
  description = "Azure Kubernetes Service Cluster password"
}

variable "subscription_id" {
  description = "Azure subscription ID"
} 

variable "tenant_id" {
  description = "Azure tenant ID"  
}

variable "client_id" {
  description = "Azure client ID"  
}
