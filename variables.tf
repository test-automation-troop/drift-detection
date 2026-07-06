variable "resource_group_location" {
  default     = "West Europe"
  description = "Location of the resource group."
}

variable "prefix" {
  type        = string
  default     = "win-vm"
  description = "Prefix of the resource name"
}