terraform {
  required_version = ">= 1.3.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.84"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "gcs" {
  source      = "./modules/storage"
  bucket_name = var.bucket_name
}

module "secret" {
  source       = "./modules/secret"
  secret_id    = "youtube_oauth"
  secret_value = var.youtube_oauth_json
}

module "cloud_run" {
  source      = "./modules/cloud_run"
  bucket_name = var.bucket_name
  image_url   = var.image_url
  region      = var.region
}

module "scheduler" {
  source        = "./modules/scheduler"
  job_name      = "fetch-and-process-images"
  schedule      = "* * * * *" # every minute
  cloud_run_uri = module.cloud_run.url
}
