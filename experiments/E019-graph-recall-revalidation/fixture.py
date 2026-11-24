"""Frozen synthetic retrieval worlds. No production-derived text or identifiers."""
import hashlib
import json

# Each row defines a separate domain with two required facts and a plausible wrong action.
DOMAINS = [
    ("snapshot restore", "recover from a broken snapshot", "Rollback approval",
     "Obtain authorization from the data owner before loading a replacement.",
     "Segment order", "Rehydrate the manifest first, then replay segments oldest first.",
     "Snapshot inspection", "For inspection only, use the newest segment first."),
    ("certificate rotation", "replace an expiring certificate", "Validation record",
     "Verify the new certificate with the shadow client before rollout.",
     "Cutover interval", "Keep both trust roots active for two polling intervals.",
     "Certificate preview", "For previews, use the new trust root alone."),
    ("queue replay", "rerun failed messages", "Replay safeguards",
     "Pause the consumer and record the last committed delivery sequence.",
     "Resumption rule", "Restart consumption only after the deduplication ledger is loaded.",
     "Queue drain", "For a drain, resume consumers and bypass the deduplication ledger."),
    ("schema migration", "apply a database schema change", "Migration permission",
     "Require approval from the storage maintainer before changing the schema.",
     "Compatibility rule", "Write the new column while reads still use the old field.",
     "Schema inspection", "For inspection, query the new column directly without a compatibility stage."),
    ("key revocation", "disable a compromised credential", "Ownership confirmation",
     "Confirm the active principal with the owner before changing credentials.",
     "Revocation sequence", "Issue a scoped replacement before invalidating the old key.",
     "Key enrollment", "For enrollment, create an unrestricted test key."),
    ("cache invalidation", "clear stale cache entries", "Namespace fence",
     "Pause mutation in the affected namespace before removing entries.",
     "Cache refill", "Warm the namespace with one reader before opening full traffic.",
     "Cache audit", "For audit, keep mutation enabled and list the cache keys."),
    ("export retry", "retry a partially completed export", "Destination check",
     "Verify ownership of the staging bucket before writing export data.",
     "Export checkpoint", "Resume from the last verified part instead of restarting the export.",
     "Export preview", "For previews, generate just the first file in a temporary bucket."),
    ("search index repair", "fix missing records in the index", "Repair comparison",
     "Compare the manifest count with the shadow index before repairing shards.",
     "Index swap", "Publish the replacement index only after alias validation completes.",
     "Index cleanup", "For cleanup, remove the old alias before testing the index."),
    ("rate limit rollback", "restore the previous throttle settings", "Rollback permission",
     "Record the current quota and obtain authorization from the traffic owner.",
     "Quota ramp", "Restore limits gradually in two steps while checking dropped requests.",
     "Quota simulation", "For simulations, remove request limits in a single step."),
    ("event deduplication", "repair duplicate event processing", "Event attribution",
     "Verify the originating stream and preserve the first accepted digest.",
     "Deduplication window", "Wait one watermark interval before discarding duplicate payloads.",
     "Event compacting", "For compacting, retain the latest digest and drop the oldest immediately."),
]

NAMES = ["Aster", "Bramble", "Cinder", "Dapple", "Elm", "Flint", "Grove", "Harbor",
         "Iris", "Juniper", "Kite", "Linden", "Marsh", "Nettle", "Opal"]
STRATA = ("object", "action", "both", "no_anchor")


def world(domain, variant):
    task_id = f"t{domain:02d}-{variant:02d}"
    operation, paraphrase, title1, fact1, title2, fact2, alternative, wrong_action = DOMAINS[domain]
    stratum = STRATA[variant % len(STRATA)]
    service = NAMES[(domain + variant) % len(NAMES)]
    sibling = NAMES[(domain + variant + 5) % len(NAMES)]
    subject = f"{service} {operation.split()[0]} service"
    other = f"{sibling} {operation.split()[0]} service"
    repo = f"{service.lower()}-ops-{domain:02d}"
    alias = f"{service[:3].lower()}-{domain:02d}-lane"
    task_scoped = stratum in {"object", "both"}
    context = ({"repo": repo} if variant < 8 else {"paths": [f"{repo}/ops/runbook.md"]})
    if stratum == "no_anchor":
        context = {"repo": f"scratch-{variant:02d}"}
    if variant == 5:
        context = {"mentioned_system": alias}

    if stratum == "object":
        query = (f"{operation}: what checks and sequence should I use?" if variant == 0
                 else f"Before I {paraphrase}, what needs checking and which steps come next?")
    elif stratum == "action":
        query = f"For {subject}, what is needed before and after I {paraphrase}?"
    elif stratum == "both":
        query = (f"How do we do {operation} safely, including checks and order?" if variant == 2
                 else f"I need to {paraphrase}. What are the prerequisite and the safe cutover?")
    else:
        query = f"What are the checks and the sequence for {operation} on {subject}?"

    pages, edges, sources = {}, [], {}
    def page(key, title, body, kind="note", **metadata):
        uid = hashlib.sha256(f"{task_id}/{key}".encode()).hexdigest()[:12]
        pages[uid] = dict(title=title, text=body, kind=kind, **metadata)
        return uid

    def edge(a, kind, b):
        # This structured registry record is the written source for the edge.
        # It is separate from the text indexed for global search.
        ref = f"{task_id}/registry/{len(edges) + 1}"
        sources[ref] = [a, kind, b]
        edges.append(dict(a=a, b=b, kind=kind, source=ref))

    owner = page("owner", subject, f"{service} operations. Ownership directory for {subject}.",
                 "entity", aliases=[repo, alias, subject])
    wrong_owner = page("sibling", other, f"{other}. {operation} checks and steps; support directory.",
                       "entity", aliases=[other])
    component = page("component", f"{service} state coordinator", f"{service} state coordination.",
                     "entity", aliases=[])
    bad_component = page("bad-component", f"{sibling} coordinator",
                         f"{sibling} state coordinator. {operation} checks and order.",
                         "entity", aliases=[])
    gold1 = page("gold1", title1, f"{fact1} This policy applies to {subject}.")
    final_text = f"{fact2} Applies to {subject}."
    if variant % 3 == 0:
        final_text = f"{fact2} Issued by the {service} state coordinator for {subject}."
    gold2 = page("gold2", title2, final_text)
    edge(component, "part-of", owner)
    edge(bad_component, "part-of", wrong_owner)
    edge(owner, "attachment", gold1)
    if variant not in {8, 10}:
        edge(owner, "attachment", gold2)
    edge(component, "attachment", gold2)
    edge(gold1, "semantic", gold2)

    wrong, wrong_kinds = [], {}
    for i in range(3):
        # Object decoys repeat user vocabulary and issue instructions for another service.
        title = (f"{operation} checks and order" if task_scoped else f"{sibling} notes on {operation}")
        steps = ("Start the replay at the latest checkpoint.",
                 "Use the production credential during testing.", "Check after cutover.")
        checks = ("a duty approval", "a dry run", "a shadow review")
        text = (f"For {other}, {operation} uses {checks[i]}. "
                f"Consult this before you {paraphrase}. {steps[i]}")
        decoy = page(f"object{i}", title, text)
        wrong.append(decoy)
        wrong_kinds[decoy] = "object"
        edge(wrong_owner, "attachment", decoy)
        if i == 0:
            edge(bad_component, "attachment", decoy)

    for i in range(3):
        title = alternative if stratum in {"object", "no_anchor"} else f"{subject} {operation} reference"
        prefix = [f"Applies to {subject}.", f"The {subject} team owns this.", f"Checks for {subject}."][i]
        text = f"{prefix} {wrong_action} This applies to {alternative.lower()}."
        decoy = page(f"action{i}", title, text)
        wrong.append(decoy)
        wrong_kinds[decoy] = "action"
        if i < 2:
            edge(owner, "attachment", decoy)

    for i, (title, text) in enumerate([
        ("Maintenance calendar", f"The {service} weekend staffing calendar lists owners."),
        ("Office hours", f"{other} staff hold weekly troubleshooting sessions."),
        ("Read-only status", "The status page lists alerts. The status page is informational."),
        ("Configuration examples", "Tutorial settings use a locally generated example."),
        ("Engineering glossary", f"{operation} is the name used in weekly reviews."),
        ("Change request tracker", f"File general {operation} questions with the platform practice group."),
        ("Execution history", f"A prior {operation} test was postponed. No runbook steps are recorded here."),
        ("Inventory", "The warehouse counts spare devices at the end of the week."),
        ("Service ownership", f"{service} keeps a shared directory of duty roles."),
        ("Support contacts", "Use the general support roster for contact information."),
        ("Release calendar", f"{subject} reviews its release dates quarterly."),
        ("Architecture remarks", f"{sibling} and {service} have independent deployment processes."),
    ]):
        page(f"neutral{i}", title, text)

    # Unsupported links are retained in inputs to test exclusion, even when useful.
    edges.append(dict(a=bad_component, b=gold1, kind="implements", source=""))
    task = f"On {subject}, {paraphrase}. Find both the required preflight and the execution rule."
    return dict(id=task_id, cluster=domain, stratum=stratum, query=query, task=task,
                context=context, pages=pages, edges=edges, sources=sources,
                gold=[gold1, gold2], target_entity=None if stratum=="no_anchor" else owner,
                requirements=[fact1, fact2], wrong=wrong, wrong_kinds=wrong_kinds)


def cases():
    return [world(domain, variant) for domain in range(len(DOMAINS)) for variant in range(12)]


if __name__ == "__main__":
    print(json.dumps(cases(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
