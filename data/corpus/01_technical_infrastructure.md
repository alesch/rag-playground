# Technical Infrastructure Documentation

## System Architecture Overview

**finanso** is Acme's flagship SaaS accounting closing software designed for financial institutions. The system is built on a robust, scalable architecture to ensure high availability and security.

### Technology Stack

- **Platform**: Java 9
- **Application Server**: Wildfly 17
- **Cloud Provider**: Microsoft Azure
- **Database**: MS-SQL
- **Architecture**: Multi-tenant SaaS with tenant isolation

### Cloud Infrastructure

finanso is hosted entirely on Microsoft Azure, leveraging the following services:

- **Compute**: Azure App Service for application hosting
- **Database**: Azure Database for MS-SQL with automated backups
- **Storage**: Azure Blob Storage for document management
- **Networking**: Azure Virtual Network with Network Security Groups
- **Load Balancing**: Azure Application Gateway with WAF

## Security Controls

### Authentication

finanso implements multiple layers of authentication:

- **Multi-Factor Authentication (MFA)**: Required for all user accounts
- **Single Sign-On (SSO)**: Supports SAML 2.0 integration with enterprise identity providers
- **Password Policy**: Minimum 12 characters with complexity requirements
- **Session Management**: 30-minute idle timeout, secure cookie handling

### Encryption

All data is encrypted both in transit and at rest:

- **In Transit**: TLS 1.3 for all network communications
- **At Rest**: AES-256 encryption for database and file storage
- **Key Management**: Azure Key Vault for encryption key management with automatic rotation

### Access Controls

- **Role-Based Access Control (RBAC)**: Granular permissions based on job function
- **Principle of Least Privilege**: Users granted minimum necessary access
- **Access Reviews**: Quarterly review of user permissions
- **API Authentication**: OAuth 2.0 with JWT tokens

## Data Storage & Processing

### Database Architecture

- **Primary Database**: Azure Database for MS-SQL 2019
- **Backup Strategy**: Automated daily backups with 30-day retention
- **Point-in-Time Recovery**: Available for last 30 days
- **Data Residency**: Customer data stored in customer-selected Azure region

### Data Isolation

Multi-tenant architecture with strict tenant isolation:

- **Database-level**: Separate databases per tenant
- **Application-level**: Tenant context validation on all queries
- **Network-level**: Virtual network isolation between environments

## Disaster Recovery & Business Continuity

### Recovery Objectives

- **Recovery Time Objective (RTO)**: 4 hours
- **Recovery Point Objective (RPO)**: 1 hour

### Backup Procedures

- **Database Backups**: Automated daily full backups, hourly transaction logs
- **Application Backups**: Immutable infrastructure, version-controlled configuration
- **Testing**: Quarterly disaster recovery drills

### High Availability

- **Database**: Azure Database for MS-SQL 2019 with automatic failover
- **Application**: Multi-instance deployment across availability zones
- **Monitoring**: 24/7 automated monitoring with alerting
- **Uptime SLA**: 99.9% availability guarantee

## Infrastructure Monitoring

- **Application Performance**: Azure Application Insights
- **Infrastructure Metrics**: Azure Monitor
- **Log Aggregation**: Centralized logging with 90-day retention
- **Security Monitoring**: Azure Security Center continuous monitoring
