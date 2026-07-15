resource "azurerm_storage_account" "sa" {
  name                     = "testsaaccount5603"
  resource_group_name      = data.azurerm_resource_group.rg.name
  location                 = "Central India"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }
}