data "azurerm_resource_group" "rg" {
  name = "test-resources"
}

data "azurerm_storage_account" "sa" {
    name = "testsaaccount5603"
    resource_group_name = "test-resources"
}