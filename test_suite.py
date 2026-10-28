import asyncio
from services.orchestrator import process_support_query

TEST_CASES = [
    {
        "category": "HR Department",
        "query": "How many annual leave days am I eligible for, and what is the policy for sick leave?",
        "expected_dept": "HR"
    },
    {
        "category": "IT Support Department",
        "query": "My VPN keeps dropping connection and I need to reset my corporate SSO password.",
        "expected_dept": "IT"
    },
    {
        "category": "Insurance Department",
        "query": "What documents are required to file a cashless hospitalization claim for my dependent?",
        "expected_dept": "INSURANCE"
    },
    {
        "category": "Admin Department",
        "query": "I lost my employee access card. How can I get a replacement ID card and temporary visitor badge?",
        "expected_dept": "ADMIN"
    },
    {
        "category": "Accounts Department",
        "query": "What is the monthly deadline to submit client travel meal expense claims and how are they paid?",
        "expected_dept": "ACCOUNTS"
    },
    {
        "category": "Ambiguous Query",
        "query": "Can someone please update me on my status?",
        "expected_dept": "AMBIGUOUS / NONE"
    },
    {
        "category": "Out-of-Scope Query",
        "query": "Can you give me a recipe for chocolate chip cookies and write a poem about autumn?",
        "expected_dept": "OUT_OF_SCOPE / NONE"
    }
]

async def run_test_suite():
    print("=" * 80)
    print("RUNNING MULTI-AGENT CUSTOMER SUPPORT EVALUATION SUITE")
    print("=" * 80)
    
    passed = 0
    total = len(TEST_CASES)
    
    for idx, test in enumerate(TEST_CASES, start=1):
        print(f"\n[Test {idx}/{total}] Category: {test['category']}")
        print(f"Query: \"{test['query']}\"")
        print(f"Expected Target: {test['expected_dept']}")
        print("-" * 50)
        
        result = await process_support_query(query=test['query'])
        dept = result.get("department", "UNKNOWN")
        status = result.get("status", "UNKNOWN")
        reasoning = result.get("reasoning", "N/A")
        response = result.get("response", "")
        
        print(f"Result Status : {status}")
        print(f"Routed To     : {dept}")
        print(f"Reasoning     : {reasoning}")
        print(f"Response Preview:\n{response[:200]}...")
        
        # Verify routing
        if test["expected_dept"] == "AMBIGUOUS / NONE":
            is_valid = status == "AMBIGUOUS" or dept in ["NONE", "MAIN COORDINATOR"]
        elif test["expected_dept"] == "OUT_OF_SCOPE / NONE":
            is_valid = status == "OUT_OF_SCOPE" or dept in ["NONE", "MAIN COORDINATOR"]
        else:
            is_valid = dept.upper() == test["expected_dept"].upper() and status == "SUCCESS"
            
        if is_valid:
            print(">>> ✅ PASS")
            passed += 1
        else:
            print(">>> ⚠️ ROUTING MISMATCH (Check coordinator classification)")
            
    print("\n" + "=" * 80)
    print(f"TEST SUITE COMPLETE: {passed}/{total} Passed")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_test_suite())