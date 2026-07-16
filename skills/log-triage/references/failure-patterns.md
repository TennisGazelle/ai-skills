# Failure pattern reference for log-triage

Load this file when the pasted log involves AWS, CI, Docker, or database errors.

## IAM / instance profile

- **Symptom:** `InvalidInstanceProfile.NotFound`, `is not authorized to perform: ec2:...`
- **Check:** instance profile name on launch template vs IAM role that exists; `aws iam get-instance-profile`
- **Common fix:** align LT `IamInstanceProfile` with IaC-defined role name; redeploy stack

## S3 cross-account

- **Symptom:** `AccessDenied` on `ListBucket` or `GetObject` for a bucket in another account
- **Check:** bucket policy trusts the caller's role ARNs; identity policy uses `s3:ResourceAccount` condition
- **Common fix:** bucket policy statement missing role ARN (copy standard template from IaC docs)

## Lambda → RDS / VPC

- **Symptom:** timeout connecting to RDS, `connection timed out`
- **Check:** Lambda in correct VPC/subnets; SG allows egress to RDS SG on 5432
- **Common fix:** security group rule in the network/IaC stack

## GitHub Actions CI

- **Symptom:** Playwright `Executable doesn't exist`, `npm ci` failure
- **Check:** workflow installs browsers (`npx playwright install --with-deps`); Node version matches project
- **Common fix:** add install step or pin action versions

## Docker Compose (local dev)

- **Symptom:** backend can't reach DB, wrong AWS profile inside container
- **Check:** `docker compose config`; env file mounted; service `depends_on` health
- **Common fix:** use compose profile/env from repo docs; prefer `make web-dev` if documented

## Flyway / DB migration

- **Symptom:** migration checksum mismatch, relation already exists
- **Check:** applied migrations table vs local migration files; submodule version
- **Common fix:** never edit applied migrations; add new migration forward
