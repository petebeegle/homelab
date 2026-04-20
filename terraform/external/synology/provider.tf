terraform {
  required_providers {
    synology = {
      source  = "synology-community/synology"
      version = "0.6.11"
    }
    external = {
      source  = "hashicorp/external"
      version = "2.3.5"
    }
  }
}

provider "synology" {
  host       = "https://192.168.30.99:5001"
  user       = "petebeegle"
  password   = "4o3TkK4vA6gVeCQo8QPJ"
  otp_secret = "2NDUKO44ISCVQK6S"

}
