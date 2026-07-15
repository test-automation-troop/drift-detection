output "resource_group_name" {
  value = data.azurerm_resource_group.rg.name
}

output "azurerm_key_vault_name" {
  value = azurerm_key_vault.vault.name
}

output "azurerm_key_name" {
  value = azurerm_key_vault_key.key.name
}