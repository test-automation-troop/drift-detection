data "azurerm_resource_group" "rg" {
    name = "drift-test"
}

data "azurerm_client_config" "user" {}