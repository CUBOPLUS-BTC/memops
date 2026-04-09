# Demo Script for MemOps  
  
## Purpose  
  
This document defines the recommended demo flow for the current executable baseline of MemOps.  
  
The goal of the demo is not to show many features. The goal is to prove two things clearly:  
  
> **MemOps is already an executable verification-first transaction inspection tool.**  
>  
> **MemOps also now provides an initial why-stuck diagnosis workflow.**  
  
The demo should stay disciplined and aligned with what the code actually does today.  
  
---  
  
## Primary Audience Takeaway  
  
By the end of the demo, the audience should understand:  
  
- what problem MemOps is addressing,  
- why backend data should not be treated as the entire analysis layer,  
- what the CLI can already inspect locally,  
- how the current why-stuck mode uses fee context plus local explicit-RBF reasoning,  
- and why this is a credible base for later export and response workflows.  
  
---  
  
## What the Current Baseline Demonstrates  
  
Today, MemOps can already:  
  
- accept a `txid`,  
- query a mempool-compatible backend,  
- retrieve raw transaction hex,  
- parse key transaction fields locally,  
- detect explicit opt-in RBF signaling,  
- retrieve normalized backend transaction summary data,  
- retrieve normalized backend fee recommendations,  
- classify the transaction fee position relative to current recommendation bands,  
- provide an initial why-stuck diagnosis,  
- and render the result in both human-readable and JSON form.  
- optionally export auditable diagnosis artifacts as JSON and Markdown files.  

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
  
> “MemOps is a verification-first Bitcoin CLI. The current baseline fetches a transaction, inspects key properties locally, and can now also provide an initial why-stuck diagnosis using backend fee context plus local explicit-RBF analysis.”  
  
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
- explicit RBF signaling is derived locally from sequence values,  
- transaction summary and fee recommendations come from the backend,  
- and the why-stuck conclusion is then built locally from normalized data plus local policy.  
  
Suggested speaking line:  
  
> “The backend is a data source. The interpretation shown here is intentionally kept on the client side whenever practical.”  
  
This reinforces the project philosophy.  
  
---  
  
## 5. Run the human-readable why-stuck command  
  
Use the real command that exists today:  
  
```bash  
uv run memops --why-stuck <txid>  
```  
  
What to highlight:  
  
- confirmation status,  
- fee paid,  
- virtual size,  
- fee rate,  
- current fee-band position,  
- target fee band,  
- explicit RBF result,  
- recommended action,  
- and the final summary and explanation.  
  
Suggested speaking line:  
  
> “This is not full rescue automation. It is an initial diagnosis layer that explains whether the transaction looks underpriced relative to current fee conditions and whether fee bumping is likely plausible.”  
  
That wording stays accurate.  
  
---  
  
## 6. Run the JSON mode  
  
Show that the same diagnosis can be emitted in a machine-friendly form:  
  
```bash  
uv run memops --why-stuck --json <txid>  
```  
  
What to highlight:  
  
- `raw_hex`  
- `parsed`  
- `analysis`  
- `summary`  
- `fee_context`  
- `diagnosis`  
  
Suggested speaking line:  
  
> “JSON output matters because incident-response workflows benefit from artifacts that can be reused, inspected, or scripted.”  
  
---
  
## 7. Run the export mode  
  
Use the real commands that now exist:  
  
```bash  
uv run memops --why-stuck --export <txid>  
uv run memops --why-stuck --json --export <txid>  
```  
  
What to highlight:  
  
- deterministic export directory layout,  
- `analysis.json` and `report.md`,  
- text-mode confirmation of written paths,  
- and the `artifacts` object in JSON output.  
  
Suggested speaking line:  
  
> “This matters because incident-response work should leave behind auditable artifacts, not only terminal output.”  

---  
  
## 8. Connect the current baseline to the roadmap 
  
Close the technical walkthrough by explaining what this baseline enables next:  
  
- richer fee-pressure context,  
- structured RBF planning,  
- and later response workflows.  
  
Suggested speaking line:  
  
> “The project now proves both inspection and initial diagnosis. The next step is to make those results easier to export, review, and act on.”  
  
---  
  
## Demo Timing Suggestion  
  
### Non-technical framing  
~1.5 to 2 minutes  
  
### Technical walkthrough  
~2.5 to 3.5 minutes  
  
This keeps the full demo compact and credible.  
  
---  
  
## Fallback Plan  
  
If the live backend fails or the environment becomes unstable, use one or more of the following:  
  
- a saved terminal capture of `uv run memops <txid>`,  
- a saved terminal capture of `uv run memops --why-stuck <txid>`,  
- a saved JSON output from `uv run memops --why-stuck --json <txid>`,  
- screenshots of expected behavior,  
- or a dry explanation of the workflow using prepared artifacts.  
- a saved export directory containing `analysis.json` and `report.md`,  

The fallback should still prove that the project is executable and technically coherent.  
  
---  
  
## What Not to Do in the Demo  
  
Avoid these mistakes:  
  
- do not demo commands that do not exist,  
- do not present `--why-stuck` as a full incident-response suite,  
- do not claim CPFP planning is implemented,  
- do not present export artifacts as full rescue automation,    
- do not turn the walkthrough into a generic explorer tour,  
- and do not oversell the current baseline.  
  
The strength of the demo is honesty plus execution.  
  
---  
  
## Closing Line  
  
Recommended ending:  
  
> “MemOps already shows that transaction inspection and initial diagnosis can be more rigorous than reading an explorer page. The next step is to turn this baseline into richer, more auditable operational tooling.”  
  
---  
  
## Final Note  
  
The best current MemOps demo is not the one with the most promises.  
  
It is the one that clearly proves:  
  
- the repository is executable,  
- the CLI performs real local inspection,  
- the why-stuck mode produces structured diagnosis,  
- the outputs are reviewable,  
- and the project has a disciplined path forward.
