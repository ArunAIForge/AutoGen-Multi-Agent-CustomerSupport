# 🤖 Multi-Agent Customer Support System Using AutoGen & Streamlit

An enterprise-ready, intelligent customer support system powered by the **AutoGen** multi-agent framework and presented through an interactive **Streamlit** frontend.

A central **Main Coordinator Agent** validates incoming queries, classifies intent, and delegates requests to one of five specialized domain agents (**HR**, **IT**, **Insurance**, **Admin**, **Accounts**). The Coordinator then reviews and polishes each agent's response before delivering it to the user.

---

## 📌 Architecture Overview

```text
                                +---------------------------+
                                |  Streamlit User Interface |
                                +-------------+-------------+
                                              | (User Query)
                                              v
                              +-------------------------------+
                              |    Main Coordinator Agent     |
                              | - Input validation & safety   |
                              | - Intent triage & routing     |
                              +---------------+---------------+
                                              |
      +-------------------+-------------------+-------------------+-------------------+-------------------+
      |                   |                   |                   |                   |                   |
      v                   v                   v                   v                   v                   v
+-----------+       +-----------+       +-----------+       +-----------+       +-----------+       +-----------+
| HR Agent  |       | IT Agent  |       | Insurance |       | Admin     |       | Accounts  |       | Ambiguous |
| (Leaves,  |       | (VPN,     |       | Agent     |       | Agent     |       | Agent     |       | Fallback  |
| Policies) |       | Password) |       | (Claims)  |       | (Badges)  |       | (Expense) |       | (Clarify) |
+-----+-----+       +-----+-----+       +-----+-----+       +-----+-----+       +-----+-----+       +-----+-----+
      |                   |                   |                   |                   |                   |
      +-------------------+-------------------+-------------------+-------------------+-------------------+
                                              | (Drafted Response)
                                              v
                              +-------------------------------+
                              |   Response Validator Agent    |
                              | - Quality assurance & polish  |
                              +---------------+---------------+
                                              | (Final Output)
                                              v
                                +---------------------------+
                                |   Streamlit Chat Window   |
                                +---------------------------+

🏢 Department Roles & ResponsibilitiesAgentResponsibilitiesScope & GuardrailsMain CoordinatorRequest validation, intent routing, ambiguity handling, quality assurance.Rejects out-of-scope requests; asks clarification for vague prompts.HR AgentAnnual leave, sick leave, attendance, onboarding, holidays, HR policy.Disallows IT, finance, building access, or medical claim questions.IT AgentPasswords, VPN, SSO credentials, Wi-Fi, software installs, hardware issues.Emphasizes security; never asks for plaintext credentials.Insurance AgentHealth & life insurance, cashless hospitalization, claim documentation.Focuses strictly on coverage, eligibility, and claim procedures.Admin AgentID cards, visitor passes, facilities, desk allocations, office supplies.Handles workplace physical logistics and facilities requests.Accounts AgentExpense claims, invoice submissions, reimbursements, payroll accounting.Guides submission deadlines, tax documentation, and approvals.

autogen-customer-support/
├── agents/
│   ├── __init__.py               # Agent module exports
│   ├── main_agent.py             # Coordinator & Response Validator Agents
│   ├── hr_agent.py               # Human Resources Specialist Agent
│   ├── it_agent.py               # IT & Technical Support Agent
│   ├── insurance_agent.py        # Corporate Insurance Specialist Agent
│   ├── admin_agent.py            # Workplace Administration Agent
│   └── accounts_agent.py         # Finance & Accounts Specialist Agent
├── config/
│   └── settings.py               # Multi-provider LLM client factory & credential resolver
├── services/
│   └── orchestrator.py           # Core triage, routing, and QA orchestration pipeline
├── utils/
│   ├── logger.py                 # Centralized rotating file and console logger
│   └── validation.py             # Input sanitization and spam detection
├── logs/
│   └── agent_activity.log        # Auto-generated execution and audit logs
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore file for secrets and environments
├── requirements.txt              # Project dependencies
├── test_suite.py                 # Automated 7-scenario batch evaluation script
├── verify_connection.py          # Quick provider connectivity verification test
├── app.py                        # Streamlit web application
└── README.md                     # Setup and usage documentation