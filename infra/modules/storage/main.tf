resource "google_storage_bucket" "media" {
  name     = var.bucket_name
  location = var.region

  force_destroy = false

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [
      labels,
      uniform_bucket_level_access,
    ]
  }
}
