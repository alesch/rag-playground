This markdown document provides the complete responses to the 50 questions found in the **sample\_questionnaire.md** file, utilizing information from the technical infrastructure, SOC 2, ISO 27001, and operational documentation.

# finanso: Vendor Information Security Assessment

**Vendor Name:** Acme Inc.  
**Product/Service:** finanso \- SaaS Accounting Closing Software  
**Assessment Date:** December 2024

### Section 1: Security & Compliance Certifications

**Q1.1: What security certifications does your organization hold?**  
Acme maintains **SOC 2 Type II** and **ISO/IEC 27001:2013** certifications for the finanso platform 1, 2\.

**Q1.2: Are you SOC 2 compliant? If yes, which Trust Services Criteria are covered and when was your last audit?**  
Yes, Acme is SOC 2 Type II compliant, covering the Trust Services Criteria of **Security, Availability, and Confidentiality** 1\. The last audit was conducted by Deloitte & Touche LLP for the period of January 2023 through December 2023, with the report issued on **January 15, 2024** 1\.

**Q1.3: Do you maintain ISO 27001 certification? Please provide certification details.**  
Yes, the finanso platform and supporting infrastructure are certified to **ISO/IEC 27001:2013** 2\. The certification was issued by **BSI Group** on March 1, 2024, and is valid until February 28, 2027, provided annual surveillance audits are completed 2\.

**Q1.4: What compliance frameworks do you adhere to (GDPR, CCPA, etc.)?**Acme adheres to **GDPR** for European Union customers and **CCPA** for customers in California 3\. The organization conducts regular legal and regulatory reviews to maintain compliance with these frameworks 3\.

### Section 2: Technical Infrastructure

**Q2.1: What technology stack is your platform built on?**  
The platform is built on **Java 9** using the **Wildfly 17** application server 4\. It utilizes **MS-SQL** for the database layer and is hosted on **Microsoft Azure** 4\.

**Q2.2: Which cloud provider do you use and in what regions is customer data stored?**  
The cloud provider is **Microsoft Azure** 4, 5\. Customer data is stored in the specific **Azure region selected by the customer** to ensure data residency requirements are met 6\.

**Q2.3: Describe your system architecture (single-tenant vs multi-tenant).**  
finanso utilizes a **multi-tenant SaaS architecture** designed with strict tenant isolation 4, 6\. Isolation is maintained at the **database level** (separate databases per tenant), the **application level** (tenant context validation), and the **network level** (segmentation between environments) 6\.

**Q2.4: What database technology do you use and how is it managed?**  
We use **Azure Database for MS-SQL 2019** 6\. It is managed through **automated daily full backups** and **hourly transaction log backups**, supporting Point-in-Time Recovery for up to 30 days 6, 7\.

### Section 3: Authentication & Access Control

**Q3.1: What authentication methods does your platform support?**  
The platform supports standard user account authentication, **SAML 2.0** for Single Sign-On, and **OAuth 2.0 with JWT tokens** for API authentication 5, 8\.

**Q3.2: Do you require multi-factor authentication (MFA)? Is it mandatory for all users?**  
Yes, **MFA is required for all user accounts** without exception 5, 9\.

**Q3.3: Do you support Single Sign-On (SSO) integration?**  
Yes, the platform supports **SAML 2.0 integration** with enterprise identity providers 5\.

**Q3.4: Describe your password policy and requirements.**  
The password policy requires a **minimum of 12 characters** and includes specific complexity requirements 5, 9\.

**Q3.5: How do you manage privileged access to customer data?**  
Privileged access is managed through **Role-Based Access Control (RBAC)** and the principle of **least privilege** 8, 10\. Administrative access requires **separate credentials**, and these accounts are reviewed on a **quarterly basis** 9, 10\.

### Section 4: Data Encryption

**Q4.1: How is data encrypted in transit?**  
All network communications are encrypted using **TLS 1.3** 8, 11\.

**Q4.2: How is data encrypted at rest?**  
Data at rest in the database and file storage is encrypted using **AES-256** 8, 11\.

**Q4.3: What encryption algorithms and key lengths do you use?**  
We utilize **AES-256** for storage encryption and **TLS 1.3** for transit encryption 8, 11\.

**Q4.4: How are encryption keys managed and rotated?**  
Keys are managed in **Azure Key Vault**, which provides centralized management and **automated key rotation** 8, 11\.

### Section 5: Data Protection & Privacy

**Q5.1: Where is customer data physically stored (geographic regions)?**  
Customer data is physically stored in **Microsoft Azure data centers** located in the region chosen by the customer during initial setup 6, 12\.

**Q5.2: How do you ensure data isolation between customers in a multi-tenant environment?**  
Isolation is enforced via **separate databases per tenant**, mandatory **tenant context validation** on all application queries, and **network segmentation** between production and other environments 6, 13\.

**Q5.3: What is your data retention policy?**  
Database backups are retained for **30 days** 6, 14\. Operational logs are kept for **90 days**, while security-related logs are retained for **one year** 15\.

**Q5.4: How do you handle data deletion requests?**  
Acme follows **secure data destruction procedures** to ensure that confidential data is permanently removed when requested or no longer needed 10, 16\.

**Q5.5: Do you process or store any personal information? How is it protected?**  
Yes, the platform processes customer data, which may include personal information 6, 17\. This data is protected by **AES-256 encryption**, strict **RBAC**, and compliance with **GDPR/CCPA** standards 3, 8\.

### Section 6: Backup & Disaster Recovery

**Q6.1: What is your backup strategy and frequency?**  
We perform **automated daily full backups** and **hourly incremental backups** of transaction logs 7, 14\.

**Q6.2: What are your Recovery Time Objective (RTO) and Recovery Point Objective (RPO)?**  
Our target **RTO is 4 hours** and our **RPO is 1 hour** 3, 7\.

**Q6.3: How often do you test your disaster recovery procedures?**  
We conduct **annual full disaster recovery tests** and **quarterly DR drills** 3, 7, 14\. Additionally, backup restoration is tested **monthly** 14, 15\.

**Q6.4: Describe your business continuity plan.**  
Acme maintains a comprehensive **Business Continuity Plan (BCP)** that is updated annually and includes **multi-region Azure deployment** and **automated failover** capabilities 3, 14\.

**Q6.5: What is your uptime SLA?**  
We provide a **99.9% availability guarantee** 7, 18\.

### Section 7: Security Monitoring & Incident Response

**Q7.1: How do you monitor your systems for security threats?**  
Monitoring is performed using **Azure Security Center** for continuous threat detection, **Azure Monitor** for metrics, and a centralized **SIEM** for log analysis 19, 20\.

**Q7.2: Do you have a 24/7 security operations center?**  
We have a dedicated **Incident Response Team** that operates on a **24/7 on-call rotation** with a **15-minute response time** for critical (P0) incidents 21, 22\.

**Q7.3: Describe your incident response process.**  
The process follows seven phases: **Detection, Triage, Containment, Investigation, Remediation, Recovery, and Post-Incident Review** 23, 24\. Critical incidents trigger the activation of a specialized response team including security engineers and legal counsel 21, 23\.

**Q7.4: What is your timeline for notifying customers of security incidents?**  
Affected customers are notified of data breaches within **72 hours of discovery** 25-27.

**Q7.5: How do you handle and log access to customer data?**  
All access to customer data is logged, including **authentication events, data modifications, and administrative actions** 14\. These logs are reviewed **daily** by the operations team 15, 20\.

### Section 8: Vulnerability Management

**Q8.1: How often do you perform vulnerability assessments?**  
We conduct **weekly automated vulnerability scans** and **annual comprehensive risk assessments** 20, 28, 29\.

**Q8.2: Do you conduct penetration testing? How frequently?**  
Yes, we engage third parties to perform **penetration tests annually** 20, 30\.

**Q8.3: What is your patch management process?**  
We use an **automated security patch management system** where changes are tested in a staging environment and approved via a formal **change management process** before production deployment 20, 25, 31\.

**Q8.4: How quickly are critical security patches applied?**  
Critical security patches are applied within **30 days** 20, 32\.

### Section 9: Vendor & Third-Party Management

**Q9.1: Do you use any sub-processors or third-party vendors that have access to customer data?**  
Yes, **Microsoft Azure** is our primary infrastructure provider 33\. We maintain a list of sub-processors and notify customers of any additions 33\.

**Q9.2: How do you assess and manage third-party vendor risk?**  
We perform **vendor risk assessments** that include reviewing **SOC 2/ISO certifications** and requiring vendors to complete security questionnaires 28, 34\. Security requirements and data processing agreements are mandated in all contracts 34, 35\.

**Q9.3: Are your cloud provider's compliance certifications inherited?**  
Yes, Acme **inherits physical and environmental security controls** from the Microsoft Azure platform 28, 33\.

### Section 10: Personnel Security

**Q10.1: Do you conduct background checks on employees with access to customer data?**  
Yes, **background checks** are required for all employees before they are granted system access 36, 37\.

**Q10.2: What security training do employees receive?**  
Employees receive **onboarding security training** in their first week and **mandatory annual awareness training** 16, 36, 38\. Developers receive specialized training in **secure coding (OWASP Top 10\)** 39\.

**Q10.3: How do you manage employee access when they join, change roles, or leave?**We use formal onboarding/offboarding procedures where access is revoked within **24 hours of termination** 10, 16\. Access rights are also reviewed by managers **quarterly** 10, 40\.

### Section 11: Application Security

**Q11.1: Do you follow secure software development practices?**  
Yes, security requirements are defined in our **SDLC**, and we follow **secure coding standards** 13\.

**Q11.2: How do you handle security in your development lifecycle?**  
We maintain **separate environments** for development, staging, and production 41\. We perform **automated security scanning** in our CI/CD pipeline and strictly prohibit the use of production data in test environments 37, 41\.

**Q11.3: Do you perform code reviews and security testing?**  
Yes, a **code review process** is mandatory for all changes, and security testing is performed in staging prior to any production deployment 13, 41\.

**Q11.4: How do you manage and protect API access?**  
API access is managed via **OAuth 2.0 with JWT tokens**, and service accounts are included in **quarterly access reviews** 8, 40\.

### Section 12: Audit & Compliance

**Q12.1: How often are your security controls audited?**  
Controls are audited **annually** by external auditors for SOC 2 and ISO 27001, and **quarterly** through internal audits 30, 42\.

**Q12.2: Can you provide a copy of your most recent SOC 2 report?**  
Yes, the SOC 2 report is available to customers **under a Non-Disclosure Agreement (NDA)** 42\.

**Q12.3: Do you perform regular internal security audits?**  
Yes, we conduct **quarterly internal ISMS audits** and internal control testing 30, 42, 43\.

**Q12.4: How do you track and remediate audit findings?**  
Audit findings are documented as **corrective actions**, tracked to completion, and reviewed by management during **quarterly review meetings** 3, 30, 44\.

**End of Questionnaire**  
**Analogy for Understanding:**Acme's security posture is like a **secure apartment complex**. **Microsoft Azure** provides the reinforced building and 24/7 lobby security (Inherited Controls). **finanso** acts as the individual apartments, where each tenant has their own deadbolt and unique key (Data Isolation). Finally, the **SOC 2 and ISO audits** are like annual safety inspections by the city to ensure the fire alarms, locks, and security cameras are all functioning exactly as promised.  
