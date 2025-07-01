variable "job_name" {
  type = string
}

variable "schedule" {
  type    = string
  default = "* * * * *" # every minute
}

variable "cloud_run_uri" {
  type = string
}
