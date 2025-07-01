resource "google_cloud_run_v2_service" "service" {
  name     = "image-processor"
  location = var.region

  template {
    containers {
      image = var.image_url
      env {
        name  = "BUCKET_NAME"
        value = var.bucket_name
      }
    }
  }
}

output "url" {
  value = google_cloud_run_v2_service.service.uri
}