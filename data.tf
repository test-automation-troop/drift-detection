data "azurerm_resource_group" "rg" {
  name = "drift-test"
}

data "azurerm_storage_account" "sa" {
    name = "testsaaccount5603"
    resource_group_name = "drift-test"
}