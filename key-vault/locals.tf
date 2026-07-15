locals {
  current_user_id = coalesce(var.msi_id, data.azurerm_client_config.user.object_id)
}