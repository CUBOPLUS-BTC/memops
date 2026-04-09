# API and Backend Notes  
  
## Purpose  
  
This document records the intended backend assumptions of MemOps.  
  
The project is designed around **mempool-compatible backends**, with the public mempool.space instance serving as a convenient default example rather than a hard dependency.  
  
The purpose of this file is to clarify:  
  
- which kinds of endpoints are expected,  
- what role those endpoints play,  
- and why backend data should still be treated as input rather than unquestionable truth.  
  
---  
  
## 1. Backend Strategy  
  
MemOps is designed to work with a configurable backend URL.  
  
This supports two operational modes:  
  
1. **Public mode**    
   using a public mempool-compatible endpoint such as `https://mempool.space`  
  
2. **Self-hosted mode**    
   using a user-controlled or organization-controlled deployment that exposes compatible routes  
  
This matters because the project is intended to be infrastructure-friendly and sovereignty-aware.  
  
---  
  
## 2. Current Target Endpoint Categories  
  
The initial MVP is expected to rely on a small set of backend data categories.  
  
### A. Transaction summary  
  
Used to retrieve high-level transaction information by `txid`.  
  
Typical route shape:  
  
```text  
/api/tx/{txid}  
```  
  
Possible uses:  
  
- basic transaction status  
- confirmation context  
- transaction summary fields  
- linkage to other relevant data  
  
### B. Raw transaction hex  
  
Used to retrieve the transaction body for local inspection.  
  
Typical route shape:  
  
```text  
/api/tx/{txid}/hex  
```  
  
Possible uses:  
  
- local parsing  
- local size-related checks  
- sequence inspection  
- transaction-structure analysis  
  
### C. Fee recommendations  
  
Used to understand current fee market conditions.  
  
Typical route shape:  
  
```text  
/api/v1/fees/recommended  
```  
  
Possible uses:  
  
- baseline fee recommendations  
- comparison context for stuck-transaction reasoning  
  
### D. Mempool block or fee pressure data  
  
Used to better explain why a transaction is likely not confirming.  
  
Typical route shape:  
  
```text  
/api/v1/fees/mempool-blocks  
```  
  
Possible uses:  
  
- contextual fee pressure  
- better `why-stuck` reasoning  
- gap analysis between transaction position and current market  
  
---  
  
## 3. Optional or Later Data Needs  
  
Depending on the depth of the implementation, future versions of MemOps may also need additional context, such as:  
  
- prevout-related information,  
- outspend information,  
- address or script-related details,  
- or optional Bitcoin Core validation.  
  
These are not all required for the initial MVP, and should only be added when they support the core workflow clearly.  
  
---  
  
## 4. Important API Principle  
  
MemOps should not be designed as a trivial API wrapper.  
  
The backend is expected to provide data retrieval, but the project should still perform local reasoning where appropriate.  
  
That means the architecture should avoid this weak pattern:  
  
- request data,  
- print backend response,  
- and call it “analysis.”  
  
Instead, the preferred pattern is:  
  
- retrieve backend data,  
- normalize it,  
- inspect what matters locally,  
- and produce a structured explanation.  
  
---  
  
## 5. Compatibility Notes  
  
“Mempool-compatible” should be treated as a practical target, not as a blind assumption of perfect identity across every deployment.  
  
Before relying on a backend in a demo or production-like context, the maintainer should verify:  
  
- route availability,  
- response shape,  
- status field behavior,  
- and any differences between public and self-hosted environments.  
  
This is especially important for an MVP.  
  
---  
  
## 6. Failure and Fallback Notes  
  
The CLI should be designed with the possibility of backend issues in mind, such as:  
  
- temporary network failures,  
- rate limits,  
- missing routes,  
- or schema differences.  
  
Even if the first MVP keeps error handling simple, the documentation should acknowledge that backend failures are part of the real operating environment.  
  
---  
  
## 7. WebSocket Note  
  
Real-time monitoring may later benefit from WebSocket support, but that is not required for the initial MVP.  
  
If WebSocket support is introduced later, it should only be done after the schema and event structure are verified carefully.  
  
For the current stage, polling or static analysis is a safer and simpler direction.  
  
---  
  
## Conclusion  
  
The backend layer in MemOps exists to provide data access, not final judgment.  
  
The project should remain compatible with mempool-style infrastructure while preserving its core principle:  
  
**use the backend as a source of data, then reason explicitly and locally wherever it matters.**
