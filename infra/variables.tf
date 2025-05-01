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

variable "postgresql_server_name" {
  description = "Name of the PostgreSQL server"
  default     = "db"
}

variable "postgresql_server_admin" {
  description = "PostgreSQL server admin username"
  default     = "admin"
}

variable "useAPIM" {
  description = "Flag to use Azure API Management to mediate the calls between the Web frontend and the backend API."
  type        = bool
  default     = false
}

variable "apimSKU" {
  description = "Azure API Management SKU. Only used if useAPIM is true."
  type       = string
  default = "Consumption"
}