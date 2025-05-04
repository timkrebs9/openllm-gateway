# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

output "resource_group_name" {
  value = azurerm_resource_group.openllm-gateway.name // Correct reference
}

output "kubernetes_cluster_name" {
  value = azurerm_kubernetes_cluster.openllm-gateway.name // Correct reference
}

