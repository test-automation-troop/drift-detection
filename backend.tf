terraform {
    backend "azurerm" {
        resource_group_name = "drift-test"
        storage_account_name = "testsaaccount5603"
        container_name = "tfstate"
        key = "vm/terraform.tfstate"
    }
}