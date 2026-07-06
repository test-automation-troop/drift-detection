output "resource_group_name" {
  value = data.azurerm_resource_group.rg.name
}

output "virtual_network" {
  value = azurerm_virtual_network.vnet.name
}

output "subnet" {
  value = azurerm_subnet.subnet.name
}

output "public_ip_address" {
  value = azurerm_windows_virtual_machine.main.public_ip_address
}