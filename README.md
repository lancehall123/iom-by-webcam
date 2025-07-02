# iom-by-webcam

This project powers the [Isle of Man by Webcam](https://www.youtube.com/@IsleOfManByWebcam/videos) YouTube channel. It automates image capture from a public webcam, processes the images into timestamped collections, and can optionally upload or assemble them into videos.

It is the result of migrating from a previously physical, on-premises setup to a modern, cloud-based, fully automated infrastructure.

---

## Tech Stack

| Component            | Description                                                       |
|----------------------|-------------------------------------------------------------------|
| **Python**           | Image processing and download automation (`fetch_and_process.py`) |
| **Docker**           | Containerized the processor to run anywhere                       |
| **Terraform**        | Infrastructure as Code (GCP provisioning)                         |
| **Cloud Run**        | Serverless hosting of the image processor                         |
| **Cloud Scheduler**  | Triggers the image processor on a fixed schedule                  |
| **Cloud Storage**    | Stores downloaded webcam images securely                          |
| **GitHub Actions**   | CI/CD pipeline for Docker image and infrastructure deployment     |

---
Diagram created by mermaid (Diagrams via code).
```mermaid
flowchart TD
    scheduler["Cloud Scheduler (runs every minute)"]
    run["Cloud Run Job (fetch_and_process.py in Docker)"]
    storage["Google Cloud Storage (images stored in date folders)"]

    scheduler --> run --> storage
```
Work still to be done

Schedule the video creation and upload to youtube