resource "azurerm_role_assignment" "kv_access" {
  scope = azurerm_key_vault.vault.id
  role_definition_name = "Key Vault Administrator"
  principal_id = data.azurerm_client_config.user.object_id
}

resource "random_string" "azurerm_key_vault_name" {
  length  = 13
  lower   = true
  upper   = false
  numeric = false
  special = false
}

resource "azurerm_key_vault" "vault" {
  name                       = coalesce(var.vault_name, "vault-${random_string.azurerm_key_vault_name.result}")
  location                   = data.azurerm_resource_group.rg.location
  resource_group_name        = data.azurerm_resource_group.rg.name
  tenant_id                  = data.azurerm_client_config.user.tenant_id
  sku_name                   = var.sku_name
  soft_delete_retention_days = 7
  enable_rbac_authorization = true
}

resource "random_string" "azurerm_key_vault_key_name" {
  length  = 13
  lower   = true
  numeric = false
  special = false
  upper   = false
}

resource "azurerm_key_vault_key" "key" {
  name = coalesce(var.key_name, "key-${random_string.azurerm_key_vault_key_name.result}")

  key_vault_id = azurerm_key_vault.vault.id
  key_type     = var.key_type
  key_size     = var.key_size
  key_opts     = var.key_ops

  rotation_policy {
    automatic {
      time_before_expiry = "P30D"
    }
    expire_after         = "P90D"
    notify_before_expiry = "P29D"
  }
}