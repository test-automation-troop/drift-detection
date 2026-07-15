resource "azurerm_mssql_server" "drift_sql_server" {
  name                         = var.sql_server_name
  resource_group_name          = data.azurerm_resource_group.rg.name
  location                     = "Southeast Asia"

  version                      = "12.0"

  administrator_login          = var.sql_admin_login
  administrator_login_password = var.sql_admin_password

  minimum_tls_version = "1.2"
}

resource "azurerm_mssql_database" "drift_db" {
  name      = var.sql_database_name
  server_id = azurerm_mssql_server.drift_sql_server.id

  sku_name = "Basic"
}

resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name      = "AllowAzureServices"
  server_id = azurerm_mssql_server.drift_sql_server.id

  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_mssql_firewall_rule" "my_ip" {
  name      = "MyLaptop"
  server_id = azurerm_mssql_server.drift_sql_server.id

  start_ip_address = "121.241.202.136"
  end_ip_address   = "121.241.202.136"
}