resource "google_cloud_scheduler_job" "job" {
  name        = var.job_name
  description = "Triggers the image processor Cloud Run service every minute"
  schedule    = var.schedule
  time_zone   = "Etc/UTC"

  http_target {
    uri = var.cloud_run_uri
    http_method = "POST"

    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      message = "Trigger from Cloud Scheduler"
    }))
  }
}
