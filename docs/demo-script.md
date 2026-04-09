# Demo Script for MemOps  
  
## Purpose  
  
This document defines the recommended demo flow for the current executable MVP of MemOps.  
  
The goal of the demo is not to show many features. The goal is to prove one thing clearly:  
  
> **MemOps is already an executable, verification-first transaction inspection tool — not just a repository plan.**  
  
The current demo should therefore stay disciplined and aligned with what the code actually does today.  
  
---  
  
## Primary Audience Takeaway  
  
By the end of the demo, the audience should understand:  
  
- what problem MemOps is addressing,  
- why backend data should not be treated as the entire analysis layer,  
- what the current CLI can already inspect locally,  
- and why this is a credible base for later `why-stuck` and response workflows.  
  
---  
  
## What the Current MVP Demonstrates  
  
Today, MemOps can already:  
  
- accept a `txid`,  
- query a mempool-compatible backend,  
- retrieve raw transaction hex,  
- parse key transaction fields locally,  
- detect explicit opt-in RBF signaling,  
- and render the result in both human-readable and JSON form.  
  
That is enough to support a real technical walkthrough.  
  
---  
  
## Pre-Demo Checklist  
  
Before the presentation, confirm the following:  
  
- the repository is up to date,  
- dependencies are installed,  
- the selected demo transaction is documented,  
- the backend endpoint is reachable,  
- a local `.env` file is prepared if needed,  
- terminal output is readable,  
- and fallback screenshots or saved outputs exist.  
  
Useful pre-demo checks:  
  
```bash  
uv run memops --help  
uv run pytest -q  
```  
  
If a live backend will be used, also prepare a fallback explanation in case the service is slow or unavailable.  
  
---  
  
## Recommended Demo Flow  
  
## 1. Opening framing  
  
Suggested message:  
  
> “MemOps is a verification-first Bitcoin CLI. The current MVP focuses on transaction inspection: fetch the raw transaction, inspect it locally, and report what matters for later operational reasoning.”  
  
This sets honest expectations.  
  
---  
  
## 2. Show the configuration model  
  
If useful, briefly show that MemOps is backend-configurable and can read from `.env`:  
  
```bash  
cp .env.example .env  
```  
  
Example configuration:  
  
```dotenv  
MEMOPS_BACKEND_URL=https://mempool.space  
MEMOPS_NETWORK=mainnet  
```  
  
Suggested speaking line:  
  
> “The project is designed to work with mempool-compatible backends, not only one public website.”  
  
Keep this short.  
  
---  
  
## 3. Run the human-readable inspection command  
  
Use the real command that exists today:  
  
```bash  
uv run memops <txid>  
```  
  
What to highlight:  
  
- transaction identifier,  
- version,  
- input and output counts,  
- locktime,  
- segwit detection,  
- explicit RBF result,  
- and which inputs signal replacement.  
  
Suggested speaking line:  
  
> “The point is not only to fetch a transaction. It is to inspect important properties locally and present them clearly.”  
  
---  
  
## 4. Explain what is local versus external  
  
Make the trust model explicit:  
  
- the backend provides the raw transaction hex,  
- MemOps parses the transaction locally,  
- and explicit RBF signaling is derived locally from sequence values.  
  
Suggested speaking line:  
  
> “The backend is a data source. The interpretation shown here is intentionally kept on the client side.”  
  
This reinforces the project philosophy.  
  
---  
  
## 5. Run the JSON mode  
  
Show that the same inspection can be exported in a machine-friendly form:  
  
```bash  
uv run memops --json <txid>  
```  
  
What to highlight:  
  
- `raw_hex`  
- `parsed`  
- `analysis`  
  
Suggested speaking line:  
  
> “JSON output matters because incident-response workflows benefit from artifacts that can be reused, inspected, or scripted.”  
  
---  
  
## 6. Connect the current MVP to the roadmap  
  
Close the technical walkthrough by explaining what this baseline enables next:  
  
- fee-pressure comparison,  
- `why-stuck` reasoning,  
- auditable report generation,  
- and structured RBF planning.  
  
Suggested speaking line:  
  
> “This MVP already proves the inspection pipeline. The next milestone is to move from inspection to diagnosis.”  
  
---  
  
## Demo Timing Suggestion  
  
### Non-technical framing  
~1.5 to 2 minutes  
  
### Technical walkthrough  
~2 to 3 minutes  
  
This keeps the full demo compact and credible.  
  
---  
  
## Fallback Plan  
  
If the live backend fails or the environment becomes unstable, use one or more of the following:  
  
- a saved terminal capture of `uv run memops <txid>`,  
- a saved JSON output from `uv run memops --json <txid>`,  
- screenshots of expected behavior,  
- or a dry explanation of the inspection pipeline using prepared artifacts.  
  
The fallback should still prove that the project is executable and technically coherent.  
  
---  
  
## What Not to Do in the Demo  
  
Avoid these mistakes:  
  
- do not demo commands that do not exist yet,  
- do not present `why-stuck` as if it were already implemented,  
- do not turn the walkthrough into a generic explorer tour,  
- do not spend too much time on infrastructure details,  
- and do not oversell the current MVP.  
  
The strength of the current demo is honesty plus execution.  
  
---  
  
## Closing Line  
  
Recommended ending:  
  
> “MemOps already shows that transaction inspection can be more rigorous than reading an explorer page. The next step is to turn that inspection baseline into clearer operational diagnosis.”  
  
---  
  
## Final Note  
  
The best current MemOps demo is not the one with the most promises.  
  
It is the one that clearly proves:  
  
- the repository is executable,  
- the CLI performs real local inspection,  
- the outputs are reviewable,  
- and the project has a disciplined path forward.
