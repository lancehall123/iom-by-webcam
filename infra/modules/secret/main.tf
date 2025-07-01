resource "google_secret_manager_secret" "oauth" {
  secret_id = var.secret_id

  replication {
    user_managed {
      replicas {
        location = "europe-west1"
      }
    }
  }
}


resource "google_secret_manager_secret_version" "oauth_version" {
  secret      = google_secret_manager_secret.oauth.id
  secret_data = var.secret_value
}
