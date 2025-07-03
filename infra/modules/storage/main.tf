resource "google_storage_bucket" "media" {
  name     = var.bucket_name
  location = var.region

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [name]
  }
}

