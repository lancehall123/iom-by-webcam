resource "google_storage_bucket" "media" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true
}
