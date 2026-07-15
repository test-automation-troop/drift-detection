variable "sql_server_name" {
  default = "drift-detect-sql-server07"
}

variable "sql_database_name" {
  default = "DriftDetectionDB"
}

variable "sql_admin_login" {}

variable "sql_admin_password" {
  sensitive = true
}