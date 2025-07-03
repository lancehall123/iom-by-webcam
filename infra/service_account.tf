# resource "google_service_account" "github_actions" {
#   account_id   = "github-actions"
#   display_name = "GitHub Actions Deployer"

#   lifecycle {
#     prevent_destroy = true
#     ignore_changes  = [display_name]
#   }
# }


# resource "google_project_iam_member" "artifact_writer" {
#   role   = "roles/artifactregistry.writer"
#   member = "serviceAccount:${google_service_account.github_actions.email}"
#   project = var.project_id
# }

# resource "google_project_iam_member" "run_deployer" {
#   role   = "roles/run.admin"
#   member = "serviceAccount:${google_service_account.github_actions.email}"
#   project = var.project_id
# }

# resource "google_project_iam_member" "storage_writer" {
#   role   = "roles/storage.objectAdmin"
#   member = "serviceAccount:${google_service_account.github_actions.email}"
#   project = var.project_id
# }

# resource "google_service_account_key" "github_key" {
#   service_account_id = google_service_account.github_actions.name
#   private_key_type   = "TYPE_GOOGLE_CREDENTIALS_FILE"
# }
