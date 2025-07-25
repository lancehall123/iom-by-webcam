variable "project_id" {
  type    = string
  default = "isleofmanbywebcam"
}

variable "region" {
  type    = string
  default = "europe-west1"
}

variable "bucket_name" {
  type    = string
  default = "iombywebcambucket"
}

variable "youtube_oauth_json" {
  type = string
  description = "Contents of YouTube OAuth JSON credentials"
  default = "dummy"
}

variable "image_url" {
  type        = string
  description = "The URL of the webcam image to fetch"
  default = "europe-west1-docker.pkg.dev/isleofmanbywebcam/webcam-repo/image_processor"
}
