# Production environment composition (EU, multi-AZ). Skeleton — modules filled in during hardening.

terraform {
  required_version = ">= 1.7"
  # backend "s3" { ... }   # remote, encrypted, locked state (configured per org)
}

locals {
  region   = "eu-central-1" # EU only (Frankfurt). Milan (eu-south-1) also permitted.
  env      = "prod"
  tags     = { app = "condominioos", env = "prod", data_residency = "eu" }
}

module "network" {
  source = "../../modules/network"
  region = local.region
  tags   = local.tags
}

module "database" {
  source        = "../../modules/database"
  region        = local.region
  multi_az      = true
  audit_separate = true # separate append-only audit DB (docs/05 §4)
  tags          = local.tags
}

module "object_store" {
  source             = "../../modules/object_store"
  region             = local.region
  per_tenant_prefix  = true
  crypto_shred_keys  = true # enables GDPR erasure (docs/05 §7)
  tags               = local.tags
}

module "kubernetes" {
  source   = "../../modules/kubernetes"
  region   = local.region
  multi_az = true
  tags     = local.tags
}

# vector, messaging, secrets, observability modules composed similarly.
